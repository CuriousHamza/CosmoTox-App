const API_BASE = window.location.origin;

// ── Supabase auth ────────────────────────────────────────────────────────────
const _supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
let _session = null;
let _selectedProductType = null;

function selectProductType(btn) {
  const wasActive = btn.classList.contains('active');
  document.querySelectorAll('.type-chip').forEach(c => c.classList.remove('active'));
  if (!wasActive) {
    btn.classList.add('active');
    _selectedProductType = btn.dataset.type;
  } else {
    _selectedProductType = null;
  }
}

async function getToken() {
  const { data } = await _supabase.auth.getSession();
  _session = data.session;
  return _session?.access_token || null;
}

function authHeaders() {
  const token = _session?.access_token;
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

function updatePasswordStrength(password) {
  const bar   = document.getElementById('password-strength-bar');
  const label = document.getElementById('password-strength-label');
  if (!bar || !label) return;
  let score = 0;
  if (password.length >= 8)           score++;
  if (password.length >= 12)          score++;
  if (/[A-Z]/.test(password))         score++;
  if (/[0-9]/.test(password))         score++;
  if (/[^A-Za-z0-9]/.test(password))  score++;
  const levels = [
    { w: '0%',   c: '',        t: '' },
    { w: '20%',  c: '#ef4444', t: 'Very weak' },
    { w: '40%',  c: '#f97316', t: 'Weak' },
    { w: '60%',  c: '#eab308', t: 'Fair' },
    { w: '80%',  c: '#22c55e', t: 'Good' },
    { w: '100%', c: '#2dd4bf', t: 'Strong' },
  ];
  const lv = password.length === 0 ? levels[0] : levels[Math.min(score, 5)];
  bar.style.width      = lv.w;
  bar.style.background = lv.c;
  label.textContent    = lv.t;
  label.style.color    = lv.c;
}

async function handleLogin() {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl    = document.getElementById('login-error');
  const btn      = document.getElementById('login-btn');
  errEl.style.display = 'none';
  btn.disabled = true; btn.textContent = 'Signing in…';
  const { data, error } = await _supabase.auth.signInWithPassword({ email, password });
  btn.disabled = false; btn.textContent = 'Sign In';
  if (error) {
    errEl.textContent = error.message;
    errEl.style.display = 'block';
    return;
  }
  _session = data.session;
  _onSignedIn();
}

async function handleRegister() {
  const name     = document.getElementById('register-name').value.trim();
  const email    = document.getElementById('register-email').value.trim();
  const password = document.getElementById('register-password').value;
  const errEl    = document.getElementById('register-error');
  const succEl   = document.getElementById('register-success');
  const btn      = document.getElementById('register-btn');
  errEl.style.display = 'none'; succEl.style.display = 'none';
  if (password.length < 8) {
    errEl.textContent = 'Password must be at least 8 characters.';
    errEl.style.display = 'block';
    return;
  }
  btn.disabled = true; btn.textContent = 'Creating account…';
  const { error } = await _supabase.auth.signUp({
    email, password,
    options: { data: { display_name: name } },
  });
  btn.disabled = false; btn.textContent = 'Create Account';
  if (error) {
    errEl.textContent = error.message;
    errEl.style.display = 'block';
    return;
  }
  succEl.style.display = 'block';
}

async function handleLogout() {
  await _supabase.auth.signOut();
  _session = null;
  showScreen('login');
  document.getElementById('logout-btn').style.display = 'none';
  document.getElementById('history-btn').style.display = 'none';
}

function _onSignedIn() {
  document.getElementById('logout-btn').style.display = 'flex';
  document.getElementById('history-btn').style.display = 'flex';
  _loadWatchlistFromApi();
  showScreen('home');
}

async function _loadWatchlistFromApi() {
  const token = _session?.access_token;
  if (!token) return;
  try {
    const res = await fetch(`${API_BASE}/watchlist`, { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    watchlist.clear();
    organWatchlist.clear();
    for (const item of data.watchlist) {
      if (item.watchlist_type === 'toxicant') watchlist.add(item.key);
      if (item.watchlist_type === 'organ')    organWatchlist.add(item.key);
    }
    localStorage.setItem(WATCHLIST_KEY,       JSON.stringify([...watchlist]));
    localStorage.setItem(ORGAN_WATCHLIST_KEY, JSON.stringify([...organWatchlist]));
    renderWatchlistScreen();
  } catch(e) { /* watchlist load failed silently */ }
}

async function _syncWatchlistItem(key, watchlistType, adding) {
  const token = _session?.access_token;
  if (!token) return; // offline: localStorage already updated
  try {
    const method = adding ? 'POST' : 'DELETE';
    await fetch(`${API_BASE}/watchlist/${encodeURIComponent(key)}`, {
      method,
      headers: authHeaders(),
      body: JSON.stringify({ watchlist_type: watchlistType }),
    });
  } catch(e) { /* watchlist sync failed silently */ }
}

// ── Screen transitions ──────────────────────────────────────────────────────
function showScreen(id) {
  if (id !== 'loading') stopIconCycle();
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.remove('active', 'entering');
  });
  const el = document.getElementById('screen-' + id);
  el.classList.add('entering');
  void el.offsetWidth; // force reflow so animation fires correctly
  el.classList.add('active');
  if (id === 'watchlist') renderWatchlistScreen();
}

function goBack() { showScreen('home'); }

// ── Loading icon system ─────────────────────────────────────────────────────
const ICONS = {
  'scan-eye': `<svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
    <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
    <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
    <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
    <circle cx="12" cy="12" r="1"/>
    <path d="M18.944 12.33a1 1 0 0 0 0-.66 7.5 7.5 0 0 0-13.888 0 1 1 0 0 0 0 .66 7.5 7.5 0 0 0 13.888 0"/>
  </svg>`,
  'flask': `<svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2"/>
    <path d="M6.453 15h11.094"/>
    <path d="M8.5 2h7"/>
  </svg>`,
  'atom': `<svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="1"/>
    <path d="M20.2 20.2c2.04-2.03.02-7.36-4.5-11.9-4.54-4.52-9.87-6.54-11.9-4.5-2.04 2.03-.02 7.36 4.5 11.9 4.54 4.52 9.87 6.54 11.9 4.5Z"/>
    <path d="M15.7 15.7c4.52-4.54 6.54-9.87 4.5-11.9-2.03-2.04-7.36-.02-11.9 4.5-4.52 4.54-6.54 9.87-4.5 11.9 2.03 2.04 7.36.02 11.9-4.5Z"/>
  </svg>`,
  'beaker': `<svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M4.5 3h15"/>
    <path d="M6 3v16a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V3"/>
    <path d="M6 14h12"/>
  </svg>`,
};

let _cycleInterval = null;
let _cycleIdx = 0;

function stopIconCycle() {
  if (_cycleInterval) { clearInterval(_cycleInterval); _cycleInterval = null; }
}

function _applyIcon(el, key) {
  el.innerHTML = ICONS[key];
  el.style.animation = 'icon-pulse 2s ease-in-out infinite, icon-enter 0.4s ease-out forwards';
}

function _transitionIcon(el, key) {
  el.style.animation = 'icon-exit 0.35s ease-in forwards';
  setTimeout(() => _applyIcon(el, key), 360);
}

function showLoading(mode, title, subtext) {
  stopIconCycle();
  document.getElementById('loading-title').textContent = title;
  document.getElementById('loading-subtext').innerHTML = subtext;
  const iconEl = document.getElementById('loading-icon');

  if (mode === 'ocr') {
    _applyIcon(iconEl, 'scan-eye');
  } else {
    // analyze: cycle flask → atom → beaker
    const icons = ['flask', 'atom', 'beaker'];
    _cycleIdx = 0;
    _applyIcon(iconEl, icons[_cycleIdx]);
    _cycleInterval = setInterval(() => {
      _cycleIdx = (_cycleIdx + 1) % icons.length;
      _transitionIcon(iconEl, icons[_cycleIdx]);
    }, 1800);
  }

  showScreen('loading');
}

// ── History (persisted to localStorage) ────────────────────────────────────
const HISTORY_KEY = 'cosmotox_history_v1';
const MAX_HISTORY = 10;
const VERDICT_DOT = { concerning: 'red', caution: 'amber', clean: 'green' };
const history = (() => {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
  catch(e) { return []; }
})();

function addToHistory(entryOrLabel, analysis) {
  let entry;
  if (typeof entryOrLabel === 'object' && entryOrLabel !== null && entryOrLabel.type) {
    // New-style: full entry object passed directly (e.g. compare entries)
    entry = entryOrLabel;
  } else {
    // Legacy call: addToHistory(label, analysis)
    const name    = entryOrLabel || 'Pasted Ingredients';
    const verdict = analysis ? analysis.verdict : 'clean';
    const dotCls  = VERDICT_DOT[verdict] || 'green';
    entry = { type: 'scan', name, dotCls, analysis };
  }
  history.unshift(entry);
  if (history.length > MAX_HISTORY) history.pop();
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(history)); } catch(e) {}
  renderHistory();
}

