// frontend/api.js
// Yeh file sabhi pages mein include karo: <script src="api.js"></script>
// Sab fetch calls yahan se hoti hain

const API_URL = "https://deepfake-detection-system-jnfo.onrender.com" // Flask server URL
const API = API_URL

// ════════════════════════════════
// AUTH FUNCTIONS
// ════════════════════════════════

async function apiSignup(formData) {
  // formData = { name, username, email, mobile, password, dob, gender, city }
  const res = await fetch(`${API}/api/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  return await res.json();
}

async function apiLogin(identifier, password) {
  // identifier = email ya mobile number
  const res = await fetch(`${API}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier, password })
  });
  return await res.json();
}

// ════════════════════════════════
// SCAN FUNCTIONS
// ════════════════════════════════

async function apiSaveScan(scanData) {
  // scanData = { user_id, verdict, ai_score, real_score, confidence, processing_time, status }
  const res = await fetch(`${API}/api/scan/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(scanData)
  });
  return await res.json();
}

async function apiGetHistory(userId, page = 1) {
  const res = await fetch(`${API}/api/scan/history/${userId}?page=${page}&limit=10`);
  return await res.json();
}

async function apiGetStats(userId) {
  const res = await fetch(`${API}/api/scan/stats/${userId}`);
  return await res.json();
}

// ════════════════════════════════
// LOCAL SESSION HELPERS
// ════════════════════════════════

function saveSession(user) {
  localStorage.setItem('df_user', JSON.stringify(user));
}

function getSession() {
  const u = localStorage.getItem('df_user');
  return u ? JSON.parse(u) : null;
}

function clearSession() {
  localStorage.removeItem('df_user');
}

function isLoggedIn() {
  return getSession() !== null;
}