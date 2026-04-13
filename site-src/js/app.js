/* app.js -- Core application: data loading, routing, state */

const App = {
  acts: [],
  sectionsIndex: {},
  cache: {},  // Cache for on-demand JSON loads

  async init() {
    // Load core data
    const [acts, sectionsIndex] = await Promise.all([
      this.fetchJSON('data/acts.json'),
      this.fetchJSON('data/sections_index.json'),
    ]);
    this.acts = acts;
    this.sectionsIndex = sectionsIndex;

    // Initialize components
    Timeline.init(acts);
    Search.init(acts, sectionsIndex);

    // Set up routing
    window.addEventListener('hashchange', () => this.route());
    this.route();
  },

  async fetchJSON(path) {
    if (this.cache[path]) return this.cache[path];
    const resp = await fetch(path);
    if (!resp.ok) return null;
    const data = await resp.json();
    this.cache[path] = data;
    return data;
  },

  route() {
    const hash = location.hash.slice(1) || '/';
    const parts = hash.split('/').filter(Boolean);

    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));

    if (parts[0] === 'act' && parts[1]) {
      this.showView('view-act');
      ActView.render(parts[1]);
    } else if (parts[0] === 'section' && parts[1]) {
      this.showView('view-section');
      SectionViewer.render(parts[1], parts[2] || null);
    } else if (parts[0] === 'compare' && parts[1]) {
      this.showView('view-compare');
      Compare.render(parts[1], parts[2] || null, parts[3] || null);
    } else if (parts[0] === 'ramseyer' && parts[1]) {
      this.showView('view-ramseyer');
      Ramseyer.render(parts[1], parts[2] || null, parts[3] || null);
    } else if (parts[0] === 'asof') {
      this.showView('view-asof');
      AsOfView.render(parts[1] || null);
    } else {
      this.showView('view-home');
      HomeView.render();
    }
  },

  showView(id) {
    document.getElementById(id).classList.remove('hidden');
  },

  // Find an act by short hash
  findAct(hash) {
    return this.acts.find(a => a.hash === hash || a.full_hash === hash);
  },

  // Find act index
  findActIndex(hash) {
    return this.acts.findIndex(a => a.hash === hash || a.full_hash === hash);
  },

  // Escape HTML
  esc(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  },
};


