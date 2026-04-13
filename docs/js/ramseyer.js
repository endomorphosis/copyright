/* ramseyer.js -- Inline redline view (Ramseyer format) */

const Ramseyer = {
  sectionData: null,
  strict: false,

  async render(secNum, hashA, hashB) {
    const el = document.getElementById('view-ramseyer');
    el.innerHTML = '<p>Loading...</p>';

    try {
    const data = await App.fetchJSON(`data/sections/${secNum}.json`);
    if (!data) {
      el.innerHTML = `<p>Section ${secNum} not found.</p>`;
      return;
    }

    this.sectionData = data;
    const versions = data.versions || [];

    const latestHash = versions.length ? versions[versions.length - 1].act_hash : null;
    const oldestHash = versions.length ? versions[0].act_hash : null;
    const effectiveA = hashA || oldestHash;
    const effectiveB = hashB || latestHash;
    const versionA = effectiveA ? versions.find(v => v.act_hash === effectiveA) : null;
    const versionB = effectiveB ? versions.find(v => v.act_hash === effectiveB) : null;
    const textA = versionA ? versionA.text : (versions[0]?.text || '');
    const textB = versionB ? versionB.text : (versions[versions.length - 1]?.text || '');
    const labelA = versionA ? versionA.act_name : (versions[0]?.act_name || 'Oldest');
    const labelB = versionB ? versionB.act_name : (versions[versions.length - 1]?.act_name || 'Latest');

    const ramseyerHtml = this.buildRamseyerHtml(textA, textB);

    el.innerHTML = `
      <div class="compare-header">
        <h1>&sect;${App.esc(secNum)} &mdash; Ramseyer Format</h1>
        <div style="margin-top:8px;display:flex;gap:16px;align-items:center">
          <a href="#/section/${secNum}" style="color:var(--accent);font-size:13px">&larr; Back to section</a>
          <a href="#/compare/${secNum}/${effectiveA}/${effectiveB}" style="color:var(--accent);font-size:13px">View side-by-side</a>
        </div>
      </div>

      <div class="compare-selectors">
        <div class="compare-side">
          <label>Before</label>
          <select id="ramseyer-select-a" onchange="Ramseyer.onChange('${secNum}')">
            ${versions.map((v, i) => `
              <option value="${v.act_hash}" ${v.act_hash === effectiveA ? 'selected' : ''}>
                ${App.esc(v.act_name)}${i === versions.length - 1 ? ' (current law)' : ''}
              </option>
            `).join('')}
          </select>
        </div>
        <div class="compare-side">
          <label>After</label>
          <select id="ramseyer-select-b" onchange="Ramseyer.onChange('${secNum}')">
            ${versions.map((v, i) => `
              <option value="${v.act_hash}" ${v.act_hash === effectiveB ? 'selected' : ''}>
                ${App.esc(v.act_name)}${i === versions.length - 1 ? ' (current law)' : ''}
              </option>
            `).join('')}
          </select>
        </div>
      </div>

      <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
        <div class="ramseyer-style-toggle">
          <button id="ramseyer-mode-strict" onclick="Ramseyer.setMode(true)" class="${this.strict ? 'active' : ''}">Congressional</button>
          <button id="ramseyer-mode-enhanced" onclick="Ramseyer.setMode(false)" class="${this.strict ? '' : 'active'}">Enhanced</button>
        </div>
        <div class="ramseyer-legend" id="ramseyer-legend">
          ${this.strict
            ? '<span><del class="ramseyer-del">Deleted text</del> (boldface brackets)</span><span><ins class="ramseyer-ins">inserted text</ins> (italic)</span>'
            : '<span><del class="ramseyer-del">Deleted text</del></span><span><ins class="ramseyer-ins">Inserted text</ins></span>'}
        </div>
      </div>

      <div class="statute-text ${this.strict ? 'ramseyer-strict' : ''}" id="ramseyer-body">${ramseyerHtml}</div>
    `;
    } catch (err) {
      el.innerHTML = `<p>Error: ${App.esc(err.message)}</p>`;
      console.error('Ramseyer render error:', err);
    }
  },

  setMode(strict) {
    this.strict = strict;
    const body = document.getElementById('ramseyer-body');
    const legend = document.getElementById('ramseyer-legend');
    const btnStrict = document.getElementById('ramseyer-mode-strict');
    const btnEnhanced = document.getElementById('ramseyer-mode-enhanced');
    if (body) body.classList.toggle('ramseyer-strict', strict);
    if (btnStrict) btnStrict.classList.toggle('active', strict);
    if (btnEnhanced) btnEnhanced.classList.toggle('active', !strict);
    if (legend) {
      legend.innerHTML = strict
        ? '<span><del class="ramseyer-del">Deleted text</del> (boldface brackets)</span><span><ins class="ramseyer-ins">inserted text</ins> (italic)</span>'
        : '<span><del class="ramseyer-del">Deleted text</del></span><span><ins class="ramseyer-ins">Inserted text</ins></span>';
    }
  },

  onChange(secNum) {
    const a = document.getElementById('ramseyer-select-a').value;
    const b = document.getElementById('ramseyer-select-b').value;
    location.hash = `#/ramseyer/${secNum}/${a}/${b}`;
  },

  buildRamseyerHtml(textA, textB) {
    const linesA = textA.split('\n');
    const linesB = textB.split('\n');
    const lineDiff = Compare.myers(linesA, linesB);

    const parts = [];
    let i = 0;

    while (i < lineDiff.length) {
      const op = lineDiff[i];
      if (op.type === 'equal') {
        parts.push(App.esc(op.text));
        i++;
      } else {
        const dels = [];
        const inss = [];
        while (i < lineDiff.length && lineDiff[i].type !== 'equal') {
          if (lineDiff[i].type === 'delete') dels.push(lineDiff[i].text);
          else inss.push(lineDiff[i].text);
          i++;
        }
        const pairs = Math.min(dels.length, inss.length);
        for (let p = 0; p < pairs; p++) {
          parts.push(this.ramseyerWordDiff(dels[p], inss[p]));
        }
        for (let p = pairs; p < dels.length; p++) {
          parts.push(`<del class="ramseyer-del">${App.esc(dels[p])}</del>`);
        }
        for (let p = pairs; p < inss.length; p++) {
          parts.push(`<ins class="ramseyer-ins">${App.esc(inss[p])}</ins>`);
        }
      }
    }

    return parts.join('\n');
  },

  ramseyerWordDiff(lineA, lineB) {
    const wordsA = lineA.split(/(\s+)/);
    const wordsB = lineB.split(/(\s+)/);
    const ops = Compare.myers(wordsA, wordsB);

    // Group consecutive same-type ops into single spans
    let result = '';
    let i = 0;
    while (i < ops.length) {
      const op = ops[i];
      if (op.type === 'equal') {
        result += App.esc(op.text);
        i++;
      } else {
        let buf = App.esc(op.text);
        const t = op.type;
        i++;
        while (i < ops.length && ops[i].type === t) {
          buf += App.esc(ops[i].text);
          i++;
        }
        if (t === 'delete') {
          result += `<del class="ramseyer-del">${buf}</del>`;
        } else {
          result += `<ins class="ramseyer-ins">${buf}</ins>`;
        }
      }
    }
    return result;
  },
};
