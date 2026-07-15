// ==========================================
// Toast Notification Utility
// ==========================================


// ---------- Toast notifications (replaces alerts) ----------
function toast(msg, type='info'){
  let host = document.getElementById('toast-host');
  if(!host){ host=document.createElement('div'); host.id='toast-host';
    host.style.cssText='position:fixed;top:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:10px';
    document.body.appendChild(host); }
  const colors={info:'#22e6e6',success:'#22e39a',error:'#ff5b6e',warn:'#ffcb3d'};
  const icons={info:'ℹ️',success:'✅',error:'⛔',warn:'⚠️'};
  const el=document.createElement('div');
  el.style.cssText=`display:flex;align-items:center;gap:10px;padding:14px 18px;border-radius:13px;
    background:linear-gradient(160deg,rgba(12,24,54,.96),rgba(10,19,48,.96));color:#fff;font-size:14px;
    border:1px solid ${colors[type]}55;box-shadow:0 12px 34px rgba(3,10,30,.5),0 0 20px ${colors[type]}22;
    backdrop-filter:blur(12px);min-width:240px;max-width:340px;transform:translateX(120%);
    transition:transform .4s cubic-bezier(.2,.8,.2,1);font-family:Inter,sans-serif`;
  el.innerHTML=`<span style="font-size:17px">${icons[type]}</span><span>${msg}</span>`;
  host.appendChild(el);
  requestAnimationFrame(()=>el.style.transform='translateX(0)');
  setTimeout(()=>{ el.style.transform='translateX(120%)'; setTimeout(()=>el.remove(),400); },3000);
}