function clearHistory() {
  history.length = 0;
  try { localStorage.removeItem(HISTORY_KEY); } catch(e) {}
  renderHistory();
}

function renderHistory() {
  const section = document.getElementById('history-section');
  const chips   = document.getElementById('history-chips');
  if (!history.length) { section.style.display = 'none'; return; }
  section.style.display = 'block';
  chips.innerHTML = history.map((h, i) => {
    if (h.type === 'compare') {
      const others = h.names.filter(n => n !== h.winner);
      const label  = others.length === 1
        ? `${h.winner} vs ${others[0]}`
        : `${h.winner} \u00b7 ${h.names.length} products`;
      return `
        <div class="history-chip history-chip--compare" onclick="showHistoryItem(${i})" role="button" tabindex="0"
             onkeydown="if(event.key==='Enter')showHistoryItem(${i})">
          <div class="chip-name"><span class="chip-trophy">&#127942;</span>${escHtml(label)}</div>
          <div class="chip-dot ${h.dotCls}"></div>
        </div>`;
    }
    return `
      <div class="history-chip" onclick="showHistoryItem(${i})" role="button" tabindex="0"
           onkeydown="if(event.key==='Enter')showHistoryItem(${i})">
        <div class="chip-name">${escHtml(h.name)}</div>
        <div class="chip-dot ${h.dotCls}"></div>
      </div>`;
  }).join('');
}

function showHistoryItem(i) {
  const item = history[i];
  if (!item) return;
  if (item.type === 'compare') {
    renderCompareResults(item.compareData);
  } else {
    renderResults(item.name, item.analysis);
  }
}

// ── Server-backed history screen ────────────────────────────────────────────
let _historyData   = [];
let _historyFilter = 'all';

async function loadHistoryScreen() {
  const rows    = document.getElementById('history-rows');
  const loading = document.getElementById('history-loading');
  const empty   = document.getElementById('history-empty');
  rows.innerHTML        = '';
  loading.style.display = 'block';
  empty.style.display   = 'none';

  try {
    const res  = await fetch(`${API_BASE}/history`, { headers: authHeaders() });
    const data = await res.json();
    _historyData = data.history || [];
  } catch(e) {
    _historyData = [];
  }

  loading.style.display = 'none';
  // Reset filter to "All" each time the screen opens
  _historyFilter = 'all';
  document.querySelectorAll('.hfilter').forEach(b => b.classList.toggle('active', b.dataset.verdict === 'all'));
  renderHistoryTable();
}

function renderHistoryTable() {
  const rows  = document.getElementById('history-rows');
  const empty = document.getElementById('history-empty');
  if (!rows) return;

  const items = _historyFilter === 'all'
    ? _historyData
    : _historyData.filter(h => h.verdict === _historyFilter);

  if (!items.length) {
    rows.innerHTML        = '';
    empty.style.display   = 'block';
    return;
  }
  empty.style.display = 'none';

  rows.innerHTML = items.map((h, i) => {
    const date    = new Date(h.scanned_at);
    const dateStr = date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: '2-digit' });
    const timeStr = date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const name    = escHtml(h.product_name || 'Unknown Product');
    const typeTag = h.scan_type === 'compare'
      ? '<span class="htype-tag htype-compare">Compare</span>'
      : '<span class="htype-tag htype-scan">Scan</span>';
    const verdict = h.verdict || 'clean';

    return `
      <div class="htable-row verdict-border--${verdict}" onclick="showHistoryDetail(${i})" role="button" tabindex="0"
           onkeydown="if(event.key==='Enter')showHistoryDetail(${i})">
        <span class="htcol htcol-date">
          <span class="hdate-day">${dateStr}</span>
          <span class="hdate-time">${timeStr}</span>
        </span>
        <span class="htcol htcol-name">
          <span class="hprod-name">${name}</span>
          ${typeTag}
        </span>
        <span class="htcol htcol-verdict">
          <span class="verdict-pill verdict-pill--${verdict}">${verdict}</span>
        </span>
        <span class="htcol htcol-count">${h.toxicant_count ?? 0}</span>
      </div>`;
  }).join('');
}

