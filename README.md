# Fake Profile Detector

A full stack web project that collects the details of a social media profile, estimates whether
the profile is **real, suspicious or fake**, explains why, and gives **safety tips**.

**Stack:** Python 3 · Flask (backend) · SQLite (database) · HTML, CSS, JavaScript (frontend)

## How to run

1. Install Python 3.9 or newer.
2. Open a terminal in this folder and install Flask:
   ```
   pip install -r requirements.txt
   ```
3. Start the app:
   ```
   python app.py
   ```
4. Open **http://127.0.0.1:5000** in your browser.

## Run the tests

```
python -m unittest discover -s tests -v
```

## Folder structure

```
fake-profile-detector/
├── app.py              Flask server: pages, form validation, JSON API
├── detector.py         The scoring rules (risk points, verdict, reasons)
├── database.py         SQLite functions (save, list, delete history)
├── tips.py             All safety tips text
├── requirements.txt    Python libraries
├── templates/          HTML pages: index, result, history, tips, about
├── static/css, js/     Styling and small form helpers
├── instance/           SQLite database file profiles.db (created while running)
├── tests/              Unit tests
└── docs/PROJECT_REPORT.md   Abstract, modules, algorithm, test cases (for your submission)
```

## Features

- Form with validation: platform, username, display name, bio, followers, following, posts, account age, mutual connections, average likes
- Scam behaviour checkboxes: asked for money/OTP, pushed to act fast, strange link, claims to be a celebrity
- Risk score 0-100 with a list of reasons (+ points for warning signs, - points for good signs)
- Verdict: Likely real / Suspicious / Likely fake
- Safety tips matched to the warnings, plus a full Safety tips page
- History page with delete, and a "How it works" page for your viva
- JSON API: `POST /api/analyze`

```
curl -X POST http://127.0.0.1:5000/api/analyze -H "Content-Type: application/json" ^
  -d "{\"username\":\"bot99999999\",\"followers\":5,\"following\":3000,\"posts\":0,\"age_months\":0}"
```

## Important notes

- This is a **screening tool**: a risk estimate from rules, not proof. Say this in your viva.
- The profile details are typed by the user. Nothing is scraped from social media and nothing leaves your computer.
- Change the `SECRET_KEY` environment variable if you ever host it online.

## Future scope

- Train a machine learning model (Logistic Regression / Random Forest) on a public fake-profile dataset and compare it with the rule-based score
- Add user login, a browser extension and reverse image search
