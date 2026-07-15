/* ============================================================
   CyberInspect – Frontend Application Logic 
============================================================ */

// Restore session
// Session restore will be implemented later using JWT.
// ---------- Navigation ----------
document.querySelectorAll('.nav-item').forEach(item=>{
  item.addEventListener('click', ()=> navigate(item.dataset.page));
});
function navigate(page){
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active', n.dataset.page===page));
  const titles={dashboard:'Dashboard',scanner:'Website Security Scanner',history:'Scan History',
    saved:'Saved Websites',profile:'User Profile',admin:'Admin Dashboard'};
  document.getElementById('page-title').textContent=titles[page]||'';
  const c=document.getElementById('content');
  c.style.animation='none'; requestAnimationFrame(()=> c.style.animation='fadeUp .45s');
  ({dashboard:renderDashboard,scanner:renderScanner,history:renderHistory,
    saved:renderSaved,profile:renderProfile,admin:renderAdmin}[page])(c);
 




// ---------- History ----------
function renderHistory(c){
  const scans=DB.scans.filter(s=>s.userId===currentUser.id).reverse();
  c.innerHTML=`<div class="card">
    <div class="flex between center mb wrap gap">
      <div class="section-title" style="margin:0">📚 Scan History</div>
      <input type="text" id="hist-search" placeholder="Search by URL…"
        style="padding:11px 16px;border:1px solid var(--line);border-radius:12px;background:var(--glass);color:#fff;font-family:inherit"
        oninput="filterHistory()">
    </div>
    <table class="table"><thead><tr><th>Website</th><th>Date</th><th>Score</th><th>Risk</th><th>Actions</th></tr></thead>
    <tbody id="hist-body">${scans.map(histRow).join('')||'<tr><td colspan="5" class="muted">No scans yet.</td></tr>'}</tbody></table>
    ${scans.length>=2?`<div class="mt"><button class="btn btn-outline" onclick="compareLast()">🔀 Compare Last 2 Scans</button></div>`:''}
  </div>`;
}
function histRow(s){ return `<tr data-url="${s.url}">
  <td><b>${s.url}</b></td><td>${new Date(s.date).toLocaleDateString()}</td>
  <td><b style="font-family:'Sora'">${s.score}</b></td><td><span class="risk-badge risk-${s.risk.toLowerCase()}">${s.risk}</span></td>
  <td><div class="flex gap"><button class="btn btn-outline btn-sm" onclick="openReport(${s.id})">View</button>
  <button class="btn btn-danger btn-sm" onclick="deleteScan(${s.id})">Delete</button></div></td></tr>`; }
function filterHistory(){ const q=document.getElementById('hist-search').value.toLowerCase();
  document.querySelectorAll('#hist-body tr').forEach(r=>{
    r.style.display=(r.dataset.url||'').includes(q)?'':'none'; }); }
function deleteScan(id){ if(!confirm('Delete this scan?'))return;
  DB.scans=DB.scans.filter(s=>s.id!==id); navigate('history'); toast('Scan deleted.','info'); }
function compareLast(){
  const scans=DB.scans.filter(s=>s.userId===currentUser.id).slice(-2);
  const [a,b]=scans;
  const diff=b.score-a.score;
  const arrow=diff>0?'▲':diff<0?'▼':'—';
  const color=diff>0?'var(--green)':diff<0?'var(--red)':'var(--slate)';
  document.getElementById('report-modal').classList.remove('hidden');
  document.getElementById('report-body').innerHTML=`
    <h2 class="mb">🔀 Scan Comparison</h2>
    <div class="grid grid-2">
      <div class="card"><div class="section-title">Previous</div>
        <h3>${a.url}</h3><p class="muted mono" style="font-size:12px">${new Date(a.date).toLocaleString()}</p>
        <div style="font-size:40px;font-family:'Sora';font-weight:800;margin:10px 0">${a.score}</div>
        <span class="risk-badge risk-${a.risk.toLowerCase()}">${a.risk}</span></div>
      <div class="card"><div class="section-title">Latest</div>
        <h3>${b.url}</h3><p class="muted mono" style="font-size:12px">${new Date(b.date).toLocaleString()}</p>
        <div style="font-size:40px;font-family:'Sora';font-weight:800;margin:10px 0">${b.score}</div>
        <span class="risk-badge risk-${b.risk.toLowerCase()}">${b.risk}</span></div>
    </div>
    <div class="card mt" style="text-align:center">
      <div class="section-title" style="justify-content:center">Change</div>
      <div style="font-size:36px;font-family:'Sora';font-weight:800;color:${color}">${arrow} ${Math.abs(diff)} pts</div>
    </div>`;
}

}