function filterHistory(btn) {
  document.querySelectorAll('.hfilter').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  _historyFilter = btn.dataset.verdict;
  renderHistoryTable();
}

function showHistoryDetail(idx) {
  const items = _historyFilter === 'all'
    ? _historyData
    : _historyData.filter(h => h.verdict === _historyFilter);
  const h = items[idx];
  if (!h) return;

  const date    = new Date(h.scanned_at).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
  const verdict  = h.verdict || 'clean';
  const toxCount = h.toxicant_count ?? 0;
  const toxList  = (h.top_toxicants || []).map(k =>
    `<span class="tox-tag">${escHtml(k.replace(/_/g, ' '))}</span>`
  ).join('');

  document.getElementById('history-detail-body').innerHTML = `
    <div class="hdetail-card">
      <div class="hdetail-name">${escHtml(h.product_name || 'Unknown Product')}</div>
      <div class="hdetail-meta">${date}&nbsp;·&nbsp;${escHtml(h.scan_type || 'scan')}</div>
      <div class="hdetail-verdict-row">
        <span class="verdict-pill verdict-pill--${verdict} verdict-pill--lg">${verdict}</span>
        <span class="hdetail-count">${toxCount} toxicant${toxCount !== 1 ? 's' : ''} detected</span>
      </div>
      ${toxCount > 0 ? `
        <div class="hdetail-section-label">Detected Toxicants</div>
        <div class="hdetail-tox-list">${toxList}</div>
      ` : '<div class="hdetail-clean">No concerning toxicants found.</div>'}
      <div class="hdetail-papers">Based on ${h.paper_count ?? 0} research papers</div>
    </div>`;

  showScreen('screen-history-detail');
}

// ── OCR photo flow ──────────────────────────────────────────────────────────
function retryPhoto() {
  document.getElementById('ocr-error').style.display = 'none';
  document.getElementById('photo-camera').value = '';
  document.getElementById('photo-camera').click();
}

function resizeImage(file, maxPx, quality) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = function(e) {
      const img = new Image();
      img.onload = function() {
        const scale = Math.min(1, maxPx / Math.max(img.width, img.height));
        const canvas = document.createElement('canvas');
        canvas.width  = Math.round(img.width  * scale);
        canvas.height = Math.round(img.height * scale);
        canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg', quality));
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

function handlePhotoUpload(file) {
  if (!file) return;
  document.getElementById('ocr-error').style.display = 'none';
  (async () => {
    const dataUrl   = await resizeImage(file, 1600, 0.85);
    const base64    = dataUrl.split(',')[1];
    const mime_type = 'image/jpeg';
    showLoading('ocr', 'Reading label...', 'Extracting ingredients from your photo');
    try {
      await getToken();
      const res = await fetch(`${API_BASE}/ocr-ingredients`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ image_base64: base64, mime_type }),
      });
      showScreen('home');
      if (!res.ok) {
        if (res.status === 401) { _handle401(); return; }
        const err = await res.json().catch(() => ({}));
        showOcrError(err.detail || "Couldn't read the label. Please try a clearer photo.");
        return;
      }
      const data     = await res.json();
      const textarea = document.getElementById('paste-input');
      textarea.value = data.ingredients_text;
      textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
      textarea.classList.add('highlight');
      setTimeout(() => textarea.classList.remove('highlight'), 1200);
    } catch (e) {
      showScreen('home');
      showOcrError("Network error. Make sure the server is running.");
    }
  })();
}

function showOcrError(msg) {
  const el = document.getElementById('ocr-error');
  document.getElementById('ocr-error-msg').textContent = msg;
  el.style.display = 'block';
}

// ── Analyze flow ─────────────────────────────────────────────────────────────
async function handlePasteAnalyze() {
  const text        = document.getElementById('paste-input').value.trim();
  const productName = document.getElementById('product-name-input').value.trim();
  if (!text) { alert('Please paste an ingredient list or upload a photo.'); return; }
  if (!productName) { alert('Please enter the product name.'); return; }
  showLoading('analyze', 'Analyzing...', 'Checking ingredients against<br>15 toxicant categories and<br>peer-reviewed research');
  try {
    await getToken();
    const res  = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ ingredients_text: text, product_name: productName, product_type: _selectedProductType }),
    });
    if (res.status === 401) { _handle401(); return; }
    const data = await res.json();
    addToHistory(productName, data.analysis);

    // Auto-highlight the AI-detected chip (only if user didn't manually select one)
    const detectedType = data.analysis && data.analysis.detected_product_type;
    if (detectedType && !_selectedProductType) {
      document.querySelectorAll('.type-chip').forEach(c => {
        c.classList.toggle('active', c.dataset.type === detectedType);
      });
      _selectedProductType = detectedType;
    }

    renderResults(productName, data.analysis);
  } catch (e) {
    showError('Network error. Make sure the server is running.');
  }
}

function showError(msg) {
  showScreen('results');
  document.getElementById('result-product-name').textContent = 'Error';
  document.getElementById('result-brand').textContent = '';
  document.getElementById('result-verdict').innerHTML = `<div class="error-msg">${escHtml(msg)}</div>`;
  document.getElementById('result-toxicants').innerHTML = '';
}

// ── Render results ───────────────────────────────────────────────────────────

// Store current result for share/copy
let _currentResultLabel = '';
let _currentResultAnalysis = null;

