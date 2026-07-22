// ---------- Shared multi-page bootstrap ----------
// Every authenticated page (dashboard.html, scanner.html, history.html,
// saved.html, profile.html, admin.html) calls initAuthedPage() once on load.
// It checks the session, fills in the shared sidebar/topbar, and then
// hands off to that page's own render function.

async function initAuthedPage(pageKey, renderFn){
  const t = token();
  if(!t){ location.href = 'login.html'; return; }

  try{
    currentUser = await api('/api/auth/me');
  }catch(e){
    localStorage.removeItem('ci_token');
    location.href = 'login.html';
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
