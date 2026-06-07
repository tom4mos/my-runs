import json
import os
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


def main():
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]

    client = Garmin(email, password)
    client.login()

    activities = client.get_activities(0, 50)

    running_types = {"running", "trail_running", "treadmill_running", "track_running"}

    runs = []
    for activity in activities:
        type_key = activity.get("activityType", {}).get("typeKey", "")
        if type_key not in running_types:
            continue

        distance_m = activity.get("distance") or 0
        duration_s = activity.get("duration") or 0
        avg_hr = activity.get("averageHR")

        runs.append({
            "date": (activity.get("startTimeLocal") or "")[:10],
            "name": activity.get("activityName") or "Run",
            "distance_km": round(distance_m / 1000, 2),
            "duration": format_duration(duration_s),
            "pace": format_pace(distance_m, duration_s),
            "avg_hr": int(avg_hr) if avg_hr else None,
        })

        if len(runs) >= 30:
            break

    os.makedirs("docs", exist_ok=True)
    payload = {
        "runs": runs,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Saved {len(runs)} runs to docs/data.json")


if __name__ == "__main__":
    main()