function renderResults(label, analysis) {
  _currentResultLabel   = label || 'Ingredient Analysis';
  _currentResultAnalysis = analysis;

  document.getElementById('result-product-name').textContent = _currentResultLabel;
  document.getElementById('result-brand').textContent = '';
  document.getElementById('result-alternatives').innerHTML = '';

  // ── Share / copy action buttons (Feature 4)
  const canShare = typeof navigator.share === 'function';
  document.getElementById('result-actions').innerHTML = `
    ${canShare ? `
    <button class="action-btn" onclick="shareResults()" aria-label="Share results">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
      </svg>
      Share
    </button>` : ''}
    <button class="action-btn" onclick="copyResults()" aria-label="Copy results to clipboard">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
      </svg>
      Copy
    </button>
  `;

  // ── Watchlist strip (Feature 5 + Organ watchlist)
  const detected = analysis && analysis.detected_toxicants || [];
  const wlStrip  = document.getElementById('result-watchlist-strip');
  const toxHits  = detected.filter(t => watchlist.has(t.toxicant_key));
  const organHits = organWatchlist.size > 0
    ? detected.filter(t =>
        [...organWatchlist].some(ok => organMatchesToxicant(t.top_organs, ok))
      )
    : [];
  // Deduplicate organ hits that are already in toxHits
  const organOnlyHits = organHits.filter(t => !watchlist.has(t.toxicant_key));
  const hasAnyWatchlist = watchlist.size > 0 || organWatchlist.size > 0;
  const totalHits = toxHits.length + organOnlyHits.length;

  if (hasAnyWatchlist) {
    if (totalHits > 0) {
      const toxChips = toxHits.map(t =>
        `<span class="watchlist-hit">${escHtml(t.display_name)}</span>`
      ).join('');
      const organChips = organOnlyHits.map(t =>
        `<span class="watchlist-hit organ-hit">${escHtml(t.display_name)}</span>`
      ).join('');
      wlStrip.innerHTML = `
        <div class="watchlist-strip wl-warn">
          <span class="watchlist-strip-label">Your Watchlist</span>
          <div class="watchlist-hits">${toxChips}${organChips}</div>
        </div>`;
    } else {
      wlStrip.innerHTML = `
        <div class="watchlist-strip wl-ok">
          <span class="watchlist-strip-label">Your Watchlist</span>
          <span style="font-size:0.78rem;color:var(--green);opacity:0.85;margin-left:4px;">None of your flagged ingredients detected</span>
        </div>`;
    }
  } else {
    wlStrip.innerHTML = '';
  }

  const n   = analysis ? analysis.total_toxicants_detected : 0;
  const m   = analysis ? analysis.total_relevant_papers    : 0;

  if (n > 0) {
    document.getElementById('result-verdict').innerHTML = `
      <p class="scan-summary">Found <strong>${n} flagged ingredient categor${n===1?'y':'ies'}</strong> — backed by ${m} relevant research paper${m===1?'':'s'}.</p>
    `;
  } else {
    document.getElementById('result-verdict').innerHTML = '';
  }

  const toxDiv = document.getElementById('result-toxicants');

  if (!detected.length) {
    toxDiv.innerHTML = `
      <div class="clean-card">
        <div class="clean-icon">✓</div>
        <h3>No flagged ingredients found</h3>
        <p>None of the ingredients in this product matched our database of 15 toxicant categories.</p>
      </div>`;
  } else {
    toxDiv.innerHTML = `
      <div class="toxicants-section">
        <h3>Toxicant Breakdown</h3>
        ${detected.map((t, i) => renderToxicantCard(t, i)).join('')}
      </div>`;
  }

  // ── All ingredients cloud (Feature 3)
  const allIng = analysis && analysis.all_ingredients || [];
  if (allIng.length > 0) {
    // Build a map: ingredient lowercase → { tier, toxicant_key }
    const flaggedMap = {};
    detected.forEach(t => {
      t.matched_ingredients.forEach(ing => {
        flaggedMap[ing.toLowerCase()] = { tier: t.tier, key: t.toxicant_key, idx: detected.indexOf(t) };
      });
    });
    const flaggedCount = allIng.filter(i => flaggedMap[i.toLowerCase()]).length;

    const pills = allIng.map(ing => {
      const fl = flaggedMap[ing.toLowerCase()];
      if (fl) {
        return `<span class="ing-pill flagged-${fl.tier}" title="${escHtml(ing)}"
                      onclick="scrollToCard('card-${fl.key}')" role="button" tabindex="0"
                      onkeydown="if(event.key==='Enter')scrollToCard('card-${fl.key}')"
                      aria-label="Flagged: ${escHtml(ing)}">${escHtml(ing)}</span>`;
      }
      return `<span class="ing-pill" title="${escHtml(ing)}">${escHtml(ing)}</span>`;
    }).join('');

    toxDiv.innerHTML += `
      <div class="ingredients-section">
        <details class="ingredients-details">
          <summary>
            <span>All Ingredients (${allIng.length} total, ${flaggedCount} flagged)</span>
            <span class="ing-arrow">▼</span>
          </summary>
          <div class="ingredients-cloud">${pills}</div>
        </details>
      </div>`;
  }

  const altDiv = document.getElementById('result-alternatives');
  const detected_toxicants = analysis && analysis.detected_toxicants || [];
  if (analysis && analysis.alternatives && analysis.alternatives.length > 0) {
    renderAlternatives(analysis.alternatives, detected_toxicants);
  } else if (detected_toxicants.length > 0 && !_selectedProductType && !(analysis && analysis.detected_product_type)) {
    // Toxicants found but neither manual selection nor AI detection produced a type — show nudge
    altDiv.innerHTML = `
      <div class="alt-nudge">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>Select a <strong>Product Type</strong> on the scan screen to see verified safer alternatives</span>
      </div>`;
  }

  showScreen('results');
}

