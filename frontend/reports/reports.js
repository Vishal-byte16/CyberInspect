// Reports
function reportPdfUrl(id){ return `${API}/api/reports/${id}/pdf`; }
function reportHtmlUrl(id){ return `${API}/api/reports/${id}/html`; }

// ---------- Report Modal ----------
async function openReport(id){
  let r;
  try{ r = await apiGetScan(id); }
  catch(e){ toast('Could not load report: '+e.message,'error'); return; }
  document.getElementById('report-modal').classList.remove('hidden');
  renderResult(r, document.getElementById('report-body'));
}
function closeReport(){ document.getElementById('report-modal').classList.add('hidden'); }

// ---------- Report Export (uses the real backend-generated PDF/HTML) ----------
async function _downloadAuthed(url, filename){
  try{
    const res = await fetch(url, { headers: { 'Authorization': 'Bearer ' + token() } });
    if(!res.ok) throw new Error('Report request failed (' + res.status + ')');
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }catch(e){ toast('Download failed: '+e.message,'error'); }
}
function downloadHTML(id){
  _downloadAuthed(reportHtmlUrl(id), `CyberInspect_report_${id}.html`);
  toast('HTML report downloading…','success');
}
function downloadPDF(id){
  _downloadAuthed(reportPdfUrl(id), `CyberInspect_report_${id}.pdf`);
  toast('PDF report downloading…','success');
}

// ---------- Exports ----------
window.openReport = openReport;
window.closeReport = closeReport;
window.downloadHTML = downloadHTML;
window.downloadPDF = downloadPDF;

// ---------- Standalone Report Page (reports.html?id=123) ----------
async function renderReportPage(c){
  const id = new URLSearchParams(location.search).get('id');
  if(!id){
    c.innerHTML = '<div class="card">No scan specified. <a href="history.html">View your scan history</a>.</div>';
    return;
  }
  c.innerHTML = '<div class="card">Loading report…</div>';
  let r;
  try{ r = await apiGetScan(id); }
  catch(e){ c.innerHTML = '<div class="card">Could not load report: '+e.message+'</div>'; return; }
  c.innerHTML = `<div class="flex between center mb wrap gap">
      <h2>Scan Report</h2>
      <div class="flex gap">
        <button class="btn btn-outline btn-sm" onclick="downloadHTML(${id})">⬇ HTML</button>
        <button class="btn btn-primary btn-sm" onclick="downloadPDF(${id})">⬇ PDF</button>
      </div>
    </div>
    <div class="card" id="report-page-body"></div>`;
  renderResult(r, document.getElementById('report-page-body'));
}
