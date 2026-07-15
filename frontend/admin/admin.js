// ---------- Admin ----------
function renderAdmin(c){
  if(currentUser.role!=='admin'){ c.innerHTML='<div class="card">Access denied.</div>'; return; }
  const users=DB.users, scans=DB.scans;
  const avg=scans.length?Math.round(scans.reduce((a,s)=>a+s.score,0)/scans.length):0;
  c.innerHTML=`
    <div class="grid grid-4 mb">
      ${statCard('👥',users.length,'Total Users')}
      ${statCard('🔍',scans.length,'Total Scans')}
      ${statCard('📈',avg,'Platform Avg Score')}
      ${statCard('⚠️',scans.filter(s=>['Critical','High'].includes(s.risk)).length,'High-Risk Findings')}
    </div>
    <div class="card mb"><div class="section-title">👥 Manage Users</div>
      <table class="table"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Scans</th><th></th></tr></thead>
      <tbody>${users.map(u=>`<tr><td><b>${u.name}</b></td><td>${u.email}</td>
        <td><span class="pill ${u.role==='admin'?'pill-red':'pill-green'}">${u.role}</span></td>
        <td>${u.joined}</td><td>${scans.filter(s=>s.userId===u.id).length}</td>
        <td>${u.id!==currentUser.id?`<button class="btn btn-danger btn-sm" onclick="delUser(${u.id})">Remove</button>`:'<span class="muted">You</span>'}</td>
      </tr>`).join('')}</tbody></table>
    </div>
    <div class="card"><div class="section-title">📋 System Activity Log</div>
      <table class="table"><thead><tr><th>Time</th><th>User</th><th>Website</th><th>Score</th></tr></thead>
      <tbody>${scans.slice(-10).reverse().map(s=>{const u=users.find(x=>x.id===s.userId);
        return `<tr><td>${new Date(s.date).toLocaleString()}</td><td>${u?u.name:'—'}</td>
        <td>${s.url}</td><td><b style="font-family:'Sora'">${s.score}</b></td></tr>`;}).join('')||'<tr><td colspan="4" class="muted">No activity.</td></tr>'}</tbody></table>
    </div>`;
}
function delUser(id){ if(!confirm('Remove this user?'))return;
  DB.users=DB.users.filter(u=>u.id!==id); navigate('admin'); toast('User removed.','info'); }