function renderAlternatives(alternatives, detected) {
  const altDiv = document.getElementById('result-alternatives');
  if (!altDiv || !alternatives || alternatives.length === 0) return;

  const SHORT_LABELS = {
    parabens: 'Parabens', phthalates: 'Phthalates', pfas: 'PFAS',
    benzophenones: 'Benzophenones', siloxanes: 'Siloxanes', fragrance: 'Fragrance',
    toluene: 'Toluene', formaldehyde_releasers: 'Formaldehyde',
    heavy_metals: 'Heavy Metals', hydroquinone: 'Hydroquinone',
    ethanolamines: 'Ethanolamines', bha_bht: 'BHA/BHT',
    coal_tar: 'Coal Tar', triclosan: 'Triclosan', dioxane: '1,4-Dioxane',
  };
  const detectedKeys = new Set((detected || []).map(t => t.toxicant_key));
  const userCount = (detected || []).length;

  const itemsHtml = alternatives.map(alt => {
    const relevantAvoids = (alt.avoids || []).filter(k => detectedKeys.has(k));
    const avoidTags = relevantAvoids.map(k =>
      `<span class="alt-avoids-tag">${escHtml(SHORT_LABELS[k] || k)}</span>`
    ).join('');
    const externalIcon = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`;
    const amazonBtn = alt.amazon_url
      ? `<a class="alt-buy-btn alt-buy-amazon" href="${escHtml(alt.amazon_url)}" target="_blank" rel="noopener noreferrer" aria-label="Buy ${escHtml(alt.brand)} ${escHtml(alt.name)} on Amazon">${externalIcon}Amazon</a>` : '';
    const flipkartBtn = alt.flipkart_url
      ? `<a class="alt-buy-btn alt-buy-flipkart" href="${escHtml(alt.flipkart_url)}" target="_blank" rel="noopener noreferrer" aria-label="Buy ${escHtml(alt.brand)} ${escHtml(alt.name)} on Flipkart">${externalIcon}Flipkart</a>` : '';
    const altCount = alt.toxicant_count || 0;
    const reduction = userCount > 0
      ? Math.round(((userCount - altCount) / userCount) * 100)
      : 0;
    const comparisonHtml = userCount > 0 ? `
      <div class="alt-comparison">
        <span class="alt-comp-safe">${altCount} toxicants</span>
        <span class="alt-comp-sep">vs</span>
        <span class="alt-comp-user">${userCount} in yours</span>
        <span class="alt-comp-pct">${reduction}% cleaner</span>
      </div>` : '';
    return `
      <div class="alternative-item">
        <div class="alt-info">
          <div class="alt-brand">${escHtml(alt.brand)}</div>
          <div class="alt-name">${escHtml(alt.name)}</div>
          ${comparisonHtml}
          ${relevantAvoids.length > 0 ? `<div class="alt-avoids-row">${avoidTags}</div>` : ''}
        </div>
        <div class="alt-actions">${amazonBtn}${flipkartBtn}</div>
      </div>`;
  }).join('');

  const card = document.createElement('div');
  card.className = 'alternatives-section';
  card.innerHTML = `
    <div class="alternatives-card">
      <div class="alternatives-header">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
        <span>Safer Alternatives</span>
      </div>
      <p class="alternatives-sub">Engine-verified with 0 toxicants — safer alternatives to consider</p>
      <div class="alternatives-list">${itemsHtml}</div>
    </div>`;
  altDiv.appendChild(card);
}

function scrollToCard(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.open = true;
  el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

const TIER_BADGE = {
  high:   { dot: '●', label: 'HIGH CONCENTRATION',   cls: 'high'   },
  medium: { dot: '●', label: 'MEDIUM CONCENTRATION', cls: 'medium' },
  low:    { dot: '◎', label: 'TRACE AMOUNT',         cls: 'low'    },
};

function renderToxicantCard(t, idx) {
  const effects = t.top_effects && t.top_effects.length
    ? t.top_effects.map(e => `<li>${escHtml(e)}</li>`).join('')
    : '<li>Not specified</li>';
  const organs = t.top_organs && t.top_organs.length
    ? t.top_organs.map(o => `<li>${escHtml(o)}</li>`).join('')
    : '<li>Not specified</li>';
  const summary = t.llm_summary
    ? `<div class="llm-summary">${escHtml(t.llm_summary)}</div>` : '';
  const matched   = (t.matched_ingredients || []).map(i => escHtml(i)).join(', ');
  const tier      = t.tier || 'high';
  const badge     = TIER_BADGE[tier] || TIER_BADGE.high;
  const concBadge = `<div class="conc-badge ${badge.cls}">${badge.dot} ${badge.label}</div>`;

  return `
    <details open id="card-${t.toxicant_key}" style="--card-idx: ${idx}">
      <summary>
        <div class="summary-left">
          <h4>${escHtml(t.display_name)}</h4>
          <div class="paper-count">${t.paper_count} relevant research papers</div>
        </div>
        <span class="summary-arrow">▼</span>
      </summary>
      <div class="card-body">
        <div class="found-as"><span>Found as: </span>${matched}</div>
        ${concBadge}
        <div class="two-col">
          <div class="info-block">
            <h5>Health Effects</h5>
            <ul>${effects}</ul>
          </div>
          <div class="info-block">
            <h5>Organs Affected</h5>
            <ul>${organs}</ul>
          </div>
        </div>
        ${summary}
      </div>
    </details>
  `;
}

// ── Utilities ────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Compare flow ─────────────────────────────────────────────────────────────
const compareSlots = [];
let _compareSlotTarget = -1;

function showCompare() {
  if (compareSlots.length === 0) {
    compareSlots.push({ name: '', ingredientsText: '' });
    compareSlots.push({ name: '', ingredientsText: '' });
  }
  renderCompareSlots();
  showScreen('compare');
}

function addCompareSlot() {
  compareSlots.push({ name: '', ingredientsText: '' });
  renderCompareSlots();
}

function removeCompareSlot(idx) {
  compareSlots.splice(idx, 1);
  renderCompareSlots();
}

function updateSlotName(idx, value) {
  if (compareSlots[idx]) compareSlots[idx].name = value;
  updateCompareBtn();
}

function renderCompareSlots() {
  const container = document.getElementById('compare-slots');
  if (!container) return;
  container.innerHTML = compareSlots.map((slot, i) => renderSlot(slot, i)).join('');
  updateCompareBtn();
}

function renderSlot(slot, idx) {
  const has = slot.ingredientsText.trim().length > 0;
  const removeBtn = compareSlots.length > 2
    ? `<button class="slot-remove" onclick="removeCompareSlot(${idx})" aria-label="Remove product ${idx + 1}">
         <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
           <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
         </svg>
       </button>` : '';
  return `
    <div class="compare-slot${has ? ' has-ingredients' : ''}" id="slot-${idx}">
      <div class="slot-header">
        <div class="slot-num">${idx + 1}</div>
        <input class="slot-name-input" type="text" placeholder="Product name"
          value="${escHtml(slot.name)}" oninput="updateSlotName(${idx}, this.value)"
          aria-label="Product ${idx + 1} name" autocomplete="off" />
        ${removeBtn}
      </div>
      <div class="slot-body">
        <div class="slot-actions">
          <button class="slot-btn" onclick="triggerSlotCamera(${idx})" aria-label="Take photo for product ${idx + 1}">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            Camera
          </button>
          <button class="slot-btn" onclick="triggerSlotGallery(${idx})" aria-label="Choose photo for product ${idx + 1}">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <rect x="3" y="3" width="18" height="18" rx="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            Gallery
          </button>
        </div>
        <textarea class="slot-textarea${has ? ' highlight' : ''}" id="slot-textarea-${idx}"
          placeholder="Paste ingredients here, or use Camera / Gallery above…"
          oninput="onSlotTextareaInput(${idx}, this.value)"
          autocomplete="off">${escHtml(slot.ingredientsText)}</textarea>
      </div>
    </div>`;
}

function onSlotTextareaInput(idx, value) {
  compareSlots[idx].ingredientsText = value;
  const slotEl = document.getElementById(`slot-${idx}`);
  if (slotEl) slotEl.classList.toggle('has-ingredients', value.trim().length > 0);
  updateCompareBtn();
}

function triggerSlotCamera(idx) {
  _compareSlotTarget = idx;
  const el = document.getElementById('compare-photo-camera');
  el.value = '';
  el.click();
}

function triggerSlotGallery(idx) {
  _compareSlotTarget = idx;
  const el = document.getElementById('compare-photo-gallery');
  el.value = '';
  el.click();
}

async function handleComparePhoto(file) {
  if (!file || _compareSlotTarget < 0 || _compareSlotTarget >= compareSlots.length) return;
  const idx = _compareSlotTarget;

  showLoading('ocr', 'Reading label...', `Extracting ingredients from product ${idx + 1}`);

  try {
    const dataUrl = await resizeImage(file, 1600, 0.85);
    const base64  = dataUrl.split(',')[1];
    await getToken();
    const res     = await fetch(`${API_BASE}/ocr-ingredients`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ image_base64: base64, mime_type: 'image/jpeg' }),
    });

    showScreen('compare');

    if (!res.ok) {
      if (res.status === 401) { _handle401(); return; }
      const err = await res.json().catch(() => ({}));
      alert(err.detail || "Couldn't read the label. Please try a clearer photo.");
      return;
    }

    const data = await res.json();
    compareSlots[idx].ingredientsText = data.ingredients_text;
    const ta = document.getElementById(`slot-textarea-${idx}`);
    if (ta) {
      ta.value = data.ingredients_text;
      ta.classList.add('highlight');
      setTimeout(() => ta.classList.remove('highlight'), 1200);
      ta.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    const slotEl = document.getElementById(`slot-${idx}`);
    if (slotEl) slotEl.classList.add('has-ingredients');
    updateCompareBtn();
  } catch (e) {
    showScreen('compare');
    alert('Network error. Make sure the server is running.');
  }
}

function updateCompareBtn() {
  const filledSlots = compareSlots.filter(s => s.ingredientsText.trim().length > 0);
  const filled    = filledSlots.length;
  const allNamed  = filledSlots.every(s => s.name.trim().length > 0);
  const btn  = document.getElementById('compare-btn');
  const hint = document.getElementById('compare-hint');
  if (btn)  btn.disabled = filled < 2 || !allNamed;
  if (hint) hint.textContent = filled < 2
    ? `Add ingredients for at least 2 products (${filled} ready)`
    : !allNamed
    ? 'Please enter a product name for each product'
    : `${filled} product${filled > 1 ? 's' : ''} ready — tap Compare Now`;
}

async function runComparison() {
  const filledSlots = compareSlots.filter(s => s.ingredientsText.trim().length > 0);
  if (filledSlots.length < 2) { alert('Please add ingredients for at least 2 products.'); return; }
  const missingName = filledSlots.findIndex(s => !s.name.trim());
  if (missingName !== -1) {
    alert(`Please enter a product name for product ${missingName + 1}.`);
    return;
  }
  const products = filledSlots.map(s => ({
    name: s.name.trim(),
    ingredients_text: s.ingredientsText.trim(),
  }));

  showLoading('analyze', 'Comparing products…',
    `Analyzing ${products.length} products — this may take a minute`);

  try {
    await getToken();
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ products }),
    });

    if (!res.ok) {
      if (res.status === 401) { _handle401(); return; }
      const err = await res.json().catch(() => ({}));
      showScreen('compare');
      alert(err.detail || 'Comparison failed. Please try again.');
      return;
    }

    const data = await res.json();

    // Save compare result to history as a single entry
    const winVerdict = data.recommendation?.winner_verdict || 'clean';
    const winDotCls  = winVerdict === 'concerning' ? 'red' : winVerdict === 'caution' ? 'amber' : 'green';
    addToHistory({
      type:        'compare',
      names:       data.results.map(r => r.name),
      winner:      data.recommendation.winner_name,
      dotCls:      winDotCls,
      compareData: { results: data.results, recommendation: data.recommendation },
    });

    renderCompareResults(data);
  } catch (e) {
    showScreen('compare');
    alert('Network error. Make sure the server is running.');
  }
}

function renderCompareResults(data) {
  const { results, recommendation } = data;
  document.getElementById('compare-results-count').textContent = `${results.length} products compared`;

  // Spectrum recommendation card
  const resultMap = {};
  results.forEach(r => { resultMap[r.name] = r; });

  // scores is sorted ascending: index 0 = safest, last = most concerning
  const sortedByScore = recommendation.scores;
  const n = sortedByScore.length;

  function spectralColor(ratio, lightness = 58, alpha = 1) {
    // ratio 0 = green (hue 142), ratio 1 = red (hue 4)
    const hue = Math.round(142 - 138 * ratio);
    return `hsla(${hue}, 70%, ${lightness}%, ${alpha})`;
  }

  const VERDICT_LABELS_SHORT = { concerning: 'Flagged', caution: 'Caution', clean: 'Clean' };
  const arrowUp   = `<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>`;
  const arrowDown = `<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>`;
  // Gold crown SVG for winner badge
  const crownGold = `<svg width="16" height="16" viewBox="0 0 24 24" fill="#fbbf24" stroke="none" aria-hidden="true"><path d="M2 20h20v2H2v-2zM3 8l4.5 4.5L12 4l4.5 8.5L21 8v11H3V8z"/></svg>`;

  // Build gradient stops — vertical (top=safest/green, bottom=most concerning/red)
  const gradStops = sortedByScore.map((item, i) => {
    const ratio = n > 1 ? i / (n - 1) : 0;
    const pct = n > 1 ? Math.round((i / (n - 1)) * 100) : 0;
    return `${spectralColor(ratio, 16, 1)} ${pct}%`;
  }).join(', ');

  const cols = sortedByScore.map((item, i) => {
    const ratio = n > 1 ? i / (n - 1) : 0;
    const col       = spectralColor(ratio);
    const colBg     = spectralColor(ratio, 45, 0.18);
    const colBorder = spectralColor(ratio, 55, 0.35);
    const r = resultMap[item.name];
    const verdict  = r ? r.analysis.verdict : 'clean';
    const vLabel   = VERDICT_LABELS_SHORT[verdict] || verdict.toUpperCase();
    const isWinner = i === 0;
    const toxCount = r ? (r.analysis.total_toxicants_detected || 0) : 0;
    const toxLabel = toxCount === 0 ? 'No concerns' : `${toxCount} toxicant${toxCount > 1 ? 's' : ''}`;

    return `<div class="spectrum-col">
      <div class="spectrum-rank-wrap">
        ${isWinner ? `<span class="spectrum-winner-crown" aria-label="Safest product">${crownGold}</span>` : ''}
        <div class="spectrum-rank" style="color:${col};">#${i + 1}</div>
      </div>
      <div class="spectrum-name">${escHtml(item.name)}</div>
      <div class="spectrum-right">
        <div class="spectrum-verdict" style="color:${col}; background:${colBg}; border:1px solid ${colBorder};">${vLabel}</div>
        <div class="spectrum-score">${toxLabel}</div>
      </div>
    </div>`;
  }).join('');

  const bannerHtml = `
    <div class="spectrum-card" style="background: linear-gradient(to bottom, ${gradStops});">
      <div class="spectrum-axis-header">${arrowUp} Safest</div>
      <div class="spectrum-cols">${cols}</div>
      <div class="spectrum-axis-footer">${arrowDown} Most Flagged</div>
      <div class="spectrum-reason">${escHtml(recommendation.reason)}</div>
    </div>`;

  // Aggregate all toxicants across all products
  const toxicantMap = new Map();
  results.forEach((r, prodIdx) => {
    (r.analysis.detected_toxicants || []).forEach(t => {
      if (!toxicantMap.has(t.toxicant_key)) {
        toxicantMap.set(t.toxicant_key, { display_name: t.display_name, max_papers: 0, perProduct: {} });
      }
      const entry = toxicantMap.get(t.toxicant_key);
      entry.perProduct[prodIdx] = t;
      if (t.paper_count > entry.max_papers) entry.max_papers = t.paper_count;
    });
  });

  const sortedTox = [...toxicantMap.entries()].sort((a, b) => b[1].max_papers - a[1].max_papers);
  const winnerName = recommendation.winner_name;
  const TIER_LABELS = { high: 'HIGH', medium: 'MED', low: 'TRACE' };
  const VERDICT_COLORS = { concerning: 'var(--red)', caution: 'var(--amber)', clean: 'var(--green)' };
  const VERDICT_LABELS = { concerning: 'Flagged', caution: 'Caution', clean: 'Clean' };

  let tableHtml;
  if (sortedTox.length === 0) {
    tableHtml = `
      <div class="compare-table-section">
        <div class="clean-card" style="margin:0;">
          <div class="clean-icon">✓</div>
          <h3>All products are clean</h3>
          <p>None of the products matched our 15 toxicant categories.</p>
        </div>
      </div>`;
  } else {
    const headerCols = results.map((r, i) => {
      const isWinner = r.name === winnerName;
      return `<th class="product-col${isWinner ? ' winner-col' : ''}">${escHtml(r.name)}</th>`;
    }).join('');

    const bodyRows = sortedTox.map(([key, info]) => {
      const cells = results.map((r, prodIdx) => {
        const t = info.perProduct[prodIdx];
        if (!t) return `<td class="cell-none">—</td>`;
        return `<td class="cell-detected"><div class="cell-badge">
          <span class="cell-tier ${t.tier}">${TIER_LABELS[t.tier] || t.tier.toUpperCase()}</span>
          <span class="cell-papers">${t.paper_count} papers</span>
        </div></td>`;
      }).join('');
      return `<tr><td class="toxicant-name">${escHtml(info.display_name)}</td>${cells}</tr>`;
    }).join('');

    const verdictCells = results.map(r => {
      const vv = r.analysis ? r.analysis.verdict : 'clean';
      return `<td style="text-align:center;color:${VERDICT_COLORS[vv]};font-size:0.75rem;font-weight:800;">${VERDICT_LABELS[vv] || vv.toUpperCase()}</td>`;
    }).join('');
    const verdictRow = `<tr class="verdict-row"><td class="toxicant-name" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.4px;color:var(--text-muted);">Overall</td>${verdictCells}</tr>`;

    tableHtml = `
      <div class="compare-table-section">
        <h3>Side-by-Side Breakdown</h3>
        <div class="compare-table-wrap">
          <table class="compare-table" role="table">
            <thead><tr><th>Toxicant</th>${headerCols}</tr></thead>
            <tbody>${bodyRows}${verdictRow}</tbody>
          </table>
        </div>
      </div>`;
  }

  const actionsHtml = `
    <div class="compare-back-actions">
      <button class="btn btn-secondary btn-full" onclick="showScreen('compare')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Edit Products
      </button>
      <button class="btn btn-secondary btn-full" onclick="showScreen('home')">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        Start Over
      </button>
    </div>`;

  document.getElementById('compare-results-body').innerHTML = bannerHtml + tableHtml + actionsHtml;
  showScreen('compare-results');
}

// ── Share / Copy (Feature 4) ─────────────────────────────────────────────────
function buildSummaryText(label, analysis) {
  const v   = analysis ? analysis.verdict : 'clean';
  const VERDICT_LABELS = { concerning: 'Flagged', caution: 'Caution', clean: 'Clean' };
  const verdictLabel = VERDICT_LABELS[v] || 'Clean';
  const detected = analysis && analysis.detected_toxicants || [];
  let text = `CosmoTox Scan Result\n`;
  text += `Product: ${label || 'Ingredient Analysis'}\n`;
  text += `Verdict: ${verdictLabel}\n`;
  if (detected.length) {
    text += `\nConcerns found (${detected.length}):\n`;
    detected.forEach(t => {
      const tier = TIER_BADGE[t.tier] || TIER_BADGE.high;
      text += `\n• ${t.display_name} — ${tier.label} (${t.paper_count} research papers)\n`;
      text += `  Found as: ${(t.matched_ingredients || []).join(', ')}\n`;
      if (t.llm_summary) text += `  "${t.llm_summary}"\n`;
    });
  } else {
    text += `\nNo flagged ingredients found.\n`;
  }
  text += `\nScanned with CosmoTox on ${new Date().toLocaleDateString()}\n`;
  text += `Based on peer-reviewed research — not medical advice.`;
  return text;
}

async function shareResults() {
  const text = buildSummaryText(_currentResultLabel, _currentResultAnalysis);
  try {
    await navigator.share({ title: 'CosmoTox: ' + _currentResultLabel, text });
  } catch(e) { /* user cancelled or not supported */ }
}

async function copyResults() {
  const text = buildSummaryText(_currentResultLabel, _currentResultAnalysis);
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard');
  } catch(e) {
    showToast('Copy failed — please select text manually');
  }
}

