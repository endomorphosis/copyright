/* search.js -- Client-side search over acts and sections */

const Search = {
  acts: [],
  sections: [],

  init(acts, sectionsIndex) {
    this.acts = acts;
    this.sections = Object.entries(sectionsIndex).map(([num, info]) => ({
      num,
      title: info.title,
      amendment_count: info.amendment_count,
    }));

    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      if (q.length < 2) {
        results.classList.add('hidden');
        return;
      }
      this.showResults(q);
    });

    input.addEventListener('focus', () => {
      if (input.value.trim().length >= 2) {
        results.classList.remove('hidden');
      }
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!e.target.closest('#search-box')) {
        results.classList.add('hidden');
      }
    });

    // Navigate on Enter
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const first = results.querySelector('.search-item');
        if (first) first.click();
      }
    });
  },

  showResults(query) {
    const results = document.getElementById('search-results');

    // Search acts
    const actMatches = this.acts.filter(a =>
      a.name.toLowerCase().includes(query) ||
      (a.public_law || '').toLowerCase().includes(query) ||
      (a.citation || '').toLowerCase().includes(query) ||
      (a.summary || '').toLowerCase().includes(query)
    ).slice(0, 8);

    // Search sections
    const sectionMatches = this.sections.filter(s =>
      s.num.includes(query) ||
      s.title.toLowerCase().includes(query)
    ).slice(0, 8);

    if (actMatches.length === 0 && sectionMatches.length === 0) {
      results.innerHTML = '<div class="search-item" style="color:var(--text-muted)">No results</div>';
      results.classList.remove('hidden');
      return;
    }

    let html = '';

    if (sectionMatches.length > 0) {
      html += '<div class="search-group-label">Sections</div>';
      html += sectionMatches.map(s => `
        <div class="search-item" onclick="location.hash='#/section/${s.num}'; document.getElementById('search-results').classList.add('hidden')">
          <strong>&sect;${App.esc(s.num)}</strong> ${App.esc(s.title)}
          <div class="search-meta">${s.amendment_count} version${s.amendment_count !== 1 ? 's' : ''}</div>
        </div>
      `).join('');
    }

    if (actMatches.length > 0) {
      html += '<div class="search-group-label">Acts</div>';
      html += actMatches.map(a => `
        <div class="search-item" onclick="location.hash='#/act/${a.hash}'; document.getElementById('search-results').classList.add('hidden')">
          <strong>${App.esc(a.name)}</strong>
          <div class="search-meta">${a.date || ''} ${a.public_law ? '&middot; ' + App.esc(a.public_law) : ''}</div>
        </div>
      `).join('');
    }

    results.innerHTML = html;
    results.classList.remove('hidden');
  },
};
