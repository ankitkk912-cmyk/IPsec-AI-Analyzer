# IPsec AI Analyzer

A hackathon-ready defensive network-security dashboard built with:

- Flask + Python backend
- HTML/CSS/JavaScript frontend
- SQLite database
- Rule-based IPsec security analyzer
- PDF report generation
- Optional AI explanation through the OpenAI Responses API

## 1. Open the project

Open the `IPsec-AI-Analyzer` folder in VS Code.

## 2. Create a virtual environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

## 3. Install packages

```bash
pip install -r requirements.txt
```

## 4. Start the backend

```bash
cd backend
python3 app.py
```

You should see Flask running on:

`http://127.0.0.1:5000`

## 5. Open Chrome

Open exactly:

`http://127.0.0.1:5000`

Do NOT use VS Code "Go Live". The Flask server serves both the dashboard and API.

## 6. Test

Upload the included `sample.conf`.

You should get:

- security score
- risk level
- checks
- warnings/failures
- recommendations
- SQLite history
- PDF report

## API endpoints

### Health
`GET /api/health`

### Analyze
`POST /api/analyze`

Form-data field:
`config=<file>`

Example curl:

```bash
curl -X POST -F "config=@sample.conf" http://127.0.0.1:5000/api/analyze
```

### History
`GET /api/history`

### Single analysis
`GET /api/analysis/<id>`

### PDF report
`GET /api/report/<id>`

### Optional AI explanation
`POST /api/ai-explain/<id>`

## Optional AI API

Copy `.env.example` to `.env` and add your API key.

The local analyzer remains functional without an API key. The AI layer is only used to turn the computed findings into a concise natural-language explanation.

Never put an API key inside HTML or JavaScript. Keep it in `.env` on the backend.

## Database

SQLite is automatically created as:

`backend/ipsec_analyzer.db`

The `analyses` table stores the filename, score, risk, summary, JSON result and timestamp.

## Architecture

Browser → Flask REST API → Analyzer → SQLite → PDF/AI services → Browser

This is a defensive configuration-analysis project. It does not attempt to attack or exploit VPN devices.
