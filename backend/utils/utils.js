// ==========================================
// Toast Notification Utility
// ==========================================


// ---------- Toast notifications (replaces alerts) ----------
function toast(msg, type='info'){
  let host = document.getElementById('toast-host');
  if(!host){ host=document.createElement('div'); host.id='toast-host';
    host.style.cssText='position:fixed;top:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:10px';
    document.body.appendChild(host); }
  const colors={info:'#00B8D9',success:'#22C55E',error:'#EF4444',warn:'#FACC15'};
  const icons={info:'ℹ️',success:'✅',error:'⛔',warn:'⚠️'};
  const el=document.createElement('div');
  el.style.cssText=`display:flex;align-items:center;gap:10px;padding:14px 18px;border-radius:13px;
    background:#101B2D;color:#F8FAFC;font-size:14px;
    border:1px solid ${colors[type]}55;box-shadow:0 12px 34px rgba(2,6,15,.5),0 0 20px ${colors[type]}22;
    min-width:240px;max-width:340px;transform:translateX(120%);
    transition:transform .4s cubic-bezier(.2,.8,.2,1);font-family:Inter,sans-serif`;
  el.innerHTML=`<span style="font-size:17px">${icons[type]}</span><span>${msg}</span>`;
  host.appendChild(el);
  requestAnimationFrame(()=>el.style.transform='translateX(0)');
  setTimeout(()=>{ el.style.transform='translateX(120%)'; setTimeout(()=>el.remove(),400); },3000);
}

// ---------- Skeleton loading placeholder (shared across pages) ----------
function skeletonRows(n){
  return `<div class="card">${Array.from({length:n}).map(()=>
    `<div class="skeleton skel-line" style="width:${60+Math.random()*35}%"></div>`).join('')}</div>`;
}