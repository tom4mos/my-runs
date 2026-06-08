# RunDataPage

A lightweight static website that pulls Garmin Connect run data and displays it at a public GitHub Pages URL.

## What this project does

- `fetch_runs.py` logs into Garmin Connect and saves up to 30 recent runs to `docs/data.json`
- `docs/index.html` reads that JSON and displays run cards (distance, pace, duration, heart rate)
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

## Design

- Font: Inter (Google Fonts), falling back to Helvetica Neue / Helvetica
- Colour scheme: white and grey, near-black (#111) header and accents
- Mobile-first, minimal layout
- Runs are grouped by month under a subtle uppercase month header
- Each run is displayed as a row: a small desk-calendar widget on the left (dark strip with abbreviated day name, large day number below) beside a full-width card showing the run name and stats pills
