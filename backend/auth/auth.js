// ---------- Authentication (pure API calls, shared by every page) ----------
async function apiLogin(email, password){
  const body = new URLSearchParams({username:email, password});
  const res = await fetch(API+'/api/auth/login', {method:'POST',
    headers:{'Content-Type':'application/x-www-form-urlencoded'}, body});
  if(!res.ok) throw new Error('Invalid credentials');
  const data = await res.json();
  localStorage.setItem('ci_token', data.access_token);
  return data.user;
}

async function apiRegister(name, email, password){
  const data = await api('/api/auth/register', {method:'POST',
    body: JSON.stringify({name, email, password})});
  localStorage.setItem('ci_token', data.access_token);
  return data.user;
}
