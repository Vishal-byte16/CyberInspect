// ================================
// Scanner API
// ================================

async function apiScan(url) {
    return api('/api/scan', {
        method: 'POST',
        body: JSON.stringify({ url })
    });
}

async function apiHistory() {
    return api('/api/scan/history');
}

async function apiGetScan(id) {
    return api('/api/scan/' + id);
}

async function apiDeleteScan(id) {
    return api('/api/scan/' + id, {
        method: 'DELETE'
    });
}


// ================================
// Helper Functions
// ================================

function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function dateFromNow(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().slice(0, 10);
}


// ================================
// Mock Scan Engine
// Replace with backend scanner later
// ================================

function mockScan(url) {

    const host = url.replace(/^https?:\/\//, '').split('/')[0];

    const rand = (a, b) =>
        Math.floor(Math.random() * (b - a + 1)) + a;

    const yesNo = p =>
        Math.random() < p;

    // ================================
    // SSL / TLS
    // ================================

    const https = yesNo(0.9);
    const daysToExpiry = rand(-5, 400);

    const ssl = {
        https,
        valid: https && daysToExpiry > 0,
        issuer: pick([
            "Let's Encrypt R3",
            "DigiCert Global G2",
            "Google Trust Services",
            "Sectigo RSA"
        ]),
        expires: dateFromNow(daysToExpiry),
        daysToExpiry,
        chainComplete: yesNo(0.85),
        tls: ['TLS 1.2', 'TLS 1.3']
            .filter(() => yesNo(0.8))
            .concat(
                yesNo(0.3)
                    ? ['TLS 1.1 (deprecated)']
                    : []
            )
    };

    if (!ssl.tls.length) {
        ssl.tls = ['TLS 1.2'];
    }

    // ================================
    // Security Headers
    // ================================

    const hdrs = [
        'Content-Security-Policy',
        'Strict-Transport-Security',
        'X-Frame-Options',
        'X-Content-Type-Options',
        'Referrer-Policy',
        'Permissions-Policy'
    ];

    const headers = hdrs.map(h => ({
        name: h,
        present: yesNo(0.55)
    }));

    // ================================
    // Domain
    // ================================

    const domain = {
        age: rand(1, 20) + ' years',
        registrar: pick([
            'GoDaddy',
            'Namecheap',
            'Cloudflare Inc.',
            'Google Domains'
        ]),
        expires: dateFromNow(rand(30, 700)),
        ip: `${rand(1,220)}.${rand(0,255)}.${rand(0,255)}.${rand(1,254)}`,
        host: pick([
            'Cloudflare',
            'AWS',
            'Google Cloud',
            'DigitalOcean',
            'Azure'
        ])
    };

    // ================================
    // DNS
    // ================================

    const dns = {
        A: domain.ip,
        AAAA: yesNo(0.5)
            ? '2606:4700:' + rand(1000,9999)
            : '—',
        MX: yesNo(0.7)
            ? `mail.${host}`
            : '—',
        NS: `ns1.${domain.host.toLowerCase()}.com`,
        TXT: yesNo(0.6)
            ? 'v=spf1 include:_spf.google.com ~all'
            : '—',
        CNAME: yesNo(0.4)
            ? `cdn.${host}`
            : '—',
        SPF: yesNo(0.7),
        DMARC: yesNo(0.5),
        DKIM: yesNo(0.4)
    };

    // ================================
    // Reputation
    // ================================

    const rep = {
        blacklisted: yesNo(0.08),
        phishing: yesNo(0.05),
        malware: yesNo(0.04)
    };

    rep.summary =
        (!rep.blacklisted && !rep.phishing && !rep.malware)
            ? 'Clean – no threats detected'
            : 'Potential threat indicators found';

    // ================================
    // Cookies
    // ================================

    const cookies = {
        secure: yesNo(0.6),
        httpOnly: yesNo(0.65),
        sameSite: yesNo(0.55),
        count: rand(1, 8)
    };

    // ================================
    // HTTP
    // ================================

    const http = {
        status: pick([200, 200, 200, 301, 403]),
        redirects: yesNo(0.4)
            ? ['http → https', 'www → non-www']
            : ['none'],
        server: yesNo(0.5)
            ? pick(['nginx', 'Apache', 'cloudflare', 'LiteSpeed'])
            : 'Hidden (good)'
    };

    // ================================
    // Technologies
    // ================================

    const tech = {
        server: pick(['Nginx', 'Apache', 'LiteSpeed']),
        cms: pick(['WordPress', 'None', 'Drupal', 'Custom']),
        js: ['React', 'Vue', 'jQuery', 'Next.js']
            .filter(() => yesNo(0.4)),
        cdn: pick(['Cloudflare', 'Akamai', 'Fastly', 'None']),
        proxy: yesNo(0.5)
            ? 'Cloudflare'
            : 'None'
    };

    if (!tech.js.length) {
        tech.js = ['Vanilla JS'];
    }

        // ================================
    // Security Score
    // ================================

    let score = 0;

    score += (ssl.valid ? 25 : 0)
           - (ssl.tls.some(t => t.includes('deprecated')) ? 6 : 0);

    score += (headers.filter(h => h.present).length / 6) * 20;

    score += (dns.SPF ? 4 : 0)
           + (dns.DMARC ? 4 : 0)
           + (dns.DKIM ? 2 : 0);

    score += (cookies.secure ? 4 : 0)
           + (cookies.httpOnly ? 4 : 0)
           + (cookies.sameSite ? 4 : 0);

    score += (rep.blacklisted || rep.phishing || rep.malware)
           ? 0
           : 15;

    score += (tech.cdn !== 'None' ? 4 : 0)
           + (http.server === 'Hidden (good)' ? 4 : 2);

    score = Math.max(0, Math.min(100, Math.round(score)));

    const risk =
        score >= 90 ? 'Excellent' :
        score >= 75 ? 'Low' :
        score >= 60 ? 'Medium' :
        score >= 40 ? 'High' :
        'Critical';

    return {
        id: Date.now(),
        url: host,
        fullUrl: url,
        date: new Date().toISOString(),
        userId: currentUser.id,

        score,
        risk,

        ssl,
        headers,
        domain,
        dns,
        rep,
        cookies,
        http,
        tech
    };
}

// ---------- Render Scanner ----------
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
  // Support arriving via quick-scan with ?url= prefilled and auto-run
  const prefill = new URLSearchParams(location.search).get('url');
  if(prefill){
    document.getElementById('scan-url').value = prefill;
    runScan();
  }
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
          ${scoreRing(r.score, r.risk)}
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

    ${r.connectionError ? `<div class="card mb" style="border-left:3px solid var(--yellow)">
      <b>⚠️ Incomplete scan</b>
      <p class="muted mt" style="font-size:13px;margin-top:6px">${r.connectionError}</p>
    </div>` : ''}

    ${section('🔒 SSL/TLS Analysis',[
      finding(r.ssl.https,'HTTPS Available',r.ssl.https?'Site served over HTTPS':'No HTTPS – data unencrypted'),
      finding(r.ssl.valid,'Certificate Valid',r.ssl.expires?`Expires ${r.ssl.expires} (${r.ssl.daysToExpiry} days)`:'No certificate presented'),
      findingInfo('Certificate Issuer',r.ssl.issuer),
      finding(r.ssl.chainComplete,'Certificate Chain',r.ssl.chainComplete?'Complete chain of trust':'Chain could not be verified'),
      findingInfo('Supported TLS',r.ssl.tls.map(t=>`<span class="tag">${t}</span>`).join('')),
    ], 'Checks whether your connection to this site is encrypted, and whether the certificate proving its identity is valid and trustworthy.')}

    ${section('🛡️ Security Headers',
      r.headers.map(h=>finding(h.present,h.name,(h.present?'Header present':'Missing – recommended to add')+' — '+headerHint(h.name))),
      'Extra instructions a site can send your browser to block common attacks like clickjacking and malicious scripts — missing ones aren\'t automatically dangerous, but they remove a layer of protection.')}

    ${section('🌍 Domain Information',[
  findingInfo('Domain Age', r.domain.age),
  findingInfo('Registrar', r.domain.registrar),
  findingInfo('Creation Date', r.domain.created),
  findingInfo('Last Updated', r.domain.updated),
  findingInfo('Domain Expires', r.domain.expires),

  findingInfo(
    'Name Servers',
    Array.isArray(r.domain.name_servers) && r.domain.name_servers.length
      ? r.domain.name_servers.join('<br>')
      : 'Unknown'
  ),

  findingInfo('DNSSEC', r.domain.dnssec),

  findingInfo(
    'WHOIS Status',
    Array.isArray(r.domain.status) && r.domain.status.length
      ? r.domain.status.join('<br>')
      : 'Unknown'
  ),

  findingInfo('IP Address', r.domain.ip),
  findingInfo('Hosting Provider', r.domain.host),

  ...(r.domain.lookupError
      ? [findingInfo('WHOIS Lookup', `⚠️ ${r.domain.lookupError}`)]
      : []),
], 'Public registration details about who owns this domain and how long it\'s existed — brand-new domains are worth extra caution.')}
    ${section('🌐 DNS Analysis',[
      findingInfo('A Record',r.dns.A), findingInfo('AAAA Record',r.dns.AAAA),
      findingInfo('MX Record',r.dns.MX), findingInfo('NS Record',r.dns.NS),
      findingInfo('TXT Record',r.dns.TXT), findingInfo('CNAME',r.dns.CNAME),
      finding(r.dns.SPF,'SPF Record',(r.dns.SPF?'SPF configured':'No SPF – email spoofing risk')+' — SPF lists which servers are allowed to send email as this domain'),
      finding(r.dns.DMARC,'DMARC Record',(r.dns.DMARC?'DMARC configured':'No DMARC policy')+' — DMARC tells email providers what to do with messages that fail spoofing checks'),
      finding(r.dns.DKIM,'DKIM',('DKIM signing '+(r.dns.DKIM?'detected':'not detected'))+' — DKIM is a digital signature proving an email really came from this domain'),
    ], 'Checks this domain\'s core internet setup and whether it\'s protected against attackers sending fake emails pretending to be from it.')}

    ${section('🚨 Website Reputation',[
      finding(!r.rep.blacklisted,'Blacklist Status',r.rep.blacklisted?'Listed on blacklist':'Not blacklisted'),
      finding(!r.rep.phishing,'Phishing Reports',r.rep.phishing?'Phishing reports found':'No phishing reports'),
      finding(!r.rep.malware,'Malware Reports',r.rep.malware?'Malware reports found':'No malware reports'),
      findingInfo('Summary',r.rep.summary),
    ], 'Checks whether this site has been publicly reported for phishing, malware, or other malicious activity.')}

    ${section('🍪 Cookie Security', r.cookies.count===0 ? [
      findingInfo('Cookies Detected','This response set no cookies — nothing to assess here.'),
    ] : [
      finding(r.cookies.secure,'Secure Flag',(r.cookies.secure?'Cookies use Secure':'Missing Secure flag')+' — Secure means cookies are only ever sent over an encrypted connection'),
      finding(r.cookies.httpOnly,'HttpOnly Flag',(r.cookies.httpOnly?'Cookies use HttpOnly':'Missing HttpOnly flag')+' — HttpOnly hides cookies from page scripts, blocking a common theft technique'),
      finding(r.cookies.sameSite,'SameSite Flag',(r.cookies.sameSite?'SameSite configured':'Missing SameSite')+' — SameSite stops other sites from riding along with your cookies to fake actions on your behalf'),
      findingInfo('Cookies Detected',r.cookies.count),
    ], 'Checks how safely this site handles the small files ("cookies") it stores in your browser to remember you.')}

   
    ${section('📡 HTTP Analysis',[
    findingInfo(
        'Status Code',
        `<b>${r.http.status_title}</b><br>${r.http.status_explanation}`
    ),

    findingInfo(
        'Response Time',
        r.http.response_time != null
            ? `${r.http.response_time} ms`
            : 'Unknown'
    ),

    findingInfo(
        'Redirect Chain',
        r.http.redirects.join('<br>')
    ),

    finding(
        r.http.server === 'Hidden',
        'Server Disclosure',
        r.http.server === 'Hidden'
            ? 'Server header hidden. This is good practice because it reveals less information to attackers.'
            : `Server: ${r.http.server}`
    ),
], 'Checks how the web server responds to requests and how much it reveals about its own setup — less disclosure gives attackers fewer clues.')}

    ${section('🔍 Technology Detection',[
      findingInfo('Web Server',r.tech.server),
      findingInfo('CMS',r.tech.cms),
      findingInfo('JS Frameworks',r.tech.js.map(t=>`<span class="tag">${t}</span>`).join('')),
      findingInfo('CDN',r.tech.cdn),
      findingInfo('Reverse Proxy',r.tech.proxy),
    ], 'Identifies the software and infrastructure this site is built on — purely informational, not a pass/fail check.')}`;

  animateScore(r.score, r.risk);
  container.scrollIntoView({behavior:'smooth'});
}

// ---------- Save website ----------

async function saveWebsite(url){
  try{ await apiSavedAdd(url); toast('Website saved!','success'); }
  catch(e){ toast(e.message==='Already saved'?'Already saved.':'Save failed: '+e.message, e.message==='Already saved'?'warn':'error'); }
}


function scoreRing(score, risk){
  if(risk === 'Incomplete'){
    return `<div class="score-ring"><svg width="160" height="160">
      <circle cx="80" cy="80" r="68" stroke="rgba(255,255,255,.08)" stroke-width="12" fill="none"/>
      <circle cx="80" cy="80" r="68" stroke="var(--slate)" stroke-width="12" fill="none"
        stroke-dasharray="6 10" stroke-linecap="round" opacity=".5"/>
      </svg><div class="score-num"><b style="color:var(--slate);font-size:22px">N/A</b><small>not assessed</small></div></div>`;
  }
  const color = score>=90?'#00B8D9':score>=75?'#22C55E':score>=60?'#FACC15':score>=40?'#FB923C':'#EF4444';
  const r=68, circ=2*Math.PI*r;
  const uid='sg'+Math.floor(Math.random()*100000);
  return `<div class="score-ring"><svg width="160" height="160">
    <defs><linearGradient id="${uid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${color}"/><stop offset="100%" stop-color="#00A6C4"/></linearGradient></defs>
    <circle cx="80" cy="80" r="${r}" stroke="rgba(255,255,255,.08)" stroke-width="12" fill="none"/>
    <circle cx="80" cy="80" r="${r}" stroke="url(#${uid})" stroke-width="12" fill="none"
      stroke-dasharray="${circ}" stroke-dashoffset="${circ}" stroke-linecap="round"
      style="transition:stroke-dashoffset 1.4s cubic-bezier(.2,.8,.2,1)" class="ring-anim"/>
    </svg><div class="score-num"><b style="color:${color}">0</b><small>/ 100</small></div></div>`;
}



// Animate ring stroke + count-up number
function animateScore(target, risk){
  if(risk === 'Incomplete') return;
  const ring=document.querySelector('.ring-anim');
  const numEl=document.querySelector('.score-num b');
  if(ring){ const r=68,circ=2*Math.PI*r;
    setTimeout(()=>ring.style.strokeDashoffset=circ-(target/100)*circ,60); }
  if(numEl){ let n=0; const step=Math.max(1,Math.round(target/40));
    const iv=setInterval(()=>{ n+=step; if(n>=target){n=target;clearInterval(iv);} numEl.textContent=n; },20); }
}

function section(title, findings, subtitle){
  return `<div class="card result-section">
    <div class="result-head" onclick="this.nextElementSibling.classList.toggle('hidden');this.querySelector('span').style.transform=this.nextElementSibling.classList.contains('hidden')?'rotate(-90deg)':'rotate(0)'">
      <div><h3>${title}</h3>${subtitle?`<p class="muted" style="font-size:12px;font-weight:400;margin-top:4px">${subtitle}</p>`:''}</div>
      <span>▾</span></div>
    <div class="result-body">${findings.join('')}</div></div>`;
}
function headerHint(name){
  const hints = {
    'Content-Security-Policy': 'blocks malicious scripts from running on the page',
    'Strict-Transport-Security': 'forces browsers to always use the encrypted version of the site',
    'X-Frame-Options': 'stops other sites from hiding this page inside theirs to trick clicks ("clickjacking")',
    'X-Content-Type-Options': 'stops browsers from misreading file types in ways attackers can exploit',
    'Referrer-Policy': 'controls how much of this site\'s address is shared when someone clicks a link away from it',
    'Permissions-Policy': 'controls which browser features (camera, location, etc.) the site can use',
  };
  return hints[name] || 'a browser-level security setting';
}
function finding(ok,title,detail){
  return `<div class="finding ${ok?'pass':'fail'}"><span class="finding-icon">${ok?'✅':'❌'}</span>
    <div><b>${title}</b><div class="finding-detail">${detail}</div></div></div>`;
}
function findingInfo(title,detail){
  return `<div class="finding info"><span class="finding-icon">ℹ️</span>
    <div><b>${title}</b><div class="finding-detail">${detail}</div></div></div>`;
}


// ================================
// Expose APIs (Classic Scripts)
// ================================

window.apiScan = apiScan;
window.apiHistory = apiHistory;
window.apiGetScan = apiGetScan;
window.apiDeleteScan = apiDeleteScan;
window.renderScanner = renderScanner;
window.runScan = runScan;
window.finishScan = finishScan;
window.saveWebsite = saveWebsite;
window.renderResult = renderResult;

// Temporary until backend scanner replaces mockScan
window.mockScan = mockScan;