const API = window.location.origin;

async function apiSignup(formData) {
  const res = await fetch(`${API}/api/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  return await res.json();
}

async function apiLogin(identifier, password) {
  const res = await fetch(`${API}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier, password })
  });
  return await res.json();
}

async function apiSaveScan(scanData) {
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
