# RunDataPage

A lightweight static website that pulls Garmin Connect run data and displays it at a public GitHub Pages URL.

## What this project does

- `fetch_runs.py` logs into Garmin Connect and saves up to 60 recent runs plus personal bests to `docs/data.json`
- `docs/index.html` reads that JSON and displays personal bests, summary stats, and run cards
- A GitHub Action (`.github/workflows/update_runs.yml`) runs the script every day at 11:00 UTC and commits the updated data
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

The script makes two Garmin API calls:
1. `get_activities(0, 100)` — bulk summary; provides distance, duration, pace, avg HR, elevation gain/loss for up to 100 activities (filtered to 60 runs)
2. `get_personal_record()` — returns all-time personal records; the script extracts 5K (typeId 3), 10K (typeId 4), and Longest Run (typeId 7)

Known typeId sequence: 2=1 mile, 3=5K, 4=10K, 5=half marathon, 6=marathon, 7=longest run. For time-based records (5K, 10K) the value is in seconds; for Longest Run it is in metres.

### data.json shape

```json
{
  "runs": [
    {
      "date": "YYYY-MM-DD",
      "name": "Morning Run",
      "distance_km": 5.2,
      "duration": "32:15",
      "pace": "6:12 /km",
      "avg_hr": 145,
      "elevation_gain": 45,
      "elevation_loss": 43
    }
  ],
  "personal_bests": {
    "5k":          { "time": "27:30", "pace": "5:30 /km", "date": "YYYY-MM-DD" },
    "10k":         { "time": "57:00", "pace": "5:42 /km", "date": "YYYY-MM-DD" },
    "longest_run": { "distance_km": 15.2, "time": "1:32:00", "pace": "6:03 /km", "date": "YYYY-MM-DD" }
  },
  "updated": "YYYY-MM-DDTHH:MM:SSZ"
}
```

## Design

- Font: Inter (Google Fonts), falling back to Helvetica Neue / Helvetica
- Colour scheme: white and grey, near-black (#111) header and accents; all colours are CSS variables in `:root`
- Mobile-first, minimal layout
- All times displayed in 24-hour format
- Page sections from top to bottom:
  1. **Header** — title, Daily/Monthly view toggle, and "Updated DD Mon YYYY at HH:MM" timestamp (local timezone, 24h)
  2. **Personal Bests** — cards for 5K, 10K, and Longest Run (hidden if no data)
  3. **Last 60 Runs** — total km and total time summary cards
  4. **Run list** — switchable between two views (controlled by the header toggle):
     - **Daily view** — runs grouped by month under an uppercase month header; each run is a row with a desk-calendar widget on the left and a card showing the run name, then two rows of stat pills — row 1: distance, duration, pace, heart rate; row 2: elevation gain (↑) and elevation loss (↓)
     - **Monthly view** — weeks grouped by calendar month under an uppercase month header; each week is a row of 7 day cards (Mon–Sun); days with a run show a solid green pill indicator, rest days are faded; weeks that cross a month boundary are split across both months with invisible placeholder cells holding the grid positions for out-of-month days
  5. **Footer** — three lines: data source, daily schedule time in UTC and local equivalent, live local clock (ticks every second, 24h)
  6. **Sync button** — below the footer; triggers the `update_runs.yml` workflow via the GitHub API

## Manual sync button

The "↻ Sync now" button below the footer calls the GitHub Actions `workflow_dispatch` API to trigger `update_runs.yml` on demand.

- Requires a GitHub Personal Access Token (PAT) with **Actions: write** permission scoped to this repo
- The PAT is stored in the browser's `localStorage` under the key `gh_sync_pat` — it is never in the source code
- First click with no stored token shows an inline form to enter and save the PAT
- A "Forget saved token" link appears when a token is stored
- API target: `POST https://api.github.com/repos/tom4mos/my-runs/actions/workflows/update_runs.yml/dispatches`
