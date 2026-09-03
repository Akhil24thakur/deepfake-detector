// hamburger.js — Final Clean Version

// Active page highlight
(function () {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.menu-nav-item').forEach(el => {
    el.classList.remove('active');
    if (el.getAttribute('href') === page) el.classList.add('active');
  });
  document.querySelectorAll('.nav-links a').forEach(el => {
    el.classList.remove('active');
    if (el.getAttribute('href') === page) el.classList.add('active');
  });
})();

function openMenu() {
  document.getElementById('sideMenu').classList.add('open');
  document.getElementById('menuOverlay').classList.add('open');
  document.getElementById('hamburgerBtn').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeMenu() {
  document.getElementById('sideMenu').classList.remove('open');
  document.getElementById('menuOverlay').classList.remove('open');
  document.getElementById('hamburgerBtn').classList.remove('open');
  document.body.style.overflow = '';
}
function toggleMenu() {
  document.getElementById('sideMenu').classList.contains('open') ? closeMenu() : openMenu();
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });

// Theme
function applyTheme(isDark) {
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  const emoji = isDark ? '🌙' : '☀️';
  const label = isDark ? 'Dark Mode' : 'Light Mode';
  const icon  = document.querySelector('.theme-icon');
  const rIcon = document.getElementById('themeRowIcon');
  const rText = document.getElementById('themeRowText');
  const sw    = document.getElementById('themeSwitchInput');
  if (icon)  icon.textContent  = emoji;
  if (rIcon) rIcon.textContent = emoji;
  if (rText) rText.textContent = label;
  if (sw)    sw.checked        = !isDark;
  localStorage.setItem('df_theme', isDark ? 'dark' : 'light');
}
function toggleTheme() { applyTheme(document.documentElement.getAttribute('data-theme') !== 'dark'); }
function toggleThemeSwitch(cb) { applyTheme(!cb.checked); }
(function () { applyTheme((localStorage.getItem('df_theme') || 'dark') === 'dark'); })();

// Desktop dropdown
function toggleDesktopDropdown() { document.getElementById('desktopDropdown')?.classList.toggle('open'); }
document.addEventListener('click', e => {
  const wrap = document.querySelector('.desktop-profile-wrap');
  const dd = document.getElementById('desktopDropdown');
  if (dd && wrap && !wrap.contains(e.target)) dd.classList.remove('open');
});

// Auth UI
function updateAuthUI() {
  const user = JSON.parse(localStorage.getItem('df_user') || 'null');
  const ids = {
    guestSec:  document.getElementById('menuGuestSection'),
    userSec:   document.getElementById('menuUserSection'),
    signInL:   document.getElementById('menuSignInLink'),
    signUpL:   document.getElementById('menuSignUpLink'),
    signOutB:  document.getElementById('menuSignOutBtn'),
    profileL:  document.getElementById('menuProfileLink'),
    deskProf:  document.getElementById('desktopProfileBtn'),
    deskTheme: document.getElementById('desktopThemeBtn'),
  };

  if (user) {
    const init  = getInitials(user.name);
    const total = user.scansLimit || 4;
    const today = user.scansToday || 0;

    if (ids.guestSec) ids.guestSec.style.display = 'none';
    if (ids.userSec)  ids.userSec.classList.add('visible');
    setText('menuAvatarText', init);
    setText('menuUserName',   user.name);
    setText('menuUserEmail',  user.email);

    const badge = document.getElementById('menuScanBadge');
    if (badge) {
      badge.textContent = `⚡ ${today}/${total} scans today`;
      badge.className = 'menu-scan-badge' + ((total - today) <= 1 ? ' limit' : '');
    }
    const hb = document.getElementById('menuHistoryBadge');
    if (hb && user.historyCount > 0) { hb.textContent = user.historyCount; hb.style.display = ''; }

    if (ids.signInL)  ids.signInL.style.display  = 'none';
    if (ids.signUpL)  ids.signUpL.style.display   = 'none';
    if (ids.signOutB) ids.signOutB.style.display  = '';
    if (ids.profileL) ids.profileL.style.display  = '';

    if (ids.deskProf) {
      ids.deskProf.classList.add('visible');
      setText('desktopAvatarText',  init);
      setText('desktopProfileName', user.name.split(' ')[0]);
      setText('dropdownName',       user.name);
      setText('dropdownEmail',      user.email);
      setText('dropdownScans',      `${today}/${total}`);
    }
    if (ids.deskTheme) ids.deskTheme.style.display = 'none';
  } else {
    if (ids.guestSec) ids.guestSec.style.display = '';
    if (ids.userSec)  ids.userSec.classList.remove('visible');
    if (ids.signInL)  ids.signInL.style.display  = '';
    if (ids.signUpL)  ids.signUpL.style.display   = '';
    if (ids.signOutB) ids.signOutB.style.display  = 'none';
    if (ids.profileL) ids.profileL.style.display  = 'none';
    if (ids.deskProf)  ids.deskProf.classList.remove('visible');
    if (ids.deskTheme) ids.deskTheme.style.display = '';
  }
}
function getInitials(name) { return (name||'?').trim().split(' ').filter(Boolean).map(w=>w[0].toUpperCase()).slice(0,2).join(''); }
function setText(id, val) { const el = document.getElementById(id); if (el) el.textContent = val || ''; }
function signOut() { localStorage.removeItem('df_user'); closeMenu(); updateAuthUI(); const p = window.location.pathname; if (p.includes('history') || p.includes('profile')) window.location.href = 'index.html'; }
function editProfile() { closeMenu(); window.location.href = 'profile.html'; }

updateAuthUI();

// Test helpers
window.df_simulateLogin = (name, email, scansToday=0) => { localStorage.setItem('df_user', JSON.stringify({name,email,scansToday,scansLimit:4,historyCount:scansToday,plan:'free'})); updateAuthUI(); console.log('✅ Login:',name); };
window.df_simulateLogout = () => { localStorage.removeItem('df_user'); updateAuthUI(); console.log('👋 Logout'); };
