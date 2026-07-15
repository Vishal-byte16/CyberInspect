// ---------- Authentication ----------
// Login
async function apiLogin(email, password){
  const body = new URLSearchParams({username:email, password});
  const res = await fetch(API+'/api/auth/login', {method:'POST',
    headers:{'Content-Type':'application/x-www-form-urlencoded'}, body});
  if(!res.ok) throw new Error('Invalid credentials');
  const data = await res.json();
  localStorage.setItem('ci_token', data.access_token);
  return data.user;
}
// Register
async function apiRegister(name,email,password){
  const data = await api('/api/auth/register',{method:'POST',
    body:JSON.stringify({name,email,password})});
  localStorage.setItem('ci_token', data.access_token);
  return data.user;

}



// ---------- Auth ----------
function showRegister(){ document.getElementById('login-form').classList.remove('active');
  document.getElementById('register-form').classList.add('active'); }
function showLogin(){ document.getElementById('register-form').classList.remove('active');
  document.getElementById('login-form').classList.add('active'); }

document.getElementById('login-form').addEventListener('submit', async (e) => {

    e.preventDefault();

    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    try {

        currentUser = await apiLogin(email, password);

        toast('Login successful!', 'success');

        enterApp();

    } catch (err) {

        toast(err.message, 'error');

    }

});

document.getElementById('register-form').addEventListener('submit', async (e) => {

    e.preventDefault();

    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim().toLowerCase();
    const password = document.getElementById('reg-password').value;

    if (password.length < 8) {
        toast('Password must be at least 8 characters.', 'warn');
        return;
    }

    try {

        currentUser = await apiRegister(name, email, password);

        toast('Account created successfully!', 'success');

        enterApp();

    } catch (err) {

        toast(err.message, 'error');

    }

});
function logout() {

    localStorage.removeItem('ci_token');

    currentUser = null;

    document.getElementById('app').classList.add('hidden');

    document.getElementById('auth-screen').classList.remove('hidden');

    toast("Logged out successfully.", "info");

}
function enterApp(){
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
  document.getElementById('user-avatar').textContent = currentUser.name[0].toUpperCase();
  document.getElementById('user-mini-name').textContent = currentUser.name;
  document.getElementById('user-mini-role').textContent = currentUser.role==='admin'?'Administrator':'Security Analyst';
  document.querySelectorAll('.admin-only').forEach(el=> el.style.display = currentUser.role==='admin'?'flex':'none');
  navigate('dashboard');
}