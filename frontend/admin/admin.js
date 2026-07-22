// ---------- Admin ----------
async function renderAdmin(c){
  if(currentUser.role!=='admin'){ c.innerHTML='<div class="card">Access denied.</div>'; return; }
  c.innerHTML=skeletonRows(5);
  let stats={users:0,scans:0,avg_score:0,high_risk:0}, users=[];
  try{
    [stats, users] = await Promise.all([apiAdminStats(), apiAdminUsers()]);
  }catch(e){ toast('Could not load admin data: '+e.message,'error'); }
  c.innerHTML=`
    <div class="grid grid-4 mb">
      ${statCard('👥',stats.users,'Total Users')}
      ${statCard('🔍',stats.scans,'Total Scans')}
      ${statCard('📈',stats.avg_score,'Platform Avg Score')}
      ${statCard('⚠️',stats.high_risk,'High-Risk Findings')}
    </div>
    <div class="card mb"><div class="section-title">👥 Manage Users</div>
      <table class="table"><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Scans</th><th></th></tr></thead>
      <tbody>${users.map(u=>`<tr><td><b>${u.name}</b></td><td>${u.email}</td>
        <td><span class="pill ${u.role==='admin'?'pill-red':'pill-green'}">${u.role}</span></td>
        <td>${new Date(u.joined).toLocaleDateString()}</td><td>${u.scans}</td>
        <td>${u.id!==currentUser.id?`<button class="btn btn-danger btn-sm" onclick="delUser(${u.id})">Remove</button>`:'<span class="muted">You</span>'}</td>
      </tr>`).join('')}</tbody></table>
    </div>`;
}
async function delUser(id){ if(!confirm('Remove this user?'))return;
  try{ await apiAdminDeleteUser(id); toast('User removed.','info'); location.reload(); }
  catch(e){ toast('Remove failed: '+e.message,'error'); } }
