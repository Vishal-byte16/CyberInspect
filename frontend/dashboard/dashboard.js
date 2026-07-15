// ---------- Dashboard ----------
function renderDashboard(c){
  const myScans=DB.scans.filter(s=>s.userId===currentUser.id);
  const avg = myScans.length? Math.round(myScans.reduce((a,s)=>a+s.score,0)/myScans.length):0;
  const critical=myScans.filter(s=>['Critical','High'].includes(s.risk)).length;
  c.innerHTML=`
    <div class="grid grid-4 mb">
      ${statCard('🔍',myScans.length,'Total Scans')}
      ${statCard('📈',avg||'—','Avg Security Score')}
      ${statCard('⚠️',critical,'High-Risk Sites')}
      ${statCard('⭐',DB.saved.filter(s=>s.userId===currentUser.id).length,'Saved Websites')}
    </div>
    <div class="grid grid-2">
      <div class="card">
        <div class="section-title">🕒 Recent Scans</div>
        ${myScans.slice(-5).reverse().map(s=>`
          <div class="flex between center" style="padding:12px 0;border-bottom:1px solid var(--line)">
            <div><b>${s.url}</b><div class="muted" style="font-size:12px">${new Date(s.date).toLocaleString()}</div></div>
            <div class="flex center gap">
              <span class="risk-badge risk-${s.risk.toLowerCase()}">${s.risk}</span>
              <b style="font-family:'Sora'">${s.score}</b>
              <button class="btn btn-outline btn-sm" onclick="openReport(${s.id})">View</button>
            </div>
          </div>`).join('') || '<p class="muted">No scans yet. Start scanning a website!</p>'}
        <button class="btn btn-primary mt" onclick="navigate('scanner')">+ New Scan</button>
      </div>
      <div class="card">
        <div class="section-title">🛡️ Security Overview</div>
        ${myScans.length?scoreDistribution(myScans):'<p class="muted">Run scans to see your security distribution.</p>'}
        <div class="divider"></div>
        <p class="muted" style="font-size:13px">💡 <b>Tip:</b> Scan only websites you own or are authorized to assess.
        Results reflect observable technical indicators only.</p>
      </div>
    </div>`;
  setTimeout(()=>document.querySelectorAll('.bar-fill').forEach(b=>b.style.width=b.dataset.w+'%'),120);
}
function statCard(icon,val,label){ return `<div class="card stat-card">
  <div class="stat-icon">${icon}</div><div class="stat-val">${val}</div><div class="stat-label">${label}</div></div>`; }
function scoreDistribution(scans){
  const buckets={Excellent:0,Low:0,Medium:0,High:0,Critical:0};
  scans.forEach(s=>buckets[s.risk]++);
  const total=scans.length;
  return Object.entries(buckets).map(([k,v])=>`
    <div style="margin:10px 0">
      <div class="flex between" style="font-size:13px;margin-bottom:6px"><span>${k}</span><span class="muted">${v}</span></div>
      <div class="bar-track"><div class="bar-fill" style="width:0%" data-w="${total?v/total*100:0}"></div></div>
    </div>`).join('');
}