// ---------- Shared multi-page bootstrap ----------
// Every authenticated page (dashboard.html, scanner.html, history.html,
// saved.html, profile.html, admin.html) calls initAuthedPage() once on load.
// It checks the session, fills in the shared sidebar/topbar, and then
// hands off to that page's own render function.

async function initAuthedPage(pageKey, renderFn){
  const t = token();
  if(!t){ showAuthGate(pageKey); return; }

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
      '</div>' +
    '</div>';
  document.body.appendChild(overlay);
}

function logout(){
  localStorage.removeItem('ci_token');
  currentUser = null;
  location.href = 'login.html';
}

function quickScan(){
  const url = document.getElementById('quick-scan-url').value.trim();
  if(!url) return;
  location.href = 'scanner.html?url=' + encodeURIComponent(url);
}
