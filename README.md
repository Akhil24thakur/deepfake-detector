# DeepFake Detector

AI-powered image authenticity detection system built with Flask and vanilla HTML/CSS/JS.

**Live:** [deepfake-detector-yoxi.onrender.com](https://deepfake-detector-yoxi.onrender.com)

## Features

- Upload images for AI-generated content detection
- CNN-based analysis with confidence scoring
- Dark/Light theme support
- Mobile-responsive design
- Scan history tracking
- Daily scan limits (4 free / 20 premium)

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python 3.12.7, Flask 3.0.0          |
| Frontend | Vanilla HTML5, CSS3, JavaScript     |
| Database | SQLite (Render)                     |
| Deploy   | Render                              |

## Project Structure

```
deepfake-detector/
├── .gitignore
├── .env.example
├── Procfile
├── runtime.txt
├── render.yaml
├── gunicorn_config.py
├── requirements.txt
├── README.md
├── wsgi.py
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask entry point
│   ├── config.py           # Environment variable config
│   ├── models/
│   │   ├── detector.py     # Image analysis logic
│   │   └── database.py     # SQLite database layer
│   ├── routes/
│   │   ├── auth.py         # Authentication routes
│   │   └── scans.py        # Scan history routes
│   └── utils/
│       └── image_utils.py  # Image validation
└── frontend/
    ├── css/
    │   ├── main.css        # Main styles + dark/light themes
    │   ├── result.css      # Result page styles
    │   ├── hamburger.css   # Side menu styles
    │   └── mobile.css      # Mobile responsive overrides
    ├── js/
    │   ├── api.js          # API helper functions
    │   ├── result.js       # Result page logic
    │   └── hamburger.js    # Mobile menu + theme toggle
    └── pages/
        ├── index.html      # Home / upload page
        ├── signin.html     # Sign in / Sign up
        ├── signup.html     # Redirects to signin
        ├── result.html     # Analysis result dashboard
        └── history.html    # Scan history page
```

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Akhil24thakur/deepfake-detector.git
cd deepfake-detector
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
cd backend
python app.py
```

The app will be available at `http://127.0.0.1:5000`

## Environment Variables

| Variable    | Description              | Default             |
|-------------|--------------------------|---------------------|
| SECRET_KEY  | Flask secret key         | (generated)         |
| FLASK_DEBUG | Enable debug mode        | false               |

## Deployment (Render)

1. Connect GitHub repo `Akhil24thakur/deepfake-detector`
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn -c gunicorn_config.py wsgi:app`
4. Add env var: `PYTHON_VERSION` = `3.12.7`
5. Add env var: `SECRET_KEY` = any random string

## License

MIT