/* === Home View === */
const HomeView = {
  render() {
    const el = document.getElementById('view-home');

    // Compute era info
    const eras = this.computeEras();
    const topSections = this.topAmended(15);
    const unamended = this.neverAmended();

    el.innerHTML = `
      <div class="home-section">
        <h2>235 Years of Copyright Law</h2>
        <p>${App.acts.length - 1} legislative acts from 1790 to 2025, each recorded as a git commit.
           Browse the timeline, explore individual sections, or compare versions side by side.</p>
        <a href="#/asof" class="asof-link">View the law at any date &rarr;</a>
      </div>

      <div class="home-section">
        <h2>Major Eras</h2>
        <div class="era-cards">${eras.map(e => `
          <div class="era-card" onclick="location.hash='#/act/${e.startHash}'">
            <div class="era-card-tag">${App.esc(e.tag)}</div>
            <div class="era-card-dates">${e.dateRange}</div>
            <div class="era-card-count">${e.count} acts</div>
          </div>
        `).join('')}</div>
      </div>

      <div class="home-section">
        <h2>Legislative Activity by Decade</h2>
        <p>Number of acts passed and distinct sections amended per decade.</p>
        <div class="decade-chart">${this.decadeData().map(d => `
          <div class="decade-row">
            <div class="decade-label">${App.esc(d.label)}</div>
            <div class="decade-bars">
              <div class="decade-bar-group">
                <div class="decade-bar acts-bar" style="width: ${d.actsPct}%" title="${d.acts} acts"></div>
                <span class="decade-val">${d.acts}</span>
              </div>
              <div class="decade-bar-group">
                <div class="decade-bar sections-bar" style="width: ${d.secPct}%" title="${d.sections} sections"></div>
                <span class="decade-val">${d.sections}</span>
              </div>
            </div>
          </div>
        `).join('')}</div>
        <div class="decade-legend">
          <span class="legend-item"><span class="legend-swatch acts-swatch"></span> Acts passed</span>
          <span class="legend-item"><span class="legend-swatch sections-swatch"></span> Sections amended</span>
        </div>
      </div>

      <div class="home-section">
        <h2>Most Amended Sections</h2>
        <div class="bar-chart">${topSections.map(s => {
          const dates = this.amendmentDates(s.num);
          const sparkline = this.sparklineSVG(dates);
          return `
          <div class="bar-row" onclick="location.hash='#/section/${s.num}'">
            <div class="bar-label">&sect;${App.esc(s.num)}</div>
            <div class="bar-track">
              <div class="bar-fill" style="width: ${(s.count / topSections[0].count) * 100}%"></div>
            </div>
            <div class="bar-sparkline">${sparkline}</div>
            <div class="bar-count">${s.count}</div>
          </div>`;
        }).join('')}</div>
      </div>

      <div class="home-section">
        <h2>All Sections</h2>
        <div class="section-list">${this.allSections().map(s => `
          <div class="section-list-item" onclick="location.hash='#/section/${s.num}'">
            <span class="sec-num">&sect;${App.esc(s.num)}</span>
            <span class="sec-title">${App.esc(s.title)}</span>
          </div>
        `).join('')}</div>
      </div>
    `;
  },

  computeEras() {
    const tagActs = App.acts.filter(a => a.tag);
    const eras = [];
    for (let i = 0; i < tagActs.length; i++) {
      const start = tagActs[i];
      const startIdx = App.findActIndex(start.hash);
      const endIdx = i + 1 < tagActs.length
        ? App.findActIndex(tagActs[i + 1].hash)
        : App.acts.length;
      const count = endIdx - startIdx;
      const endAct = App.acts[endIdx - 1];
      eras.push({
        tag: start.tag,
        startHash: start.hash,
        dateRange: `${start.date?.slice(0, 4) || '?'} \u2013 ${endAct?.date?.slice(0, 4) || 'present'}`,
        count,
      });
    }
    return eras;
  },

  topAmended(n) {
    return Object.entries(App.sectionsIndex)
      .map(([num, info]) => ({ num, count: info.amendment_count, title: info.title }))
      .sort((a, b) => b.count - a.count)
      .slice(0, n);
  },

  neverAmended() {
    return Object.entries(App.sectionsIndex)
      .filter(([, info]) => info.amendment_count <= 1)
      .map(([num, info]) => ({ num, title: info.title }));
  },

  decadeData() {
    const decades = {};
    // Skip the initial "scaffold" commit (index 0) which has no date or is the base
    for (const act of App.acts) {
      if (!act.date) continue;
      const decade = act.date.slice(0, 3) + '0s';
      if (!decades[decade]) decades[decade] = { acts: 0, sectionsSet: new Set() };
      decades[decade].acts++;
      if (act.sections_affected) {
        for (const s of act.sections_affected) decades[decade].sectionsSet.add(s);
      }
    }
    const rows = Object.entries(decades)
      .map(([label, d]) => ({ label, acts: d.acts, sections: d.sectionsSet.size }))
      .sort((a, b) => a.label.localeCompare(b.label));
    const maxActs = Math.max(...rows.map(r => r.acts), 1);
    const maxSec = Math.max(...rows.map(r => r.sections), 1);
    for (const r of rows) {
      r.actsPct = (r.acts / maxActs) * 100;
      r.secPct = (r.sections / maxSec) * 100;
    }
    return rows;
  },

  amendmentDates(secNum) {
    return App.acts
      .filter(a => a.sections_affected && a.sections_affected.includes(secNum))
      .map(a => ({ date: a.date, name: a.name }));
  },

  sparklineSVG(dates) {
    if (!dates.length) return '';
    const w = 120, h = 16, r = 2.5;
    const minYear = 1976, maxYear = 2025;
    const dots = dates.map(d => {
      const year = parseInt(d.date);
      const x = ((year - minYear) / (maxYear - minYear)) * (w - 2 * r) + r;
      return `<circle cx="${x}" cy="${h / 2}" r="${r}" fill="var(--accent)" opacity="0.7"><title>${App.esc(d.name)} (${d.date})</title></circle>`;
    }).join('');
    return `<svg width="${w}" height="${h}" class="sparkline">${dots}</svg>`;
  },

  allSections() {
    return Object.entries(App.sectionsIndex)
      .map(([num, info]) => ({ num, title: info.title }))
      .sort((a, b) => {
        const na = parseInt(a.num), nb = parseInt(b.num);
        if (na !== nb) return na - nb;
        return a.num.localeCompare(b.num);
      });
  },
};


