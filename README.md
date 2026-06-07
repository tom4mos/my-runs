# My Runs — Setup Guide

A simple website that automatically pulls your Garmin running data and displays it at a public URL.

---

## How it works

1. A **GitHub Action** runs every morning, logs into Garmin Connect, and saves your recent runs to `docs/data.json`.
2. **GitHub Pages** serves `docs/index.html` as a public website that reads that file.

---

## One-time setup (about 15 minutes)

### Step 1 — Push this project to GitHub

1. Go to [github.com](https://github.com) and click **New repository**.
2. Name it `my-runs` (or anything you like). Keep it **Public**. Do **not** tick "Add a README".
3. Click **Create repository**.
4. GitHub will show you a page with commands. Open a terminal in this folder and run:

```
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/my-runs.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

---

### Step 2 — Add your Garmin credentials as secrets

Your Garmin email and password are stored as **encrypted secrets** — they are never visible in your code.

1. On GitHub, open your repository and go to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret** and add:
   - Name: `GARMIN_EMAIL` — Value: your Garmin Connect email address
   - Name: `GARMIN_PASSWORD` — Value: your Garmin Connect password
3. Click **Add secret** for each one.

> **Note:** If you have two-factor authentication (2FA) enabled on your Garmin account, you will need to temporarily disable it under your Garmin Connect account settings for the automated login to work.

---

### Step 3 — Enable GitHub Pages

1. In your repository go to **Settings → Pages**.
2. Under **Source**, choose **Deploy from a branch**.
3. Set the branch to `main` and the folder to `/docs`.
4. Click **Save**.

After about a minute, GitHub will show you your site URL — something like `https://your-username.github.io/my-runs`.

---

### Step 4 — Run the Action for the first time

The Action normally runs at 6 AM UTC every day. To get your data straight away:

1. Go to the **Actions** tab in your repository.
2. Click **Update run data** on the left.
3. Click **Run workflow → Run workflow**.

Wait about 30 seconds, then visit your GitHub Pages URL to see your runs.

---

## Sharing with friends

Just send them your GitHub Pages URL — for example `https://your-username.github.io/my-runs`. Anyone with the link can view it.

---

## Updating the data manually

Any time you want to force a refresh (e.g. straight after a run), go to **Actions → Update run data → Run workflow**.

---

## Files explained

| File | Purpose |
|---|---|
| `fetch_runs.py` | Logs into Garmin and saves your runs to `docs/data.json` |
| `requirements.txt` | Python packages needed by the script |
| `.github/workflows/update_runs.yml` | Runs the script automatically every day |
| `docs/index.html` | The webpage your friends see |
| `docs/data.json` | Your run data (updated by the Action) |
