# DeepFake Detector

AI-powered image authenticity detection system built with Flask and vanilla HTML/CSS/JS.

## Features

- Upload images for AI-generated content detection
- CNN-based analysis with confidence scoring
- Dark/Light theme support
- Mobile-responsive design
- Scan history tracking (requires MySQL)
- Daily scan limits (4 free / 20 premium)

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python 3.11.9, Flask 3.0.0          |
| Frontend | Vanilla HTML5, CSS3, JavaScript     |
| Database | MySQL (optional)                    |
| Deploy   | Heroku / Render                     |

## Project Structure

```
deepfake-detector/
├── .gitignore
├── .env.example
├── Procfile
├── runtime.txt
├── requirements.txt
├── README.md
├── backend/
│   ├── app.py              # Flask entry point
│   ├── config.py           # Environment variable config
│   ├── models/
│   │   ├── detector.py     # Image analysis logic
│   │   └── database.py     # MySQL connection
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
git clone https://github.com/YOUR_USERNAME/deepfake-detector.git
cd deepfake-detector
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 3. Install dependencies

```bash
cd backend
pip install -r ../requirements.txt
```

### 4. Run the application

```bash
cd backend
python app.py
```

The app will be available at `http://127.0.0.1:5000`

## Environment Variables

| Variable    | Description              | Default             |
|-------------|--------------------------|---------------------|
| DB_HOST     | MySQL host               | localhost           |
| DB_USER     | MySQL username           | root                |
| DB_PASSWORD | MySQL password           | (required for auth) |
| DB_NAME     | Database name            | deepfake_detector   |
| API_URL     | Backend API URL          | http://127.0.0.1:5000 |
| FLASK_DEBUG | Enable debug mode        | false               |

## Deployment

### Heroku

```bash
heroku create your-app-name
git push heroku main
```

### Render

Connect your GitHub repo and set the build command:
```
pip install -r requirements.txt
```
Start command:
```
cd backend && gunicorn app:app
```

## License

MIT
