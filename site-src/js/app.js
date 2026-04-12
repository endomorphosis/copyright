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
        <h2>Most Amended Sections</h2>
        <div class="bar-chart">${topSections.map(s => `
          <div class="bar-row" onclick="location.hash='#/section/${s.num}'">
            <div class="bar-label">&sect;${App.esc(s.num)}</div>
            <div class="bar-track">
              <div class="bar-fill" style="width: ${(s.count / topSections[0].count) * 100}%"></div>
            </div>
            <div class="bar-count">${s.count}</div>
          </div>
        `).join('')}</div>
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


// Boot
document.addEventListener('DOMContentLoaded', () => App.init());