let _toastTimer = null;
function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
}

// ── Watchlist (Feature 5) ────────────────────────────────────────────────────
const WATCHLIST_KEY = 'cosmotox_watchlist_v1';
const WATCHLIST_CATEGORIES = [
  { key: 'parabens',              label: 'Parabens' },
  { key: 'phthalates',            label: 'Phthalates' },
  { key: 'benzophenones',         label: 'Benzophenones (UV Filters)' },
  { key: 'siloxanes',             label: 'Siloxanes' },
  { key: 'fragrance',             label: 'Fragrance / Parfum' },
  { key: 'toluene',               label: 'Toluene' },
  { key: 'formaldehyde_releasers',label: 'Formaldehyde Releasers' },
  { key: 'heavy_metals',          label: 'Heavy Metals' },
  { key: 'hydroquinone',          label: 'Hydroquinone' },
  { key: 'ethanolamines',         label: 'Ethanolamines' },
  { key: 'bha_bht',               label: 'BHA / BHT' },
  { key: 'coal_tar',              label: 'Coal Tar Dyes' },
  { key: 'pfas',                  label: 'PFAS' },
  { key: 'triclosan',             label: 'Triclosan' },
  { key: 'dioxane',               label: '1,4-Dioxane' },
];

const ORGAN_WATCHLIST_KEY = 'cosmotox_watchlist_organs_v1';
const WATCHLIST_ORGANS = [
  { key: 'skin',         label: 'Skin',                  keywords: ['skin', 'dermal', 'dermatitis', 'epidermis', 'cutaneous'] },
  { key: 'liver',        label: 'Liver',                  keywords: ['liver', 'hepatic', 'hepato', 'hepatotoxic'] },
  { key: 'kidneys',      label: 'Kidneys',                keywords: ['kidney', 'renal', 'nephro'] },
  { key: 'brain',        label: 'Brain / Nervous System', keywords: ['brain', 'nervous', 'neuro', 'neural', 'cognitive', 'neurotoxic'] },
  { key: 'endocrine',    label: 'Endocrine / Hormones',   keywords: ['endocrine', 'hormone', 'estrogenic', 'androgenic', 'endocrine disrupt'] },
  { key: 'reproductive', label: 'Reproductive System',    keywords: ['reproductive', 'fertility', 'ovarian', 'testicular', 'uterine', 'sperm'] },
  { key: 'thyroid',      label: 'Thyroid',                keywords: ['thyroid'] },
  { key: 'lungs',        label: 'Lungs / Respiratory',    keywords: ['lung', 'respiratory', 'pulmonary', 'airway', 'bronch'] },
  { key: 'immune',       label: 'Immune System',          keywords: ['immune', 'allerg', 'sensitiz', 'immunotoxic'] },
  { key: 'eyes',         label: 'Eyes',                   keywords: ['eye', 'ocular', 'ophthalm'] },
];

