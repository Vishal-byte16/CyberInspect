/* ============================================================
   CyberInspect – Frontend Application Logic 
============================================================ */

// ---------- State & Storage ----------
const DB = {
  get users() { return JSON.parse(localStorage.getItem('ci_users') || '[]'); },
  set users(v) { localStorage.setItem('ci_users', JSON.stringify(v)); },
  get scans() { return JSON.parse(localStorage.getItem('ci_scans') || '[]'); },
  set scans(v) { localStorage.setItem('ci_scans', JSON.stringify(v)); },
  get saved() { return JSON.parse(localStorage.getItem('ci_saved') || '[]'); },
  set saved(v) { localStorage.setItem('ci_saved', JSON.stringify(v)); },
};
let currentUser = null;

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

// Login
async function apiLogin(email, password){
  const body = new URLSearchParams({username:email, password});
  const res = await fetch(API+'/api/auth/login', {method:'POST',
    headers:{'Content-Type':'application/x-www-form-urlencoded'}, body});
  if(!res.ok) throw new Error('Invalid credentials');
  const data = await res.json();
  localStorage.setItem('ci_token', data.access_token);
  return data.user;
}
// Register
async function apiRegister(name,email,password){
  const data = await api('/api/auth/register',{method:'POST',
    body:JSON.stringify({name,email,password})});
  localStorage.setItem('ci_token', data.access_token);
  return data.user;

}
// Scan
async function apiScan(url){ return api('/api/scan',{method:'POST',body:JSON.stringify({url})}); }
async function apiHistory(){ return api('/api/scan/history'); }
async function apiGetScan(id){ return api('/api/scan/'+id); }
async function apiDeleteScan(id){ return api('/api/scan/'+id,{method:'DELETE'}); }
// Reports
function reportPdfUrl(id){ return `${API}/api/reports/${id}/pdf`; }
function reportHtmlUrl(id){ return `${API}/api/reports/${id}/html`; }

// Seed default accounts
(function seed() {
  if (!DB.users.length) {
    DB.users = [
      { id:1, name:'Admin', email:'admin@cyberinspect.io', password:'admin', role:'admin', joined:'2024-01-10' },
      { id:2, name:'Demo Analyst', email:'user@demo.io', password:'demo', role:'analyst', joined:'2024-03-22' },
    ];
  }
})();

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

// ---------- Auth ----------
function showRegister(){ document.getElementById('login-form').classList.remove('active');
  document.getElementById('register-form').classList.add('active'); }
function showLogin(){ document.getElementById('register-form').classList.remove('active');
  document.getElementById('login-form').classList.add('active'); }

document.getElementById('login-form').addEventListener('submit', async (e) => {

    e.preventDefault();

    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    try {

        currentUser = await apiLogin(email, password);

        toast('Login successful!', 'success');

        enterApp();

    } catch (err) {

        toast(err.message, 'error');

    }

});

document.getElementById('register-form').addEventListener('submit', async (e) => {

    e.preventDefault();

    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim().toLowerCase();
    const password = document.getElementById('reg-password').value;

    if (password.length < 8) {
        toast('Password must be at least 8 characters.', 'warn');
        return;
    }

    try {

        currentUser = await apiRegister(name, email, password);

        toast('Account created successfully!', 'success');

        enterApp();

    } catch (err) {

        toast(err.message, 'error');

    }

});
function logout() {

    localStorage.removeItem('ci_token');

    currentUser = null;

    document.getElementById('app').classList.add('hidden');

    document.getElementById('auth-screen').classList.remove('hidden');

    toast("Logged out successfully.", "info");

}
function enterApp(){
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
  document.getElementById('user-avatar').textContent = currentUser.name[0].toUpperCase();
  document.getElementById('user-mini-name').textContent = currentUser.name;
  document.getElementById('user-mini-role').textContent = currentUser.role==='admin'?'Administrator':'Security Analyst';
  document.querySelectorAll('.admin-only').forEach(el=> el.style.display = currentUser.role==='admin'?'flex':'none');
  navigate('dashboard');
}

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
}

