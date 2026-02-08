# PhishGuard - Email Phishing Detection

PhishGuard is a training-focused phishing detection game. It serves realistic messages, scores your decisions, and captures feedback to improve the experience. There is also an AI Challenge mode that can generate fresh phishing/legitimate samples using Groq.

## Why This Exists

Most phishing training is passive. PhishGuard makes it hands-on, time-boxed, and measurable so people build real instincts quickly.

## Features

- **Interactive classification** with a 10-second timer per message.
- **Score + attempts tracking** to measure progress.
- **AI Challenge mode** to generate new samples on demand.
- **Feedback capture** stored locally as JSON.
- **Safety checks** on payload size and input validation.

## Project Structure

```
phishguard/
├── app.py
├── phishing_data.json
├── requirements.txt
├── requirements-dev.txt
├── requirements-ai.txt
├── templates/
│   └── index.html
├── static/
│   ├── script.js
│   └── style.css
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        └── python-ci.yml
```

## Quick Start

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run the app

```bash
python app.py
```

Open the browser at:

```
http://127.0.0.1:5000/
```

## AI Challenge Setup (Optional)

Install Groq SDK:

```bash
pip install -r requirements-ai.txt
```

Set your API key:

```bash
$env:GROQ_API_KEY="your-key"  # PowerShell
```

AI Challenge is triggered from the UI and saves new samples into phishing_data.json.

## API Endpoints

- `GET /` - Serve the UI
- `GET /get-email` - Fetch a random message
- `GET /get-email?source=ai` - Generate and store an AI message
- `POST /submit-feedback` - Store feedback as JSON
- `GET /health` - Basic health check

## Configuration

Environment variables (all optional):

- `PHISHGUARD_DATA_PATH` - Path to phishing_data.json
- `PHISHGUARD_FEEDBACK_DIR` - Folder for feedback JSON
- `PHISHGUARD_MAX_FEEDBACK` - Max feedback length (default 1000)
- `PHISHGUARD_MAX_EMAIL` - Max AI email length (default 600)
- `PHISHGUARD_MAX_DATASET` - Max stored emails (default 2000)
- `PHISHGUARD_MIN_AI_INTERVAL` - Min seconds between AI requests per IP (default 1.5)
- `PHISHGUARD_MIN_FEEDBACK_INTERVAL` - Min seconds between feedback submissions per IP (default 2.0)
- `PHISHGUARD_HOST` - Bind host (default 127.0.0.1)
- `PHISHGUARD_PORT` - Bind port (default 5000)
- `FLASK_DEBUG` - Set to 1 for debug mode

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

## Dataset Notes

phishing_data.json is a simple list of objects:

```json
{
  "text": "Your account needs verification...",
  "label": "phishing"
}
```

## Feedback Storage

Feedback is stored locally in the folder defined by `PHISHGUARD_FEEDBACK_DIR` (defaults to FeedBack/). Each file is timestamped and contains the feedback text plus a creation time.

## Security Considerations

- API keys are never stored in the repo.
- Input length is bounded to reduce abuse.
- AI output is validated before storage.

## Contributing

Issues and pull requests are welcome. If you add new scenarios or UI ideas, please include a short explanation of the learning goal.

## License

MIT License.