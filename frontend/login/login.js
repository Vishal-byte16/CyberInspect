// ---------- Login page ----------
function showRegister(){
  document.getElementById('login-form').classList.remove('active');
  document.getElementById('register-form').classList.add('active');
}
function showLogin(){
  document.getElementById('register-form').classList.remove('active');
  document.getElementById('login-form').classList.add('active');
}

// If already logged in, skip straight to the dashboard
(async function redirectIfLoggedIn(){
  if(!token()) return;
  try{ await api('/api/auth/me'); location.href = 'dashboard.html'; }
  catch(e){ localStorage.removeItem('ci_token'); }
})();

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  try{
    currentUser = await apiLogin(email, password);
    toast('Login successful!', 'success');
    location.href = 'dashboard.html';
  }catch(err){
    toast(err.message, 'error');
  }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim().toLowerCase();
  const password = document.getElementById('reg-password').value;
  if(password.length < 8){ toast('Password must be at least 8 characters.', 'warn'); return; }
  try{
    currentUser = await apiRegister(name, email, password);
    toast('Account created successfully!', 'success');
    location.href = 'dashboard.html';
  }catch(err){
    toast(err.message, 'error');
  }
});
