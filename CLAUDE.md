# RunDataPage

A lightweight static website that pulls Garmin Connect run data and displays it at a public GitHub Pages URL.

## What this project does

- `fetch_runs.py` logs into Garmin Connect and saves up to 30 recent runs to `docs/data.json`
- `docs/index.html` reads that JSON and displays run cards (distance, pace, duration, heart rate, elevation)
- A GitHub Action (`.github/workflows/update_runs.yml`) runs the script every day at 09:35 UTC and commits the updated data
- The site is hosted on GitHub Pages serving from the `docs/` folder

## Garmin credentials

Stored as GitHub repository secrets: `GARMIN_EMAIL` and `GARMIN_PASSWORD`. Never commit these to the repo.

## Deploying changes

After editing any file locally, push to GitHub to deploy:

```
git add .
git commit -m "describe what changed"
git push
```

GitHub Pages updates within about a minute.

## Data pipeline — fetch_runs.py

For each activity the script makes two Garmin API calls:
1. `get_activities(0, 50)` — bulk summary; provides distance, duration, pace, avg HR, elevation gain/loss
2. `get_activity_details(activity_id)` — per-activity detail; provides the elevation time-series (downsampled to ~50 points and stored as `elevation_profile`)

A 0.3 s sleep between detail calls avoids Garmin rate-limiting. Treadmill runs or activities where the detail call fails will have `elevation_profile: null`.

### data.json shape per run

```json
{
  "date": "YYYY-MM-DD",
  "name": "Morning Run",
  "distance_km": 5.2,
  "duration": "32:15",
  "pace": "6:12 /km",
  "avg_hr": 145,
  "elevation_gain": 45,
  "elevation_loss": 43,
  "elevation_profile": [120.0, 122.5, ...]
}
```

## Design

- Font: Inter (Google Fonts), falling back to Helvetica Neue / Helvetica
- Colour scheme: white and grey, near-black (#111) header and accents; all colours are CSS variables in `:root`
- Mobile-first, minimal layout
- Summary bar at the top shows: runs shown · total km · total time
- Runs are grouped by month under a subtle uppercase month header
- Each run is displayed as a row: a small desk-calendar widget on the left (dark strip with abbreviated day name, large day number below) beside a full-width card showing the run name and stats pills
- Cards with elevation data show a chevron (▾) button; clicking it expands an inline SVG area chart of the elevation profile plus ↑/↓ metre totals
