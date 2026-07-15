
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

