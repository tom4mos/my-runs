import json
import os
import time
from datetime import datetime, timezone
from garminconnect import Garmin


def format_duration(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_pace(meters, seconds):
    if not meters or meters == 0:
        return "—"
    pace_secs_per_km = seconds / (meters / 1000)
    mins = int(pace_secs_per_km // 60)
    secs = int(pace_secs_per_km % 60)
    return f"{mins}:{secs:02d} /km"


def fetch_personal_bests(client, act_lookup):
    pbs = {}
    try:
        records = client.get_personal_record()
        print("DEBUG personal_record raw:", json.dumps(records, default=str, indent=2))

        # typeId sequence: 2=1mi, 3=5K, 4=10K, 5=half, 6=marathon, 7=longest run
        type_map = {3: "5k", 4: "10k", 7: "longest_run"}
        distances = {3: 5000, 4: 10000}

        for rec in records or []:
            type_id = rec.get("typeId")
            value = float(rec.get("value") or 0)
            act_id = rec.get("activityId")
            raw_time = rec.get("prStartTimeLocal") or rec.get("prStartTimeGmt")
            if isinstance(raw_time, (int, float)):
                ts = raw_time / 1000 if raw_time > 1e12 else raw_time
                date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            elif isinstance(raw_time, str):
                date_str = raw_time[:10]
            else:
                date_str = ""

            if type_id == 3 or type_id == 4:
                dist_m = distances[type_id]
                pbs[type_map[type_id]] = {
                    "time": format_duration(value),
                    "pace": format_pace(dist_m, value),
                    "date": date_str,
                }
            elif type_id == 7:
                dist_m = value
                act = act_lookup.get(act_id, {})
                dur_s = float(act.get("duration") or 0)
                pbs["longest_run"] = {
                    "distance_km": round(dist_m / 1000, 2),
                    "time": format_duration(dur_s) if dur_s else None,
                    "pace": format_pace(dist_m, dur_s) if dur_s else None,
                    "date": date_str,
                }
    except Exception as e:
        print(f"Could not fetch personal records: {e}")
    return pbs


def main():
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]

    client = Garmin(email, password)
    client.login()

    activities = client.get_activities(0, 50)

    act_lookup = {a.get("activityId"): a for a in activities if a.get("activityId")}
    personal_bests = fetch_personal_bests(client, act_lookup)

    running_types = {"running", "trail_running", "treadmill_running", "track_running"}

    runs = []
    for activity in activities:
        type_key = activity.get("activityType", {}).get("typeKey", "")
        if type_key not in running_types:
            continue

        distance_m = activity.get("distance") or 0
        duration_s = activity.get("duration") or 0
        avg_hr = activity.get("averageHR")

        activity_id = activity.get("activityId")
        run = {
            "date": (activity.get("startTimeLocal") or "")[:10],
            "name": activity.get("activityName") or "Run",
            "distance_km": round(distance_m / 1000, 2),
            "duration": format_duration(duration_s),
            "pace": format_pace(distance_m, duration_s),
            "avg_hr": int(avg_hr) if avg_hr else None,
            "elevation_gain": round(activity.get("elevationGain") or 0),
            "elevation_loss": round(activity.get("elevationLoss") or 0),
        }

        try:
            details = client.get_activity_details(activity_id, maxchart=2000)
            descriptors = details.get("metricDescriptors", [])
            elev_index = next(
                (d["metricsIndex"] for d in descriptors if d.get("key") == "directElevation"),
                None,
            )
            if elev_index is not None:
                samples = details.get("activityDetailMetrics", [])
                raw = [
                    s["metrics"][elev_index]
                    for s in samples
                    if s.get("metrics") and s["metrics"][elev_index] is not None
                ]
                step = max(1, len(raw) // 50)
                run["elevation_profile"] = [round(raw[i], 1) for i in range(0, len(raw), step)][:50]
            else:
                run["elevation_profile"] = None
        except Exception:
            run["elevation_profile"] = None

        time.sleep(0.3)
        runs.append(run)

        if len(runs) >= 30:
            break

    os.makedirs("docs", exist_ok=True)
    payload = {
        "runs": runs,
        "personal_bests": personal_bests,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Saved {len(runs)} runs to docs/data.json")


if __name__ == "__main__":
    main()
