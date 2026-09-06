# DeepFake Detector — Detailed Project Documentation

**Version:** 1.0.0  
**Live URL:** https://deepfake-detector-yoxi.onrender.com  
**GitHub:** https://github.com/Akhil24thakur/deepfake-detector  
**Author:** Akhil Thakur  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [How It Works — End-to-End Flow](#3-how-it-works--end-to-end-flow)
4. [Project Structure](#4-project-structure)
5. [Technology Stack](#5-technology-stack)
6. [API Endpoints](#6-api-endpoints)
7. [Database Design](#7-database-design)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Authentication System](#9-authentication-system)
10. [Problems Faced & Solutions](#10-problems-faced--solutions)
11. [Deployment — Render](#11-deployment--render)
12. [Environment Variables & API Keys](#12-environment-variables--api-keys)
13. [User-Facing Fixes](#13-user-facing-fixes)
14. [Performance & Optimization](#14-performance--optimization)
15. [AI Detection Models (Detailed)](#15-ai-detection-models-detailed)
16. [Future Improvements](#16-future-improvements)

---

## 1. Project Overview

The **DeepFake Detector** is a web application that analyzes uploaded images to determine whether they are AI-generated or real photographs. It uses an ensemble approach combining multiple AI detection models for higher accuracy.

### Key Features

| Feature | Description |
|---------|-------------|
| Image Upload | Drag-and-drop or click-to-upload interface |
| AI Detection | Multi-model ensemble (Hive + NVIDIA Vision) |
| Confidence Scoring | AI score vs Real score with confidence levels |
| Source Identification | Identifies which AI generator created the image |
| Scan History | Saved scan results for registered users |
| Daily Limits | 4 free scans/day, 20 for premium users |
| Dark/Light Theme | Toggle between themes |
| Mobile Responsive | Works on all device sizes |

---

## 2. System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Upload   │  │  Result  │  │  Sign    │  │ History  │       │
│  │  Page     │  │  Page    │  │  In/Up   │  │  Page    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │             │
│       └──────────────┴──────────────┴──────────────┘             │
│                           │ HTTP                                 │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                    FLASK SERVER (Render)                         │
│  ┌────────────────────────┼─────────────────────────────────┐   │
│  │                   app.py                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│  │  │  /api/   │  │  /api/   │  │  /api/   │               │   │
│  │  │ analyze  │  │  health  │  │  signup  │               │   │
│  │  └────┬─────┘  └──────────┘  │  login   │               │   │
│  │       │                       └──────────┘               │   │
│  └───────┼───────────────────────────────────────────────────┘   │
│          │                                                       │
│  ┌───────┼───────────────────────────────────────────────────┐   │
│  │       ▼           DETECTION ENGINE                        │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │   │
│  │  │  Hive   │  │ NVIDIA  │  │Heuristic│                   │   │
│  │  │  API    │  │ Vision  │  │ Fallback│                   │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘                   │   │
│  │       └─────────────┼───────────┘                         │   │
│  │                     ▼                                     │   │
│  │              ┌─────────────┐                              │   │
│  │              │  Ensemble   │                              │   │
│  │              │  Combiner   │                              │   │
│  │              └─────────────┘                              │   │
│  └───────────────────────────────────────────────────────────┘   │
│          │                                                       │
│  ┌───────┼───────────────────────────────────────────────────┐   │
│  │       ▼           DATABASE                                │   │
│  │  ┌─────────┐  ┌──────────────┐                           │   │
│  │  │  users  │  │ scan_history │                           │   │
│  │  └─────────┘  └──────────────┘                           │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
    ┌─────────┐       ┌─────────┐       ┌─────────┐
    │  Hive   │       │ NVIDIA  │       │ SQLite  │
    │   API   │       │   API   │       │   DB    │
    └─────────┘       └─────────┘       └─────────┘
```

---

## 3. How It Works — End-to-End Flow

### Image Analysis Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER UPLOADS IMAGE                           │
│                  (index.html - drag/drop)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              200px THUMBNAIL CREATED (Frontend)                  │
│         • Resized to max 200px for localStorage                 │
│         • Prevents QuotaExceededError (5MB limit)               │
│         • Navigates to result.html with data in localStorage    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               FULL IMAGE SENT TO /api/analyze                   │
│         • Flask receives image file via multipart/form-data     │
│         • Validates format (JPEG, PNG, WebP, GIF, BMP)          │
│         • Checks file size (max 10MB)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DETECTION ENGINE                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Step 1: Try Hive API (if HIVE_API_KEY set)             │    │
│  │  • Convert image to base64                               │    │
│  │  • Send to api.hivemoderation.com/api/v2/task/sync      │    │
│  │  • Poll for results                                      │    │
│  │  • Returns: ai_generated/not_ai_generated scores         │    │
│  │  • Also returns: source (flux, midjourney, sd, etc.)     │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │  Step 2: Try NVIDIA Vision (if NVIDIA_API_KEY set)       │    │
│  │  • Convert image to base64                               │    │
│  │  • Send to moonshotai/kimi-k3 via NVIDIA API             │    │
│  │  • Ask: "Is this AI-generated?"                          │    │
│  │  • Parse JSON response                                   │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │  Step 3: Ensemble Combination (if 2+ models respond)     │    │
│  │  • Average AI scores from all models                     │    │
│  │  • If models agree → +10 confidence boost                │    │
│  │  • If models disagree → -10 confidence penalty           │    │
│  │  • Merge source/generator data                           │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐    │
│  │  Fallback: Heuristic Analysis (if all APIs fail)         │    │
│  │  • Noise variance analysis                               │    │
│  │  • Color channel correlation                             │    │
│  │  • Saturation distribution                               │    │
│  │  • Block texture analysis                                │    │
│  │  • Symmetry detection                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RESPONSE TO FRONTEND                          │
│         {                                                      │
│           "verdict": "AI Generated" | "Real Image",            │
│           "ai_score": 87.4,                                    │
│           "real_score": 12.6,                                  │
│           "confidence": "HIGH" | "MEDIUM" | "LOW",             │
│           "model": "Ensemble (Hive + NVIDIA)",                 │
│           "source": "Flux",                                    │
│           "generators": {"flux": 98.3, "sd": 1.2},            │
│           "models_used": 2,                                    │
│           "models_agree": true                                 │
│         }                                                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                RESULT DISPLAY (result.html)                     │
│         • Animated score ring                                   │
│         • Verdict card with icon                                │
│         • Source/generator tags                                 │
│         • Model consensus indicator                             │
│         • Detailed breakdown bars                               │
│         • Full analysis report                                  │
└─────────────────────────────────────────────────────────────────┘
```

### User Authentication Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   SIGNUP     │      │    LOGIN     │      │   SESSION    │
│              │      │              │      │              │
│ Enter name,  │      │ Enter email/ │      │ Store user   │
│ email, mobile│─────▶│ mobile +     │─────▶│ ID in        │
│ password     │      │ password     │      │ localStorage │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Hash password│      │ Verify hash  │      │ Attach to    │
│ with salt    │      │ against      │      │ scan save    │
│ (SHA-256)    │      │ stored hash  │      │ requests     │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Store in     │      │ Return user  │      │ Check daily  │
│ SQLite       │      │ object       │      │ scan limit   │
│ users table  │      │              │      │ (4 free/day) │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## 4. Project Structure

```
deepfake-detector/
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment variable template
├── Procfile                      # Render start command
├── runtime.txt                   # Python version (3.12.7)
├── render.yaml                   # Render service config
├── gunicorn_config.py            # Gunicorn settings (120s timeout)
├── requirements.txt              # Python dependencies
├── README.md                     # Project readme
├── wsgi.py                       # WSGI entry point for gunicorn
│
├── backend/
│   ├── __init__.py               # Package marker
│   ├── app.py                    # Flask app + routes
│   ├── config.py                 # Environment config
│   ├── data/
│   │   └── deepfake.db           # SQLite database (auto-created)
│   ├── models/
│   │   ├── detector.py           # AI detection engine
│   │   └── database.py           # SQLite database layer
│   ├── routes/
│   │   ├── auth.py               # Auth endpoints (signup/login)
│   │   └── scans.py              # Scan history endpoints
│   ├── utils/
│   │   └── image_utils.py        # Image validation helpers
│   └── temp_images/              # Temporary image storage (auto-cleaned)
│
└── frontend/
    ├── css/
    │   ├── main.css              # Main styles + themes
    │   ├── result.css            # Result page styles
    │   ├── hamburger.css         # Mobile menu styles
    │   └── mobile.css            # Responsive overrides
    ├── js/
    │   ├── api.js                # API helper functions
    │   ├── result.js             # Result page logic
    │   └── hamburger.js          # Menu + theme toggle
    └── pages/
        ├── index.html            # Home / upload page
        ├── signin.html           # Sign in page
        ├── signup.html           # Redirects to signin
        ├── result.html           # Analysis result dashboard
        └── history.html          # Scan history page
```

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Backend** | Python | 3.12.7 | Server-side logic |
| **Framework** | Flask | 3.0.0 | Web framework |
| **CORS** | flask-cors | 4.0.0 | Cross-origin support |
| **Database** | SQLite | 3.x | User/scan storage |
| **Image Processing** | Pillow | 11.0+ | Image loading/manipulation |
| **Numerical** | NumPy | 1.24+ | Heuristic analysis |
| **HTTP Client** | Requests | 2.31+ | API calls to Hive |
| **NVIDIA SDK** | langchain-nvidia-ai-endpoints | 0.1+ | Vision model access |
| **Server** | Gunicorn | 21.2.0 | Production WSGI server |
| **Frontend** | HTML5/CSS3/JS | Vanilla | No frameworks |
| **Hosting** | Render | Free tier | Cloud deployment |

---

## 6. API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check + detection mode |
| `POST` | `/api/analyze` | Analyze uploaded image |
| `POST` | `/api/signup` | Register new user |
| `POST` | `/api/login` | User login |

### Authenticated Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/user/<id>` | Get user profile |
| `POST` | `/api/scan/save` | Save scan to history |
| `GET` | `/api/scan/history/<id>` | Get scan history (paginated) |
| `GET` | `/api/scan/stats/<id>` | Get user scan statistics |

### Request/Response Examples

#### POST /api/analyze

**Request:**
```http
POST /api/analyze HTTP/1.1
Content-Type: multipart/form-data

image: <binary file data>
```

**Response (200 OK):**
```json
{
  "success": true,
  "verdict": "AI Generated",
  "is_ai": true,
  "ai_score": 87.4,
  "real_score": 12.6,
  "confidence": "HIGH",
  "processing_time": "2.34s",
  "image_info": {
    "filename": "test_image.jpg",
    "dimensions": "1024 x 768",
    "size": "1.2 MB",
    "format": "JPEG"
  },
  "model": "Ensemble (Hive AI Detection + NVIDIA Vision (kimi-k3))",
  "source": "Flux",
  "generators": {
    "flux": 98.3,
    "stablediffusion": 1.2
  },
  "models_used": 2,
  "models_agree": true,
  "breakdown": {
    "pixel_consistency": 74.3,
    "edge_sharpness": 91.7,
    "texture_analysis": 85.6,
    "gan_artifacts": 93.5,
    "color_distribution": 68.2,
    "noise_pattern": 79.5
  }
}
```

#### GET /api/health

**Response:**
```json
{
  "status": "running",
  "message": "DeepFake Detection API is live",
  "version": "1.0.0",
  "detection_mode": "Hive + NVIDIA",
  "models_active": 2
}
```

---

## 7. Database Design

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         users TABLE                             │
├─────────────────────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY AUTOINCREMENT               │
│ name            TEXT NOT NULL                                   │
│ username        TEXT                                            │
│ email           TEXT UNIQUE                                     │
│ mobile          TEXT UNIQUE                                     │
│ password_hash   TEXT NOT NULL                                   │
│ salt            TEXT NOT NULL                                   │
│ dob             TEXT                                            │
│ gender          TEXT                                            │
│ city            TEXT                                            │
│ plan            TEXT DEFAULT 'free'                             │
│ scans_today     INTEGER DEFAULT 0                              │
│ total_scans     INTEGER DEFAULT 0                              │
│ last_scan_date  TEXT                                            │
│ created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ 1:N
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    scan_history TABLE                            │
├─────────────────────────────────────────────────────────────────┤
│ id              INTEGER PRIMARY KEY AUTOINCREMENT               │
│ user_id         INTEGER (FK → users.id)                        │
│ verdict         TEXT NOT NULL                                   │
│ ai_score        REAL DEFAULT 0                                 │
│ real_score      REAL DEFAULT 0                                 │
│ confidence      TEXT DEFAULT 'MEDIUM'                          │
│ model_used      TEXT DEFAULT 'CNN v2.1'                        │
│ processing_time TEXT DEFAULT ''                                 │
│ status          TEXT DEFAULT 'completed'                       │
│ error_message   TEXT DEFAULT ''                                 │
│ scanned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP            │
└─────────────────────────────────────────────────────────────────┘
```

### SQLite Configuration

- **WAL Mode:** Enabled for better concurrent read performance
- **Foreign Keys:** Enforced for data integrity
- **Thread-Local Connections:** Each thread gets its own connection
- **Auto-Creation:** Tables created on startup if not exist

---

## 8. Frontend Architecture

### Page Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER JOURNEY                               │
│                                                                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │  index   │───▶│  result  │───▶│  save    │───▶│ history  │ │
│   │  .html   │    │  .html   │    │ (auto)   │    │  .html   │ │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │                                                       │  │
│       │           ┌──────────┐    ┌──────────┐               │  │
│       └──────────▶│ signin   │───▶│  auth    │───────────────┘  │
│                   │ .html    │    │  (API)   │                  │
│                   └──────────┘    └──────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Between Pages

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCALSTORAGE KEYS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  "deepfake_result"  →  Full API response (JSON)                 │
│  "deepfake_image"   →  200px JPEG thumbnail (base64)            │
│  "user"             →  User object (id, name, email, plan)      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

     index.html                    result.html
     ┌─────────┐                   ┌─────────┐
     │ Upload  │   store data      │ Display │
     │ image   │──────────────────▶│ results │
     │         │   localStorage    │         │
     └─────────┘                   └─────────┘
```

### CSS Theme System

```css
/* Dark Theme (default) */
[data-theme="dark"] {
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  --accent-primary: #6366f1;
}

/* Light Theme */
[data-theme="light"] {
  --bg-primary: #f8fafc;
  --bg-secondary: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --accent-primary: #4f46e5;
}
```

---

## 9. Authentication System

### Password Hashing

```
┌─────────────────────────────────────────────────────────────────┐
│                    PASSWORD HASHING                             │
│                                                                  │
│  User Password: "mypassword123"                                 │
│           │                                                     │
│           ▼                                                     │
│  Generate Salt: secrets.token_hex(16)                          │
│  Salt: "a1b2c3d4e5f6..." (32 hex chars)                        │
│           │                                                     │
│           ▼                                                     │
│  Hash: SHA-256(password + salt)                                │
│  Hash: "e99a18c428cb38d5f260853678922e03..."                   │
│           │                                                     │
│           ▼                                                     │
│  Store in DB: (hash, salt)                                      │
│                                                                  │
│  Verification:                                                   │
│  SHA-256(entered_password + stored_salt) == stored_hash        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Scan Limit System

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCAN LIMIT LOGIC                             │
│                                                                  │
│  Plan: "free"  → 4 scans/day                                   │
│  Plan: "premium" → 20 scans/day                                │
│                                                                  │
│  Daily Reset:                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ if last_scan_date != today:                             │    │
│  │     scans_today = 0                                     │    │
│  │     last_scan_date = today                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Check Before Save:                                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ if scans_today >= limit:                                │    │
│  │     return 429 Too Many Requests                        │    │
│  │     "Daily scan limit reached (4/4)"                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Problems Faced & Solutions

### Problem 1: MySQL to SQLite Migration

**Problem:** Original project used MySQL which isn't available on Render free tier.

**Solution:** Migrated to SQLite with thread-safe connections.

```python
# database.py - Thread-local SQLite connections
_local = threading.local()

def _get_connection():
    if not hasattr(_local, "conn") or _local.conn is None:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        _local.conn = conn
    return _local.conn
```

**Additional Fix:** MySQL uses `%s` placeholders, SQLite uses `?`.

```python
def _convert_params(sql):
    """Convert MySQL %s placeholders to SQLite ? placeholders."""
    return re.sub(r"%s", "?", sql)
```

---

### Problem 2: Python 3.14 Incompatibility

**Problem:** Render defaulted to Python 3.14 which broke Pillow installation.

**Solution:** Pinned Python version via `runtime.txt` and environment variable.

```
# runtime.txt
python-3.12.7
```

**Render Dashboard Setting:**
```
PYTHON_VERSION = 3.12.7
```

---

### Problem 3: Gunicorn Start Command

**Problem:** Initial start command `gunicorn app:app` failed because `app.py` is in `backend/` not root.

**Solution:** Created `wsgi.py` at root that adjusts sys.path.

```python
# wsgi.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app import app
```

**Start Command:**
```
gunicorn -c gunicorn_config.py wsgi:app
```

---

### Problem 4: Flask Static Folder Hijacking

**Problem:** Flask's `static_folder` parameter intercepted requests for `result.html`, serving `index.html` instead.

**Root Cause:** When no `static_folder` is set, Flask defaults to serving from the app's directory. The `/<path:filename>` route was catching `result.html` and falling back to `index.html`.

**Solution:** Removed `static_folder` parameter and explicit route handling.

```python
# Before (broken)
app = Flask(__name__, static_folder="../frontend")

# After (working)
app = Flask(__name__)
```

---

### Problem 5: localStorage QuotaExceededError

**Problem:** Storing full base64 images (>5MB) in localStorage caused `QuotaExceededError`.

**Solution:** Create 200px thumbnail before storing.

```javascript
// index.html - Before navigation
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
const img = new Image();
img.onload = () => {
    const size = 200;
    const ratio = Math.min(size / img.width, size / img.height);
    canvas.width = img.width * ratio;
    canvas.height = img.height * ratio;
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    const thumbnail = canvas.toDataURL('image/jpeg', 0.7);
    localStorage.setItem('deepfake_image', thumbnail);
    window.location.href = 'result.html';
};
img.src = e.target.result;
```

---

### Problem 6: Broken AI Detection Models

**Problem:** Attempted approaches that failed:

1. **Heuristic approach** — Classified everything as "Real"
2. **Trained CNN (ONNX)** — Overfit, classified everything as "AI Generated"

**Root Cause:** No training data for real-world AI detection; synthetic training data doesn't generalize.

**Solution:** Use external AI detection APIs (Hive + NVIDIA Vision).

---

### Problem 7: Render Free Tier Spin-Down

**Problem:** Render free tier spins down after 15 minutes of inactivity, causing slow cold starts.

**Solution:** Set up UptimeRobot to ping `/api/health` every 5 minutes.

```
Monitor Type: HTTP(s)
URL: https://deepfake-detector-yoxi.onrender.com/api/health
Interval: 5 minutes
Uptime Goal: 100%
```

---

### Problem 8: Render Environment Variables

**Problem:** `render.yaml` doesn't override manually-created service settings.

**Solution:** Set critical env vars in Render dashboard:

```
PYTHON_VERSION = 3.12.7     (in dashboard, not render.yaml)
SECRET_KEY = <generated>    (in dashboard)
HIVE_API_KEY = <your-key>   (in dashboard)
NVIDIA_API_KEY = <your-key> (in dashboard)
```

---

## 11. Deployment — Render

### Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    RENDER DEPLOYMENT                            │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  GitHub  │───▶│  Render  │───▶│  Build   │───▶│  Deploy  │  │
│  │  Push    │    │  Detect  │    │  pip     │    │  gunicorn│  │
│  └──────────┘    └──────────┘    │ install  │    │  start   │  │
│                                   └──────────┘    └──────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration Files

**render.yaml:**
```yaml
services:
  - type: web
    name: deepfake-detector
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -c gunicorn_config.py wsgi:app
    envVars:
      - key: PYTHON_VERSION
        value: "3.12.7"
      - key: FLASK_DEBUG
        value: "false"
      - key: SECRET_KEY
        generateValue: true
```

**gunicorn_config.py:**
```python
timeout = 120
workers = 1
preload_app = True
```

**Procfile:**
```
web: gunicorn -c gunicorn_config.py wsgi:app
```

---

## 12. Environment Variables & API Keys

### Required Variables

| Variable | Where to Set | Description |
|----------|--------------|-------------|
| `SECRET_KEY` | Render Dashboard | Flask session secret |
| `PYTHON_VERSION` | Render Dashboard | Must be `3.12.7` |

### Detection API Keys (Optional — with fallback)

| Variable | Source | Free Tier |
|----------|--------|-----------|
| `HIVE_API_KEY` | Hive Moderation Dashboard | 100 scans/month |
| `NVIDIA_API_KEY` | NVIDIA NGC Catalog | Varies by model |

### How to Get API Keys

#### Hive Moderation API Key

1. Go to https://dashboard.hivemoderation.com
2. Sign up for free account
3. Create a new application
4. Copy the API key from the application settings
5. Add to Render dashboard as `HIVE_API_KEY`

**Hive API Details:**
- Endpoint: `https://api.hivemoderation.com/api/v2/task/sync`
- Model: `ai_generated_media`
- Returns: AI probability, source classification (flux, midjourney, sd, etc.)
- Free tier: 100 scans/month

#### NVIDIA API Key

1. Go to https://catalog.ngc.nvidia.com
2. Sign up for NVIDIA account
3. Generate an API key
4. Add to Render dashboard as `NVIDIA_API_KEY`

**NVIDIA API Details:**
- Model: `moonshotai/kimi-k3` (vision model)
- Uses langchain-nvidia-ai-endpoints SDK
- Sends image as base64, asks "Is this AI-generated?"
- Parses JSON response with is_ai + confidence

---

## 13. User-Facing Fixes

### Fix 1: Image Upload Not Working

**Symptom:** Upload button does nothing or shows error.

**Causes & Solutions:**
- File too large → Max 10MB allowed
- Wrong format → Only JPEG, PNG, WebP, GIF, BMP supported
- Browser cache → Clear cache and reload

### Fix 2: Result Page Not Loading

**Symptom:** Shows blank page or index.html instead of results.

**Cause:** Flask static_folder hijacking (fixed in code).

**User Fix:** Hard refresh (Ctrl+Shift+R) after deployment.

### Fix 3: Scan History Empty

**Symptom:** History page shows no scans.

**Cause:** Must be signed in to save scans.

**User Fix:** Sign in first, then scans will be saved automatically.

### Fix 4: Daily Limit Reached

**Symptom:** "Daily scan limit reached (4/4)" error.

**Cause:** Free plan limited to 4 scans per day.

**User Fix:** Wait until tomorrow or upgrade to premium (when available).

### Fix 5: Theme Not Persisting

**Symptom:** Theme resets on page reload.

**Cause:** Theme stored in localStorage.

**User Fix:** Click theme toggle on each page visit (feature, not bug).

---

## 14. Performance & Optimization

### Image Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                 IMAGE PROCESSING STEPS                          │
│                                                                  │
│  1. Receive upload (multipart/form-data)                       │
│           │                                                     │
│           ▼                                                     │
│  2. Validate format (check magic bytes, not just extension)    │
│           │                                                     │
│           ▼                                                     │
│  3. Load with Pillow (PIL)                                      │
│           │                                                     │
│           ▼                                                     │
│  4. Resize if > 1024px (for Hive) or > 512px (for NVIDIA)     │
│           │                                                     │
│           ▼                                                     │
│  5. Convert to RGB (handle RGBA, palette, etc.)                │
│           │                                                     │
│           ▼                                                     │
│  6. Save as JPEG (quality=90) for base64 encoding              │
│           │                                                     │
│           ▼                                                     │
│  7. Send to detection APIs                                      │
│           │                                                     │
│           ▼                                                     │
│  8. Clean up temp file                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Timeout Configuration

| Component | Timeout | Reason |
|-----------|---------|--------|
| Gunicorn | 120s | Allow time for API calls |
| Hive API | 30s | External API latency |
| NVIDIA API | 30s | External API latency |
| Render Health | 5min | UptimeRobot interval |

### Memory Management

- **Temp files:** Auto-deleted after each scan
- **Thread-local DB connections:** Prevents connection leaks
- **WAL mode:** Better concurrent read performance
- **Image resizing:** Reduces memory footprint before API calls

---

## 15. AI Detection Models (Detailed)

### Model Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENSEMBLE DETECTION                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    INPUT IMAGE                           │    │
│  │              (user uploaded file)                        │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │                                    │
│              ┌──────────────┼──────────────┐                    │
│              ▼              ▼              ▼                    │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │  HIVE API     │ │  NVIDIA API   │ │  HEURISTIC    │         │
│  │               │ │               │ │               │         │
│  │  Specialized  │ │  Vision LLM   │ │  Pixel-level  │         │
│  │  AI detection │ │  (kimi-k3)    │ │  analysis     │         │
│  │  model        │ │               │ │               │         │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘         │
│          │                 │                 │                   │
│          ▼                 ▼                 ▼                   │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │  Result:      │ │  Result:      │ │  Result:      │         │
│  │  ai: 0.95     │ │  ai: 0.88     │ │  ai: 0.72     │         │
│  │  source: flux │ │  reason: ...  │ │  method: ...  │         │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘         │
│          │                 │                 │                   │
│          └─────────────────┼─────────────────┘                   │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  ENSEMBLE COMBINER                       │    │
│  │                                                          │    │
│  │  if 2+ models respond:                                  │    │
│  │    avg_score = mean(all_ai_scores)                      │    │
│  │    if all_agree: boost = +10                            │    │
│  │    if disagree: boost = -10                             │    │
│  │    final_score = avg_score + boost                      │    │
│  │                                                          │    │
│  │  if 1 model responds: use that result directly          │    │
│  │  if 0 models respond: use heuristic fallback            │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   FINAL RESULT                           │    │
│  │  {                                                      │    │
│  │    verdict: "AI Generated",                             │    │
│  │    ai_score: 87.4,                                      │    │
│  │    confidence: "HIGH",                                  │    │
│  │    model: "Ensemble (Hive + NVIDIA)",                   │    │
│  │    models_agree: true                                   │    │
│  │  }                                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Hive Moderation API

**How it works:**
1. Image sent as base64 data URL to Hive endpoint
2. Hive runs specialized AI-generated content detection model
3. Returns probability scores for `ai_generated` vs `not_ai_generated`
4. Also classifies source: flux, midjourney, stable diffusion, dalle, etc.

**Response format:**
```json
{
  "classes": [
    {"class": "ai_generated", "score": 0.98},
    {"class": "not_ai_generated", "score": 0.02},
    {"class": "flux", "score": 0.95},
    {"class": "stablediffusion", "score": 0.03}
  ]
}
```

**Supported generators:** 50+ including flux, midjourney, stable diffusion, dalle, sora, pika, kling, runway, and many more.

---

### NVIDIA Vision Model (kimi-k3)

**How it works:**
1. Image converted to base64
2. Sent to NVIDIA API with structured prompt
3. Vision LLM analyzes image characteristics
4. Returns JSON with is_ai boolean + confidence score

**Prompt:**
```
Analyze this image and determine if it is AI-generated or a real photograph.

Respond with ONLY a JSON object:
{"is_ai": true/false, "confidence": 0.0-1.0, "reason": "brief explanation"}
```

**Response parsing:**
```python
json_match = re.search(r'\{[^}]+\}', text)
data = json.loads(json_match.group())
# data = {"is_ai": true, "confidence": 0.95, "reason": "..."}
```

---

### Heuristic Analysis (Fallback)

**Used when:** Both Hive and NVIDIA APIs are unavailable.

**Signals analyzed:**

| Signal | What It Measures | AI Indicator |
|--------|------------------|--------------|
| Noise variance | Laplacian filter variance | Low noise = likely AI |
| Color correlation | RGB channel correlation | High correlation = likely AI |
| Saturation std | Color saturation distribution | Low std = likely AI |
| Block texture | Block-wise std deviation | Uniform blocks = likely AI |
| Symmetry | Horizontal mirror symmetry | High symmetry = likely AI |

**Score calculation:**
```python
score = 50.0  # Start neutral

if noise_var < 20:    score += 15  # Too clean
if avg_corr > 0.92:   score += 10  # Too correlated
if sat_std < 0.05:    score += 10  # Too uniform
if block_std < 5:     score += 8   # Too smooth
if symmetry > 0.9:    score += 12  # Too symmetric

score = clamp(score, 5, 95)
```

**Note:** Heuristic is not reliable for real-world detection — only used as last resort fallback.

---

### Ensemble Decision Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                 ENSEMBLE DECISION TREE                          │
│                                                                  │
│  models_available = []                                          │
│                                                                  │
│  if HIVE_API_KEY:                                               │
│      try: models_available.append(hive_result)                  │
│      except: log error                                          │
│                                                                  │
│  if NVIDIA_API_KEY:                                             │
│      try: models_available.append(nvidia_result)                │
│      except: log error                                          │
│                                                                  │
│  if len(models_available) >= 2:                                 │
│      │                                                           │
│      ├── avg_ai = mean([r.ai_score for r in models])           │
│      │                                                           │
│      ├── all_agree = all(r.is_ai) or all(not r.is_ai)         │
│      │                                                           │
│      ├── if all_agree:                                          │
│      │     final_score = avg_ai + 10  (confidence boost)       │
│      │                                                           │
│      └── if disagree:                                           │
│            final_score = avg_ai - 10  (confidence penalty)     │
│                                                                  │
│  elif len(models_available) == 1:                               │
│      return models_available[0]                                 │
│                                                                  │
│  else:                                                          │
│      return heuristic_fallback()                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 16. Future Improvements

### Short Term

- [ ] Add rate limiting to prevent API abuse
- [ ] Implement image caching to reduce API calls
- [ ] Add batch scanning for multiple images
- [ ] Email notifications for scan results
- [ ] Premium plan payment integration

### Medium Term

- [ ] Video deepfake detection support
- [ ] Real-time webcam analysis
- [ ] Browser extension for quick checks
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Unit tests and integration tests

### Long Term

- [ ] Custom trained model on real dataset
- [ ] Mobile app (React Native/Flutter)
- [ ] Enterprise API with higher limits
- [ ] Integration with social media platforms
- [ ] Real-time streaming analysis

---

## Appendix A: Git History (Key Commits)

| Commit | Description |
|--------|-------------|
| `6faaf1c` | feat: integrate Hive Moderation API for real AI detection |
| `2903b77` | feat: add NVIDIA Vision model as secondary detector |
| `61d0aab` | Initial working deployment on Render |

---

## Appendix B: API Rate Limits

| API | Free Tier Limit | Notes |
|-----|-----------------|-------|
| Hive Moderation | 100 scans/month | Per account |
| NVIDIA API | Varies | Check NGC dashboard |
| Render | 750 hours/month | Free tier |

---

## Appendix C: Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: langchain_nvidia_ai_endpoints` | Run `pip install langchain-nvidia-ai-endpoints` |
| `OperationalError: database is locked` | Restart the server (SQLite WAL mode issue) |
| `413 Request Entity Too Large` | Image exceeds 10MB limit |
| `Hive API failed` | Check HIVE_API_KEY is set correctly |
| `NVIDIA API failed` | Check NVIDIA_API_KEY and network access |
| Cold start slow (30-60s) | Normal for Render free tier after spin-down |

---

**Document Version:** 1.0  
**Last Updated:** September 2026  
**Status:** Production (Live)
