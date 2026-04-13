/* section-viewer.js -- Browse a section's text at any version */

const SectionViewer = {
  currentData: null,

  async render(secNum, selectedHash) {
    const el = document.getElementById('view-section');
    el.innerHTML = '<p>Loading section...</p>';

    const data = await App.fetchJSON(`data/sections/${secNum}.json`);
    if (!data) {
      el.innerHTML = `<p>Section ${secNum} not found.</p>`;
      return;
    }

    this.currentData = data;
    const versions = data.versions || [];
    // Default to showing the most recent version (= current law)
    const latestHash = versions.length ? versions[versions.length - 1].act_hash : null;
    const effectiveHash = selectedHash || latestHash;
    const selectedVersion = effectiveHash
      ? versions.find(v => v.act_hash === effectiveHash)
      : null;
    const displayText = selectedVersion ? selectedVersion.text : data.current_text;

    el.innerHTML = `
      <div class="section-header">
        <h1>&sect;${App.esc(secNum)}</h1>
        <div class="section-title-line">${App.esc(data.title)}</div>
      </div>

      <div class="version-selector">
        <label for="version-select">Version:</label>
        <select id="version-select" onchange="SectionViewer.onVersionChange('${secNum}')">
          ${versions.slice().reverse().map((v, i) => `
            <option value="${v.act_hash}" ${v.act_hash === effectiveHash ? 'selected' : ''}>
              ${App.esc(v.act_name)}${i === 0 ? ' (current law)' : ''}
            </option>
          `).join('')}
        </select>
        ${versions.length >= 2 ? `
          <button class="compare-btn" onclick="SectionViewer.openCompare('${secNum}')">
            Compare versions
          </button>
          <button class="compare-btn" onclick="SectionViewer.openRamseyer('${secNum}')">
            Ramseyer format
          </button>
        ` : ''}
        <button class="compare-btn cite-btn" onclick="SectionViewer.copyCitation('${secNum}')">
          Copy citation
        </button>
      </div>

      <div class="statute-text" id="statute-text">${App.esc(displayText)}</div>

      <div class="amendment-history">
        <h3>Amendment History (${versions.length} version${versions.length !== 1 ? 's' : ''})</h3>
        <ul class="amendment-list">
          ${versions.map(v => `
            <li>
              <span class="amend-marker"></span>
              <a href="#/act/${v.act_hash}">${App.esc(v.act_name)}</a>
            </li>
          `).join('')}
        </ul>
      </div>
    `;
  },

  onVersionChange(secNum) {
    const select = document.getElementById('version-select');
    const hash = select.value;
    if (hash) {
      location.hash = `#/section/${secNum}/${hash}`;
    } else {
      location.hash = `#/section/${secNum}`;
    }
  },

  openCompare(secNum) {
    const data = this.currentData;
    if (!data || !data.versions || data.versions.length < 2) return;
    const versions = data.versions;
    // Default: compare the two most recent versions
    const older = versions[versions.length - 2].act_hash;
    const newer = versions[versions.length - 1].act_hash;
    location.hash = `#/compare/${secNum}/${older}/${newer}`;
  },

  copyCitation(secNum) {
    const select = document.getElementById('version-select');
    const selectedHash = select ? select.value : null;
    const act = selectedHash ? App.findAct(selectedHash) : null;
    const versions = this.currentData ? this.currentData.versions || [] : [];
    const isLatest = selectedHash === (versions.length ? versions[versions.length - 1].act_hash : null);

    let citation = `17 U.S.C. \u00A7 ${secNum}`;
    if (act && !isLatest) {
      citation += ` (as amended by ${act.name}, ${act.date})`;
    }
    citation += `\n${window.location.href}`;

    navigator.clipboard.writeText(citation).then(() => {
      const btn = document.querySelector('.cite-btn');
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
      }
    });
  },

  openRamseyer(secNum) {
    const data = this.currentData;
    if (!data || !data.versions || data.versions.length < 2) return;
    const versions = data.versions;
    // Find the selected version and its predecessor
    const select = document.getElementById('version-select');
    const selectedHash = select ? select.value : null;
    const idx = selectedHash ? versions.findIndex(v => v.act_hash === selectedHash) : versions.length - 1;
    const prevIdx = idx > 0 ? idx - 1 : 0;
    const older = versions[prevIdx].act_hash;
    const newer = versions[idx >= 0 ? idx : versions.length - 1].act_hash;
    location.hash = `#/ramseyer/${secNum}/${older}/${newer}`;
  },
};
