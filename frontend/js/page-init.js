// ---------- Shared multi-page bootstrap ----------
// Every authenticated page (dashboard.html, scanner.html, history.html,
// saved.html, profile.html, admin.html) calls initAuthedPage() once on load.
// It checks the session, fills in the shared sidebar/topbar, and then
// hands off to that page's own render function.

// Pages a guest (no account) is allowed to use at all. Everything else —
// dashboard, history, saved, profile, admin — always shows the auth gate,
// since those pages are inherently tied to a real, persisted account.
const GUEST_ALLOWED_PAGES = ['scanner'];

function isGuest(){ return sessionStorage.getItem('ci_guest') === '1'; }

async function initAuthedPage(pageKey, renderFn){
  const t = token();
  if(!t){
    if(GUEST_ALLOWED_PAGES.includes(pageKey) && isGuest()){
      applyGuestShell();
      await renderFn(document.getElementById('content'));
      return;
    }
    showAuthGate(pageKey);
    return;
  }

  try{
    currentUser = await api('/api/auth/me');
  }catch(e){
    localStorage.removeItem('ci_token');
    showAuthGate(pageKey);
    return;
  }

  document.getElementById('user-avatar').textContent = currentUser.name[0].toUpperCase();
  document.getElementById('user-mini-name').textContent = currentUser.name;
  document.getElementById('user-mini-role').textContent =
    currentUser.role === 'admin' ? 'Administrator' : 'Security Analyst';
  document.querySelectorAll('.admin-only').forEach(el =>
    el.style.display = currentUser.role === 'admin' ? 'flex' : 'none');

  const content = document.getElementById('content');
  if(pageKey === 'admin' && currentUser.role !== 'admin'){
    content.innerHTML = '<div class="card">Access denied. This page is for administrators only.</div>';
    return;
  }
  await renderFn(content);
}

// Adjusts the shared sidebar/topbar for a guest session: marks the
// account-only nav items as locked, swaps the user card for a "Guest"
// state, and adds a small banner reminding them nothing will be saved.
function applyGuestShell(){
  const lockedPages = ['dashboard.html', 'history.html', 'saved.html', 'profile.html', 'admin.html'];
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
    const href = el.getAttribute('href');
    if(lockedPages.includes(href)){
      el.classList.add('nav-item-locked');
      el.innerHTML += ' <span class="lock-badge">🔒</span>';
      el.addEventListener('click', e => {
        e.preventDefault();
        toast('Sign in to access this — you\'re currently browsing as a guest.', 'warn');
      });
    }
  });

  const avatar = document.getElementById('user-avatar');
  const name = document.getElementById('user-mini-name');
  const role = document.getElementById('user-mini-role');
  if(avatar) avatar.textContent = 'G';
  if(name) name.textContent = 'Guest';
  if(role) role.textContent = 'Not signed in';

  const footer = document.querySelector('.sidebar-footer');
  const logoutBtn = footer && footer.querySelector('button');
  if(logoutBtn){
    logoutBtn.textContent = 'Sign in';
    logoutBtn.setAttribute('onclick', "location.href='login.html'");
  }

  const topbar = document.querySelector('.topbar');
  if(topbar && !document.getElementById('guest-banner')){
    const banner = document.createElement('div');
    banner.id = 'guest-banner';
    banner.className = 'guest-banner';
    banner.innerHTML = 'Browsing as guest — results aren\'t saved. ' +
      '<a href="login.html?mode=register">Create a free account</a> to keep your scan history.';
    topbar.insertAdjacentElement('afterend', banner);
  }
}

function exitGuest(){
  sessionStorage.removeItem('ci_guest');
}

// Shown instead of an immediate redirect when there's no valid session.
// Blurs whatever shell/content is already on the page and overlays a
// sign-in / create-account prompt, so visitors get a preview instead of
// being bounced straight to login.html.
function showAuthGate(pageKey){
  if(document.getElementById('auth-gate-overlay')) return; // already shown

  const app = document.getElementById('app');
  if(app) app.classList.add('blurred-preview');

  const content = document.getElementById('content');
  if(content && !content.innerHTML.trim()){
    content.innerHTML =
      '<div class="grid grid-4">' +
        '<div class="card stat-card"><div class="stat-icon">📊</div><div class="stat-val">—</div><div class="stat-label">Total Scans</div></div>' +
        '<div class="card stat-card"><div class="stat-icon">📈</div><div class="stat-val">—</div><div class="stat-label">Avg Security Score</div></div>' +
        '<div class="card stat-card"><div class="stat-icon">⚠️</div><div class="stat-val">—</div><div class="stat-label">High-Risk Sites</div></div>' +
        '<div class="card stat-card"><div class="stat-icon">⭐</div><div class="stat-val">—</div><div class="stat-label">Saved Websites</div></div>' +
      '</div>';
  }

  const urlParam = new URLSearchParams(location.search).get('url');
  const redirectTarget = encodeURIComponent(location.pathname + location.search);

  const overlay = document.createElement('div');
  overlay.id = 'auth-gate-overlay';
  overlay.className = 'modal auth-gate-overlay';
  overlay.innerHTML =
    '<div class="modal-content auth-gate-card">' +
      '<div class="logo-shield">🛡️</div>' +
      '<h2>Sign in to continue</h2>' +
      '<p class="muted">Create a free account to run scans, save results, and track your security history.' +
      (urlParam ? ' Your URL <b class="mono">' + urlParam.replace(/</g,'&lt;') + '</b> is ready to scan as soon as you sign in.' : '') +
      '</p>' +
      '<div class="auth-gate-actions">' +
        '<a class="btn btn-primary btn-full" href="login.html?mode=register&redirect=' + redirectTarget + '">Create free account</a>' +
        '<a class="btn btn-ghost btn-full" href="login.html?redirect=' + redirectTarget + '">Sign in</a>' +
        '<a class="btn btn-outline btn-full" href="scanner.html' + (urlParam ? '?url=' + encodeURIComponent(urlParam) : '') +
          '" onclick="sessionStorage.setItem(\'ci_guest\',\'1\')">Continue as guest</a>' +
      '</div>' +
      '<p class="auth-gate-note muted">Guests can run scans, but can\'t save results, export reports, or view scan history.</p>' +
    '</div>';
  document.body.appendChild(overlay);
}

function logout(){
  localStorage.removeItem('ci_token');
  sessionStorage.removeItem('ci_guest');
  currentUser = null;
  location.href = 'login.html';
}

function quickScan(){
  const url = document.getElementById('quick-scan-url').value.trim();
  if(!url) return;
  location.href = 'scanner.html?url=' + encodeURIComponent(url);
}
