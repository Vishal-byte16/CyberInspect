// ---------- Profile ----------
async function renderProfile(c){
  c.innerHTML=skeletonRows(3);
  let myScans=[], saved=[];
  try{ [myScans, saved] = await Promise.all([apiHistory(), apiSavedList()]); }
  catch(e){ toast('Could not load profile: '+e.message,'error'); }
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
      ${statLine('Member Since',new Date(currentUser.created_at).toLocaleDateString())}
      ${statLine('Total Scans',myScans.length)}
      ${statLine('Saved Websites',saved.length)}
      ${statLine('Avg Score',(()=>{const s=myScans.filter(x=>x.risk!=='Incomplete');return s.length?Math.round(s.reduce((a,x)=>a+x.score,0)/s.length):'—';})())}
    </div></div>`;
}
function statLine(k,v){ return `<div class="flex between" style="padding:12px 0;border-bottom:1px solid var(--line)"><span class="muted">${k}</span><b>${v}</b></div>`; }
async function saveProfile(){
  const name=document.getElementById('pf-name').value.trim();
  if(!name){ toast('Name cannot be empty.','warn'); return; }
  try{
    const updated = await apiUpdateProfile(name);
    currentUser.name = updated.name;
    document.getElementById('user-mini-name').textContent=updated.name;
    document.getElementById('user-avatar').textContent=updated.name[0].toUpperCase();
    toast('Profile updated!','success'); location.reload();
  }catch(e){ toast('Update failed: '+e.message,'error'); }
}

// ---------- Saved ----------
async function renderSaved(c){
  c.innerHTML=skeletonRows(3);
  let saved=[];
  try{ saved = await apiSavedList(); }catch(e){ toast('Could not load saved sites: '+e.message,'error'); }
  c.innerHTML=`<div class="card"><div class="section-title">⭐ Saved Websites</div>
    ${saved.length?saved.map(s=>`<div class="flex between center" style="padding:14px 0;border-bottom:1px solid var(--line)">
      <div><b>${s.url}</b><div class="muted" style="font-size:12px">Saved ${new Date(s.date).toLocaleDateString()}</div></div>
      <div class="flex gap">
      <button class="btn btn-primary btn-sm" onclick="quickScanUrl('${s.url}')">Rescan</button>
      <button class="btn btn-danger btn-sm" onclick="unsave(${s.id})">Remove</button></div></div>`).join('')
      :'<p class="muted">No saved websites yet. Save a site from a scan result.</p>'}</div>`;
}
function quickScanUrl(url){ location.href = 'scanner.html?url=' + encodeURIComponent(url); }
async function unsave(id){
  try{ await apiSavedRemove(id); toast('Removed from saved.','info'); location.reload(); }
  catch(e){ toast('Remove failed: '+e.message,'error'); }
}
