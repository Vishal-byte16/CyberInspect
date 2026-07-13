// ---------- API Layer (replaces mockScan + localStorage) ----------
const API = "http://127.0.0.1:8000";
function token(){ return localStorage.getItem('ci_token'); }
async function api(path, opts={}){
  const res = await fetch(API+path, {
    ...opts,
    headers: {'Content-Type':'application/json',
      ...(token()?{'Authorization':'Bearer '+token()}:{}), ...(opts.headers||{})}
  });
  if(!res.ok){ const e=await res.json().catch(()=>({detail:'Error'})); throw new Error(e.detail); }
  return res.json();
}