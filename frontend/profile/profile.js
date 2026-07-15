// ---------- Profile ----------
function renderProfile(c){
  const myScans=DB.scans.filter(s=>s.userId===currentUser.id);
  c.innerHTML=`<div class="grid grid-2">
    <div class="card"><div class="section-title">👤 Profile</div>
      <div class="flex center gap mb"><div class="avatar" style="width:64px;height:64px;font-size:24px;border-radius:18px">${currentUser.name[0].toUpperCase()}</div>
      <div><h3>${currentUser.name}</h3><p class="muted">${currentUser.email}</p>
      <span class="pill ${currentUser.role==='admin'?'pill-red':'pill-green'}">${currentUser.role}</span></div></div>
      <div class="input-group"><label>Full Name</label><input id="pf-name" value="${currentUser.name}"></div>
      <div class="input-group"><label>Email</label><input id="pf-email" value="${currentUser.email}" disabled></div>
      <button class="btn btn-primary" onclick="saveProfile()">Save Changes</button>
    </div>
    <div class="card"><div class="section-title">📊 Your Activity</div>
      ${statLine('Member Since',currentUser.joined)}
      ${statLine('Total Scans',myScans.length)}
      ${statLine('Saved Websites',DB.saved.filter(s=>s.userId===currentUser.id).length)}
      ${statLine('Avg Score',myScans.length?Math.round(myScans.reduce((a,s)=>a+s.score,0)/myScans.length):'—')}
      <div class="divider"></div>
      <button class="btn btn-outline" onclick="if(confirm('Clear all your scan history?')){DB.scans=DB.scans.filter(s=>s.userId!==currentUser.id);navigate('profile');toast('Scan data cleared.','info')}">Clear My Scan Data</button>
    </div></div>`;
}
function statLine(k,v){ return `<div class="flex between" style="padding:12px 0;border-bottom:1px solid var(--line)"><span class="muted">${k}</span><b>${v}</b></div>`; }
function saveProfile(){ const name=document.getElementById('pf-name').value.trim();
  if(!name){ toast('Name cannot be empty.','warn'); return; }
  const users=DB.users; const u=users.find(x=>x.id===currentUser.id); u.name=name; DB.users=users;
  currentUser.name=name; localStorage.setItem('ci_session',JSON.stringify(currentUser));
  document.getElementById('user-mini-name').textContent=name;
  document.getElementById('user-avatar').textContent=name[0].toUpperCase();
  toast('Profile updated!','success'); navigate('profile'); }


// ---------- Saved ----------
function renderSaved(c){
  const saved=DB.saved.filter(s=>s.userId===currentUser.id);
  c.innerHTML=`<div class="card"><div class="section-title">⭐ Saved Websites</div>
    ${saved.length?saved.map(s=>`<div class="flex between center" style="padding:14px 0;border-bottom:1px solid var(--line)">
      <div><b>${s.url}</b><div class="muted" style="font-size:12px">Saved ${new Date(s.date).toLocaleDateString()}</div></div>
      <div class="flex gap">
      <button class="btn btn-primary btn-sm" onclick="quickScanUrl('${s.url}')">Rescan</button>
      <button class="btn btn-danger btn-sm" onclick="unsave('${s.url}')">Remove</button></div></div>`).join('')
      :'<p class="muted">No saved websites yet. Save a site from a scan result.</p>'}</div>`;
}
function quickScanUrl(url){ navigate('scanner'); setTimeout(()=>{document.getElementById('scan-url').value=url; runScan();},120); }
function unsave(url){ DB.saved=DB.saved.filter(s=>!(s.url===url&&s.userId===currentUser.id)); navigate('saved'); toast('Removed from saved.','info'); }
