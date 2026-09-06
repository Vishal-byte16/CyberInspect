// ---------- API Layer (replaces mockScan + localStorage) ----------
const API = "https://cyberinspect-rebk.onrender.com";
function token(){ return localStorage.getItem('ci_token'); }
async function api(path, opts={}){
  const res = await fetch(API+path, {
    ...opts,
    headers: {'Content-Type':'application/json',
      ...(token()?{'Authorization':'Bearer '+token()}:{}), ...(opts.headers||{})}
  });
  if(!res.ok){
    const e = await res.json().catch(()=>({detail:'Error'}));
    let msg = e.detail;
    if(Array.isArray(msg)){
      msg = msg.map(d => `${(d.loc||[]).slice(-1)[0] || 'field'}: ${d.msg}`).join('; ');
    } else if(msg && typeof msg === 'object'){
      msg = JSON.stringify(msg);
    }
    throw new Error(msg || 'Error');
  }
  return res.json();
}

// ---------- Admin ----------
async function apiAdminStats(){ return api('/api/admin/stats'); }
async function apiAdminUsers(){ return api('/api/admin/users'); }
async function apiAdminDeleteUser(uid){ return api('/api/admin/users/'+uid, {method:'DELETE'}); }

// ---------- Profile ----------
async function apiUpdateProfile(name){ return api('/api/auth/me', {method:'PATCH', body:JSON.stringify({name})}); }

// ---------- Saved Websites ----------
async function apiSavedList(){ return api('/api/saved'); }
async function apiSavedAdd(url){ return api('/api/saved', {method:'POST', body:JSON.stringify({url})}); }
async function apiSavedRemove(id){ return api('/api/saved/'+id, {method:'DELETE'}); }