const watchlist = (() => {
  try { return new Set(JSON.parse(localStorage.getItem(WATCHLIST_KEY) || '[]')); }
  catch(e) { return new Set(); }
})();

const organWatchlist = (() => {
  try { return new Set(JSON.parse(localStorage.getItem(ORGAN_WATCHLIST_KEY) || '[]')); }
  catch(e) { return new Set(); }
})();

function saveWatchlist() {
  try { localStorage.setItem(WATCHLIST_KEY, JSON.stringify([...watchlist])); } catch(e) {}
}

function saveOrganWatchlist() {
  try { localStorage.setItem(ORGAN_WATCHLIST_KEY, JSON.stringify([...organWatchlist])); } catch(e) {}
}

function toggleWatchlistItem(key) {
  const adding = !watchlist.has(key);
  if (adding) watchlist.add(key); else watchlist.delete(key);
  saveWatchlist();
  _syncWatchlistItem(key, 'toxicant', adding);
  renderWatchlistScreen();
}

function toggleOrganWatchlistItem(key) {
  const adding = !organWatchlist.has(key);
  if (adding) organWatchlist.add(key); else organWatchlist.delete(key);
  saveOrganWatchlist();
  _syncWatchlistItem(key, 'organ', adding);
  renderWatchlistScreen();
}