/* === Act Detail View === */
const ActView = {
  async render(hash) {
    const el = document.getElementById('view-act');
    const act = App.findAct(hash);
    if (!act) {
      el.innerHTML = '<p>Act not found.</p>';
      return;
    }

    // Mark active in timeline
    Timeline.setActive(hash);

    // Find prev/next
    const idx = App.findActIndex(hash);
    const prev = idx > 0 ? App.acts[idx - 1] : null;
    const next = idx < App.acts.length - 1 ? App.acts[idx + 1] : null;

    // Render header immediately
    el.innerHTML = `
      <div class="act-header">
        <h1>${App.esc(act.name)}</h1>
        <div class="act-meta">
          ${act.date ? `<span><strong>Date:</strong> ${App.esc(act.date)}</span>` : ''}
          ${act.public_law ? `<span><strong>Public Law:</strong> ${App.esc(act.public_law)}</span>` : ''}
          ${act.citation ? `<span><strong>Citation:</strong> ${App.esc(act.citation)}</span>` : ''}
        </div>
        ${act.summary ? `<div class="act-summary">${App.esc(act.summary)}</div>` : ''}
        <div class="act-nav">
          ${prev ? `<a href="#/act/${prev.hash}">&larr; ${App.esc(prev.name)}</a>` : '<span></span>'}
          ${next ? `<a href="#/act/${next.hash}">${App.esc(next.name)} &rarr;</a>` : '<span></span>'}
        </div>
      </div>
      ${act.sections_affected && act.sections_affected.length ? `
        <div>
          <strong>Sections affected:</strong>
          <div class="sections-affected">
            ${act.sections_affected.map(s => `<a class="section-chip" href="#/section/${s}">&sect;${App.esc(s)}</a>`).join('')}
          </div>
        </div>
      ` : ''}
      <div id="act-diff">Loading diff...</div>
    `;

    // Load diff
    const diff = await App.fetchJSON(`data/diffs/${hash}.json`);
    const diffEl = document.getElementById('act-diff');
    if (diff && diff.files && diff.files.length > 0) {
      diffEl.innerHTML = DiffViewer.render(diff.files);
    } else if (act.sections_expected && act.sections_expected.length > 0) {
      diffEl.innerHTML = `
        <div style="padding:20px; background:var(--bg-alt); border-radius:6px; border:1px solid var(--border)">
          <strong>Text changes not yet reconstructed.</strong>
          <p style="color:var(--text-muted); margin-top:8px">
            This act amends ${act.sections_expected.length} section${act.sections_expected.length !== 1 ? 's' : ''}
            of Title 17, but the historical text snapshots have not been built yet.
          </p>
          <div style="margin-top:8px">
            <strong>Expected sections:</strong>
            <div class="sections-affected" style="margin-top:6px">
              ${act.sections_expected.map(s => `<a class="section-chip" href="#/section/${s}">&sect;${App.esc(s)}</a>`).join('')}
            </div>
          </div>
        </div>
      `;
    } else {
      diffEl.innerHTML = `
        <div style="padding:20px; background:var(--bg-alt); border-radius:6px; border:1px solid var(--border)">
          <strong>This act did not directly amend the text of Title 17.</strong>
          <p style="color:var(--text-muted); margin-top:8px">
            It may have directed agency action, authorized studies, or amended other titles of the US Code.
          </p>
        </div>
      `;
    }
  },
};