// ---------- MOCK SCAN ENGINE (replace with API later) ----------
function mockScan(url){
  const host = url.replace(/^https?:\/\//,'').split('/')[0];
  const rand=(a,b)=>Math.floor(Math.random()*(b-a+1))+a;
  const yesNo=p=>Math.random()<p;

  // SSL/TLS
  const https = yesNo(0.9);
  const daysToExpiry = rand(-5,400);
  const ssl = {
    https, valid: https && daysToExpiry>0,
    issuer: pick(["Let's Encrypt R3","DigiCert Global G2","Google Trust Services","Sectigo RSA"]),
    expires: dateFromNow(daysToExpiry), daysToExpiry,
    chainComplete: yesNo(0.85),
    tls: ['TLS 1.2','TLS 1.3'].filter(()=>yesNo(0.8)).concat(yesNo(0.3)?['TLS 1.1 (deprecated)']:[])
  };
  if(!ssl.tls.length) ssl.tls=['TLS 1.2'];

  // Headers
  const hdrs=['Content-Security-Policy','Strict-Transport-Security','X-Frame-Options',
    'X-Content-Type-Options','Referrer-Policy','Permissions-Policy'];
  const headers = hdrs.map(h=>({name:h, present:yesNo(0.55)}));

  // Domain
  const domain={ age:rand(1,20)+' years', registrar:pick(['GoDaddy','Namecheap','Cloudflare Inc.','Google Domains']),
    expires:dateFromNow(rand(30,700)), ip:`${rand(1,220)}.${rand(0,255)}.${rand(0,255)}.${rand(1,254)}`,
    host:pick(['Cloudflare','AWS','Google Cloud','DigitalOcean','Azure']) };

  // DNS
  const dns={ A:domain.ip, AAAA: yesNo(0.5)?'2606:4700:'+rand(1000,9999):'—',
    MX: yesNo(0.7)?`mail.${host}`:'—', NS:`ns1.${domain.host.toLowerCase()}.com`,
    TXT: yesNo(0.6)?'v=spf1 include:_spf.google.com ~all':'—',
    CNAME: yesNo(0.4)?`cdn.${host}`:'—',
    SPF: yesNo(0.7), DMARC: yesNo(0.5), DKIM: yesNo(0.4) };

  // Reputation
  const rep={ blacklisted:yesNo(0.08), phishing:yesNo(0.05), malware:yesNo(0.04) };
  rep.summary = (!rep.blacklisted&&!rep.phishing&&!rep.malware)?'Clean – no threats detected':'Potential threat indicators found';

  // Cookies
  const cookies={ secure:yesNo(0.6), httpOnly:yesNo(0.65), sameSite:yesNo(0.55), count:rand(1,8) };

  // HTTP
  const http={ status: pick([200,200,200,301,403]), redirects: yesNo(0.4)?['http → https','www → non-www']:['none'],
    server: yesNo(0.5)?pick(['nginx','Apache','cloudflare','LiteSpeed']):'Hidden (good)' };

  // Tech
  const tech={ server:pick(['Nginx','Apache','LiteSpeed']), cms:pick(['WordPress','None','Drupal','Custom']),
    js:['React','Vue','jQuery','Next.js'].filter(()=>yesNo(0.4)),
    cdn:pick(['Cloudflare','Akamai','Fastly','None']), proxy:yesNo(0.5)?'Cloudflare':'None' };
  if(!tech.js.length) tech.js=['Vanilla JS'];

  // ---- SCORING ENGINE ----
  let score=0;
  score += (ssl.valid?25:0) - (ssl.tls.some(t=>t.includes('deprecated'))?6:0);
  score += headers.filter(h=>h.present).length/6*20;
  score += (dns.SPF?4:0)+(dns.DMARC?4:0)+(dns.DKIM?2:0);
  score += (cookies.secure?4:0)+(cookies.httpOnly?4:0)+(cookies.sameSite?4:0);
  score += (rep.blacklisted||rep.phishing||rep.malware)?0:15;
  score += (tech.cdn!=='None'?4:0)+(http.server==='Hidden (good)'?4:2);
  score = Math.max(0,Math.min(100,Math.round(score)));

  const risk = score>=90?'Excellent':score>=75?'Low':score>=60?'Medium':score>=40?'High':'Critical';

  return { id:Date.now(), url:host, fullUrl:url, date:new Date().toISOString(),
    userId:currentUser.id, score, risk, ssl, headers, domain, dns, rep, cookies, http, tech };
}
function pick(a){ return a[Math.floor(Math.random()*a.length)]; }
function dateFromNow(days){ const d=new Date(); d.setDate(d.getDate()+days); return d.toISOString().slice(0,10); }

// ---------- Quick scan from topbar ----------
function quickScan(){
  const url=document.getElementById('quick-scan-url').value.trim();
  if(!url) return; navigate('scanner');
  setTimeout(()=>{ document.getElementById('scan-url').value=url; runScan(); },120);
}

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

// ---------- Scanner ----------
function renderScanner(c){
  c.innerHTML=`
    <div class="scan-hero">
      <h1>🌐 Website Security Scanner</h1>
      <p>Enter a URL to run a comprehensive, non-intrusive security assessment.</p>
      <div class="scan-input-row">
        <input type="text" id="scan-url" placeholder="https://example.com" onkeydown="if(event.key==='Enter')runScan()">
        <button class="btn btn-primary" onclick="runScan()">🔍 Scan Now</button>
      </div>
      <div class="scan-checkbox-row">
        ${['SSL/TLS','Headers','DNS','Domain','Reputation','Cookies','HTTP','Technology']
          .map(x=>`<label><input type="checkbox" checked> ${x}</label>`).join('')}
      </div>
    </div>
    <div id="scan-output"></div>`;
}

function runScan(){
  const raw=document.getElementById('scan-url').value.trim();
  if(!raw){ toast('Please enter a URL.','warn'); return; }
  let url=raw; if(!/^https?:\/\//.test(url)) url='https://'+url;
  try{ new URL(url); }catch{ toast('Invalid URL format.','error'); return; }

  const out=document.getElementById('scan-output');
  const steps=['Validating URL','Analyzing SSL/TLS','Checking Security Headers','Resolving DNS Records',
    'Fetching Domain Info','Checking Reputation','Inspecting Cookies','Analyzing HTTP','Detecting Technologies','Calculating Score'];
  out.innerHTML=`<div class="card scan-progress"><div class="spinner"></div>
    <h3>Scanning ${url}…</h3><div class="scan-steps">${steps.map((s,i)=>
    `<div class="scan-step" id="step-${i}">⏳ ${s}</div>`).join('')}</div></div>`;

  let i=0;
  const iv=setInterval(()=>{
    if(i>0){ const p=document.getElementById('step-'+(i-1)); p.classList.remove('active'); p.classList.add('done'); p.innerHTML='✅ '+steps[i-1]; }
    if(i<steps.length){ const el=document.getElementById('step-'+i); el.classList.add('active'); i++; }
    else{ clearInterval(iv); finishScan(url); }
  },260);
}

async function finishScan(url) {

    try {

        const result = await apiScan(url);

        renderResult(result, document.getElementById('scan-output'));

        toast(
            `Scan complete — Score ${result.score}/100 (${result.risk})`,
            result.score >= 75
                ? "success"
                : result.score >= 40
                ? "warn"
                : "error"
        );

    } catch (err) {

        toast(err.message, "error");

    }

}

// ---------- Result Rendering ----------
function renderResult(r, container){
  container.innerHTML=`
    <div class="card mb">
      <div class="flex between center wrap gap">
        <div class="score-hero">
          ${scoreRing(r.score)}
          <div>
            <h2>${r.url}</h2>
            <p class="muted mono">${r.fullUrl}</p>
            <div class="mt"><span class="risk-badge risk-${r.risk.toLowerCase()}">Risk: ${r.risk}</span></div>
            <p class="muted mt" style="font-size:12px">Scanned ${new Date(r.date).toLocaleString()}</p>
          </div>
        </div>
        <div class="flex gap wrap">
          <button class="btn btn-outline btn-sm" onclick="saveWebsite('${r.url}')">⭐ Save</button>
          <button class="btn btn-outline btn-sm" onclick="downloadHTML(${r.id})">📄 HTML</button>
          <button class="btn btn-primary btn-sm" onclick="downloadPDF(${r.id})">📑 PDF</button>
        </div>
      </div>
    </div>

    ${section('🔒 SSL/TLS Analysis',[
      finding(r.ssl.https,'HTTPS Available',r.ssl.https?'Site served over HTTPS':'No HTTPS – data unencrypted'),
      finding(r.ssl.valid,'Certificate Valid',`Expires ${r.ssl.expires} (${r.ssl.daysToExpiry} days)`),
      findingInfo('Certificate Issuer',r.ssl.issuer),
      finding(r.ssl.chainComplete,'Certificate Chain','Complete chain of trust'),
      findingInfo('Supported TLS',r.ssl.tls.map(t=>`<span class="tag">${t}</span>`).join('')),
    ])}

    ${section('🛡️ Security Headers',
      r.headers.map(h=>finding(h.present,h.name,h.present?'Header present':'Missing – recommended to add')))}

    ${section('🌍 Domain Information',[
      findingInfo('Domain Age',r.domain.age),
      findingInfo('Registrar',r.domain.registrar),
      findingInfo('Domain Expires',r.domain.expires),
      findingInfo('IP Address',r.domain.ip),
      findingInfo('Hosting Provider',r.domain.host),
    ])}

    ${section('🌐 DNS Analysis',[
      findingInfo('A Record',r.dns.A), findingInfo('AAAA Record',r.dns.AAAA),
      findingInfo('MX Record',r.dns.MX), findingInfo('NS Record',r.dns.NS),
      findingInfo('TXT Record',r.dns.TXT), findingInfo('CNAME',r.dns.CNAME),
      finding(r.dns.SPF,'SPF Record',r.dns.SPF?'SPF configured':'No SPF – email spoofing risk'),
      finding(r.dns.DMARC,'DMARC Record',r.dns.DMARC?'DMARC configured':'No DMARC policy'),
      finding(r.dns.DKIM,'DKIM','DKIM signing '+(r.dns.DKIM?'detected':'not detected')),
    ])}

    ${section('🚨 Website Reputation',[
      finding(!r.rep.blacklisted,'Blacklist Status',r.rep.blacklisted?'Listed on blacklist':'Not blacklisted'),
      finding(!r.rep.phishing,'Phishing Reports',r.rep.phishing?'Phishing reports found':'No phishing reports'),
      finding(!r.rep.malware,'Malware Reports',r.rep.malware?'Malware reports found':'No malware reports'),
      findingInfo('Summary',r.rep.summary),
    ])}

    ${section('🍪 Cookie Security',[
      finding(r.cookies.secure,'Secure Flag',r.cookies.secure?'Cookies use Secure':'Missing Secure flag'),
      finding(r.cookies.httpOnly,'HttpOnly Flag',r.cookies.httpOnly?'Cookies use HttpOnly':'Missing HttpOnly flag'),
      finding(r.cookies.sameSite,'SameSite Flag',r.cookies.sameSite?'SameSite configured':'Missing SameSite'),
      findingInfo('Cookies Detected',r.cookies.count),
    ])}

    ${section('📡 HTTP Analysis',[
      findingInfo('Status Code',r.http.status),
      findingInfo('Redirect Chain',r.http.redirects.join(' → ')),
      finding(r.http.server==='Hidden (good)','Server Disclosure',r.http.server==='Hidden (good)'?'Server header hidden':'Server: '+r.http.server),
    ])}

    ${section('🔍 Technology Detection',[
      findingInfo('Web Server',r.tech.server),
      findingInfo('CMS',r.tech.cms),
      findingInfo('JS Frameworks',r.tech.js.map(t=>`<span class="tag">${t}</span>`).join('')),
      findingInfo('CDN',r.tech.cdn),
      findingInfo('Reverse Proxy',r.tech.proxy),
    ])}`;

  animateScore(r.score);
  container.scrollIntoView({behavior:'smooth'});
}

function scoreRing(score){
  const color = score>=90?'#22e6e6':score>=75?'#22e39a':score>=60?'#ffcb3d':score>=40?'#ff9f45':'#ff5b6e';
  const r=68, circ=2*Math.PI*r;
  const uid='sg'+Math.floor(Math.random()*100000);
  return `<div class="score-ring"><svg width="160" height="160">
    <defs><linearGradient id="${uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${color}"/><stop offset="100%" stop-color="#00c2d4"/></linearGradient></defs>
    <circle cx="80" cy="80" r="${r}" stroke="rgba(255,255,255,.08)" stroke-width="12" fill="none"/>
    <circle cx="80" cy="80" r="${r}" stroke="url(#${uid})" stroke-width="12" fill="none"
      stroke-dasharray="${circ}" stroke-dashoffset="${circ}" stroke-linecap="round"
      style="transition:stroke-dashoffset 1.4s cubic-bezier(.2,.8,.2,1)" class="ring-anim"/>
    </svg><div class="score-num"><b style="color:${color}">0</b><small>/ 100</small></div></div>`;
}

// Animate ring stroke + count-up number
function animateScore(target){
  const ring=document.querySelector('.ring-anim');
  const numEl=document.querySelector('.score-num b');
  if(ring){ const r=68,circ=2*Math.PI*r;
    setTimeout(()=>ring.style.strokeDashoffset=circ-(target/100)*circ,60); }
  if(numEl){ let n=0; const step=Math.max(1,Math.round(target/40));
    const iv=setInterval(()=>{ n+=step; if(n>=target){n=target;clearInterval(iv);} numEl.textContent=n; },20); }
}

function section(title, findings){
  return `<div class="card result-section">
    <div class="result-head" onclick="this.nextElementSibling.classList.toggle('hidden');this.querySelector('span').style.transform=this.nextElementSibling.classList.contains('hidden')?'rotate(-90deg)':'rotate(0)'">
      <h3>${title}</h3><span>▾</span></div>
    <div class="result-body">${findings.join('')}</div></div>`;
}
function finding(ok,title,detail){
  return `<div class="finding ${ok?'pass':'fail'}"><span class="finding-icon">${ok?'✅':'❌'}</span>
    <div><b>${title}</b><div class="finding-detail">${detail}</div></div></div>`;
}
function findingInfo(title,detail){
  return `<div class="finding info"><span class="finding-icon">ℹ️</span>
    <div><b>${title}</b><div class="finding-detail">${detail}</div></div></div>`;
}

// ---------- Save website ----------
function saveWebsite(url){
  const saved=DB.saved;
  if(saved.find(s=>s.url===url&&s.userId===currentUser.id)){ toast('Already saved.','warn'); return; }
  saved.push({url,userId:currentUser.id,date:new Date().toISOString()}); DB.saved=saved;
  toast('Website saved!','success');
}

// ---------- Report Modal ----------
function openReport(id){
  const r=DB.scans.find(s=>s.id===id); if(!r) return;
  document.getElementById('report-modal').classList.remove('hidden');
  renderResult(r, document.getElementById('report-body'));
}
function closeReport(){ document.getElementById('report-modal').classList.add('hidden'); }

// ---------- Report Export ----------
function reportHTML(r){
  return `<html><head><meta charset="utf-8"><title>CyberInspect Report – ${r.url}</title>
    <style>
      body{font-family:'Segoe UI',Arial,sans-serif;padding:40px;color:#0a1330;background:#f4f8fb;max-width:900px;margin:auto}
      h1{color:#00a3b5}h2{margin-top:26px;color:#0d1f4c}
      .head{display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #22e6e6;padding-bottom:16px}
      .badge{padding:6px 16px;border-radius:20px;background:#e0fafa;color:#008a99;font-weight:700}
      .score{font-size:44px;font-weight:800;color:#0d1f4c}
      table{border-collapse:collapse;width:100%;margin:10px 0;background:#fff;border-radius:8px;overflow:hidden}
      td,th{border-bottom:1px solid #e4ebf5;padding:11px 14px;text-align:left;font-size:14px}
      th{background:#0d1f4c;color:#fff}
      .ok{color:#16a34a;font-weight:600}.bad{color:#dc2626;font-weight:600}
      .foot{margin-top:30px;font-size:12px;color:#8a9bc4;border-top:1px solid #e4ebf5;padding-top:14px}
    </style></head><body>
    <div class="head"><h1>🛡️ CyberInspect Security Report</h1>
      <div style="text-align:right"><div class="score">${r.score}<span style="font-size:18px;color:#8a9bc4">/100</span></div>
      <span class="badge">${r.risk} Risk</span></div></div>
    <p><b>Website:</b> ${r.fullUrl}<br><b>Scanned:</b> ${new Date(r.date).toLocaleString()}</p>

    <h2>🔒 SSL/TLS</h2><table>
      <tr><td>HTTPS Available</td><td class="${r.ssl.https?'ok':'bad'}">${r.ssl.https?'Yes':'No'}</td></tr>
      <tr><td>Certificate Valid</td><td class="${r.ssl.valid?'ok':'bad'}">${r.ssl.valid?'Yes':'No'}</td></tr>
      <tr><td>Issuer</td><td>${r.ssl.issuer}</td></tr>
      <tr><td>Expires</td><td>${r.ssl.expires} (${r.ssl.daysToExpiry} days)</td></tr>
      <tr><td>TLS Versions</td><td>${r.ssl.tls.join(', ')}</td></tr></table>

    <h2>🛡️ Security Headers</h2><table>${r.headers.map(h=>`<tr><td>${h.name}</td>
      <td class="${h.present?'ok':'bad'}">${h.present?'Present':'Missing'}</td></tr>`).join('')}</table>

    <h2>🌍 Domain</h2><table>
      <tr><td>Registrar</td><td>${r.domain.registrar}</td></tr>
      <tr><td>Domain Age</td><td>${r.domain.age}</td></tr>
      <tr><td>Expires</td><td>${r.domain.expires}</td></tr>
      <tr><td>IP Address</td><td>${r.domain.ip}</td></tr>
      <tr><td>Hosting</td><td>${r.domain.host}</td></tr></table>

    <h2>🌐 DNS</h2><table>
      <tr><td>A</td><td>${r.dns.A}</td></tr><tr><td>AAAA</td><td>${r.dns.AAAA}</td></tr>
      <tr><td>MX</td><td>${r.dns.MX}</td></tr><tr><td>NS</td><td>${r.dns.NS}</td></tr>
      <tr><td>SPF</td><td class="${r.dns.SPF?'ok':'bad'}">${r.dns.SPF?'Configured':'Missing'}</td></tr>
      <tr><td>DMARC</td><td class="${r.dns.DMARC?'ok':'bad'}">${r.dns.DMARC?'Configured':'Missing'}</td></tr>
      <tr><td>DKIM</td><td class="${r.dns.DKIM?'ok':'bad'}">${r.dns.DKIM?'Detected':'Not detected'}</td></tr></table>

    <h2>🚨 Reputation</h2><table>
      <tr><td>Blacklist</td><td class="${r.rep.blacklisted?'bad':'ok'}">${r.rep.blacklisted?'Listed':'Clean'}</td></tr>
      <tr><td>Phishing</td><td class="${r.rep.phishing?'bad':'ok'}">${r.rep.phishing?'Reported':'None'}</td></tr>
      <tr><td>Malware</td><td class="${r.rep.malware?'bad':'ok'}">${r.rep.malware?'Reported':'None'}</td></tr>
      <tr><td>Summary</td><td>${r.rep.summary}</td></tr></table>

    <h2>🍪 Cookies</h2><table>
      <tr><td>Secure</td><td class="${r.cookies.secure?'ok':'bad'}">${r.cookies.secure?'Yes':'No'}</td></tr>
      <tr><td>HttpOnly</td><td class="${r.cookies.httpOnly?'ok':'bad'}">${r.cookies.httpOnly?'Yes':'No'}</td></tr>
      <tr><td>SameSite</td><td class="${r.cookies.sameSite?'ok':'bad'}">${r.cookies.sameSite?'Yes':'No'}</td></tr></table>

    <h2>🔍 Technology</h2><table>
      <tr><td>Web Server</td><td>${r.tech.server}</td></tr>
      <tr><td>CMS</td><td>${r.tech.cms}</td></tr>
      <tr><td>JS Frameworks</td><td>${r.tech.js.join(', ')}</td></tr>
      <tr><td>CDN</td><td>${r.tech.cdn}</td></tr>
      <tr><td>Reverse Proxy</td><td>${r.tech.proxy}</td></tr></table>

    <div class="foot">Generated by CyberInspect on ${new Date().toLocaleString()}.
    Assessment based on observable technical indicators only and does not guarantee complete safety.
    Scan only websites you own or are authorized to assess.</div>
    </body></html>`;
}
function downloadHTML(id){
  const r=DB.scans.find(s=>s.id===id);
  const blob=new Blob([reportHTML(r)],{type:'text/html'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download=`CyberInspect_${r.url}_${Date.now()}.html`; a.click();
  toast('HTML report downloaded.','success');
}
function downloadPDF(id){
  const r=DB.scans.find(s=>s.id===id);
  const w=window.open('','_blank');
  w.document.write(reportHTML(r));
  w.document.close(); setTimeout(()=>w.print(),450);
  toast('Opening print dialog — choose "Save as PDF".','info');
}

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