// Returns true if any of a toxicant's top_organs match the given organ key's keywords
function organMatchesToxicant(top_organs, organ_key) {
  const organ = WATCHLIST_ORGANS.find(o => o.key === organ_key);
  if (!organ || !top_organs) return false;
  return top_organs.some(org =>
    organ.keywords.some(kw => org.toLowerCase().includes(kw.toLowerCase()))
  );
}

function renderWatchlistScreen() {
  const grid = document.getElementById('watchlist-grid');
  const organGrid = document.getElementById('watchlist-organ-grid');
  const toxFilter = (document.getElementById('watchlist-toxicant-search') || {}).value || '';
  const orgFilter = (document.getElementById('watchlist-organ-search') || {}).value || '';
  if (!grid) return;

  const filteredTox = WATCHLIST_CATEGORIES.filter(cat =>
    cat.label.toLowerCase().includes(toxFilter.toLowerCase())
  );
  const filteredOrg = WATCHLIST_ORGANS.filter(cat =>
    cat.label.toLowerCase().includes(orgFilter.toLowerCase())
  );

  grid.innerHTML = filteredTox.map(cat => {
    const active = watchlist.has(cat.key);
    return `
      <button class="watchlist-chip${active ? ' active' : ''}"
              onclick="toggleWatchlistItem('${cat.key}')"
              aria-pressed="${active}" aria-label="${escHtml(cat.label)}">
        <span class="watchlist-check">${active ? '✓' : ''}</span>
        ${escHtml(cat.label)}
      </button>`;
  }).join('') || '<p style="color:var(--text-muted);font-size:0.8rem;padding:4px 0;">No matches</p>';

  if (organGrid) {
    organGrid.innerHTML = filteredOrg.map(cat => {
      const active = organWatchlist.has(cat.key);
      return `
        <button class="watchlist-chip${active ? ' active' : ''}"
                onclick="toggleOrganWatchlistItem('${cat.key}')"
                aria-pressed="${active}" aria-label="${escHtml(cat.label)}">
          <span class="watchlist-check">${active ? '✓' : ''}</span>
          ${escHtml(cat.label)}
        </button>`;
    }).join('') || '<p style="color:var(--text-muted);font-size:0.8rem;padding:4px 0;">No matches</p>';
  }
}

// ── Initialization ───────────────────────────────────────────────────────────
renderHistory();
renderWatchlistScreen();

// onAuthStateChange fires INITIAL_SESSION immediately on setup — including
// when the page loads from a confirmation-link redirect (#access_token in URL).
// This replaces the old IIFE + separate handler pattern.
_supabase.auth.onAuthStateChange(async (event, session) => {
  _session = session;
  if (event === 'INITIAL_SESSION') {
    if (session) {
      // Verify the session is still live server-side — catches deleted users
      const { data, error } = await _supabase.auth.getUser();
      if (error || !data.user) {
        await _supabase.auth.signOut();
        showScreen('login');
      } else {
        _onSignedIn();
      }
    } else {
      showScreen('login');
    }
  } else if (event === 'SIGNED_IN') {
    _onSignedIn();
  } else if (event === 'SIGNED_OUT') {
    _session = null;
    showScreen('login');
    document.getElementById('logout-btn').style.display = 'none';
    document.getElementById('history-btn').style.display = 'none';
  }
});

function _handle401() {
  _session = null;
  showScreen('login');
  const errEl = document.getElementById('login-error');
  errEl.textContent = 'Your session expired. Please sign in again.';
  errEl.style.display = 'block';
}