/* === Point-in-Time View === */
const AsOfView = {
  render(dateStr) {
    const el = document.getElementById('view-asof');

    // Default to a useful date if none provided
    if (!dateStr) {
      dateStr = '1998-10-28'; // day after DMCA
    }

    // Find the last act on or before this date
    const actsBeforeDate = App.acts.filter(a => a.date && a.date <= dateStr);
    const lastAct = actsBeforeDate.length ? actsBeforeDate[actsBeforeDate.length - 1] : null;

    // Collect all sections that existed by this date
    const allSections = Object.entries(App.sectionsIndex)
      .map(([num, info]) => ({ num, title: info.title }))
      .sort((a, b) => {
        const na = parseInt(a.num), nb = parseInt(b.num);
        if (na !== nb) return na - nb;
        return a.num.localeCompare(b.num);
      });

    el.innerHTML = `
      <div class="asof-header">
        <h1>Title 17 as of a Given Date</h1>
        <p class="asof-desc">See every section of copyright law as it existed on a specific date.</p>
        <div class="asof-picker">
          <label for="asof-date">Date:</label>
          <input type="date" id="asof-date" value="${App.esc(dateStr)}"
                 min="1790-05-31" max="2025-12-31"
                 onchange="AsOfView.onDateChange()">
        </div>
        ${lastAct ? `
          <div class="asof-context">
            Showing law after <a href="#/act/${lastAct.hash}">${App.esc(lastAct.name)}</a>
            <span class="asof-context-date">(${App.esc(lastAct.date)})</span>
          </div>
        ` : `
          <div class="asof-context">No acts found before this date.</div>
        `}
      </div>
      <div class="asof-sections" id="asof-sections">
        ${allSections.map(s => `
          <div class="asof-section" id="asof-sec-${s.num}">
            <div class="asof-section-header" onclick="AsOfView.toggleSection('${s.num}', '${dateStr}')">
              <span class="asof-toggle">+</span>
              <span class="asof-sec-num">&sect;${App.esc(s.num)}</span>
              <span class="asof-sec-title">${App.esc(s.title)}</span>
            </div>
            <div class="asof-section-body hidden" id="asof-body-${s.num}"></div>
          </div>
        `).join('')}
      </div>
    `;
  },

  onDateChange() {
    const input = document.getElementById('asof-date');
    if (input && input.value) {
      location.hash = `#/asof/${input.value}`;
    }
  },

  async toggleSection(secNum, dateStr) {
    const body = document.getElementById(`asof-body-${secNum}`);
    const header = body.previousElementSibling;
    const toggle = header.querySelector('.asof-toggle');

    if (!body.classList.contains('hidden')) {
      body.classList.add('hidden');
      toggle.textContent = '+';
      return;
    }

    // Show loading state
    body.classList.remove('hidden');
    toggle.textContent = '\u2212';
    body.innerHTML = '<p class="asof-loading">Loading...</p>';

    const data = await App.fetchJSON(`data/sections/${secNum}.json`);
    if (!data || !data.versions || !data.versions.length) {
      body.innerHTML = '<p class="asof-no-text">No text available for this section.</p>';
      return;
    }

    // Find the latest version whose act date <= target date
    let matchedVersion = null;
    for (const v of data.versions) {
      const act = App.findAct(v.act_hash);
      if (act && act.date && act.date <= dateStr) {
        matchedVersion = v;
      }
    }

    if (!matchedVersion) {
      body.innerHTML = '<p class="asof-no-text">This section did not yet exist on ' + App.esc(dateStr) + '.</p>';
      return;
    }

    const act = App.findAct(matchedVersion.act_hash);
    body.innerHTML = `
      <div class="asof-version-info">
        Version from <a href="#/act/${matchedVersion.act_hash}">${App.esc(act ? act.name : matchedVersion.act_name)}</a>
        ${act ? `<span class="asof-context-date">(${App.esc(act.date)})</span>` : ''}
        &mdash; <a href="#/section/${secNum}/${matchedVersion.act_hash}">View in section viewer</a>
      </div>
      <div class="statute-text asof-text">${App.esc(matchedVersion.text)}</div>
    `;
  },
};


// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
