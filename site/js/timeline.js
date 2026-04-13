/* timeline.js -- Sidebar timeline grouped by era */

const Timeline = {
  acts: [],

  init(acts) {
    this.acts = acts;
    this.render();
  },

  render() {
    const container = document.getElementById('timeline');
    const stats = document.getElementById('sidebar-stats');
    const acts = this.acts;

    stats.textContent = `${acts.length - 1} acts, 1790\u20132025`;

    // Group by era (using tags as boundaries)
    const eras = [];
    let currentEra = null;

    for (let i = 0; i < acts.length; i++) {
      const act = acts[i];
      if (act.tag || i === 0) {
        currentEra = {
          label: act.tag || 'Start',
          acts: [],
        };
        eras.push(currentEra);
      }
      if (currentEra) {
        currentEra.acts.push(act);
      }
    }

    container.innerHTML = eras.map((era, eraIdx) => `
      <div class="era-group">
        <div class="era-label" onclick="Timeline.toggleEra(${eraIdx})">
          <span>${App.esc(era.label)}</span>
          <span class="era-count">${era.acts.length}</span>
        </div>
        <div class="era-acts${eraIdx < eras.length - 3 ? ' collapsed' : ''}" id="era-${eraIdx}">
          ${era.acts.map(a => `
            <div class="timeline-item" data-hash="${a.hash}" onclick="location.hash='#/act/${a.hash}'">
              <span class="timeline-date">${(a.date || '').slice(0, 4)}</span>
              <span class="timeline-name" title="${App.esc(a.name)}">${App.esc(a.name)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  },

  toggleEra(idx) {
    const el = document.getElementById(`era-${idx}`);
    if (el) el.classList.toggle('collapsed');
  },

  setActive(hash) {
    // Remove old active
    document.querySelectorAll('.timeline-item.active').forEach(el => el.classList.remove('active'));
    // Set new active
    const item = document.querySelector(`.timeline-item[data-hash="${hash}"]`);
    if (item) {
      item.classList.add('active');
      // Expand parent era if collapsed
      const eraActs = item.closest('.era-acts');
      if (eraActs && eraActs.classList.contains('collapsed')) {
        eraActs.classList.remove('collapsed');
      }
      // Scroll into view
      item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  },
};
