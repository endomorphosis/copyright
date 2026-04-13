/* compare.js -- Side-by-side comparison with word-level diff */

const Compare = {
  sectionData: null,

  async render(secNum, hashA, hashB) {
    const el = document.getElementById('view-compare');
    el.innerHTML = '<p>Loading...</p>';

    const data = await App.fetchJSON(`data/sections/${secNum}.json`);
    if (!data) {
      el.innerHTML = `<p>Section ${secNum} not found.</p>`;
      return;
    }

    this.sectionData = data;
    const versions = data.versions || [];

    // Default: oldest for A, newest for B
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

    // Compute word-level diff
    const { leftHtml, rightHtml } = this.wordDiff(textA, textB);

    el.innerHTML = `
      <div class="compare-header">
        <h1>&sect;${App.esc(secNum)} &mdash; Compare Versions</h1>
        <div style="margin-top:8px">
          <a href="#/section/${secNum}" style="color:var(--accent);font-size:13px">&larr; Back to section</a>
        </div>
      </div>

      <div class="compare-selectors">
        <div class="compare-side">
          <label>Before</label>
          <select id="compare-select-a" onchange="Compare.onChange('${secNum}')">
            ${versions.map((v, i) => `
              <option value="${v.act_hash}" ${v.act_hash === effectiveA ? 'selected' : ''}>
                ${App.esc(v.act_name)}${i === versions.length - 1 ? ' (current law)' : ''}
              </option>
            `).join('')}
          </select>
        </div>
        <div class="compare-side">
          <label>After</label>
          <select id="compare-select-b" onchange="Compare.onChange('${secNum}')">
            ${versions.map((v, i) => `
              <option value="${v.act_hash}" ${v.act_hash === effectiveB ? 'selected' : ''}>
                ${App.esc(v.act_name)}${i === versions.length - 1 ? ' (current law)' : ''}
              </option>
            `).join('')}
          </select>
        </div>
      </div>

      <div class="compare-panes">
        <div class="compare-pane">
          <div class="compare-pane-header">${App.esc(labelA)}</div>
          <pre>${leftHtml}</pre>
        </div>
        <div class="compare-pane">
          <div class="compare-pane-header">${App.esc(labelB)}</div>
          <pre>${rightHtml}</pre>
        </div>
      </div>
    `;
  },

  onChange(secNum) {
    const a = document.getElementById('compare-select-a').value;
    const b = document.getElementById('compare-select-b').value;
    location.hash = `#/compare/${secNum}/${a}/${b}`;
  },

  // Simple word-level diff without external library
  wordDiff(textA, textB) {
    // Split into words preserving whitespace
    const wordsA = textA.split(/(\s+)/);
    const wordsB = textB.split(/(\s+)/);

    // Use a simple LCS-based diff on words
    const ops = this.diffWords(wordsA, wordsB);

    let leftParts = [];
    let rightParts = [];

    for (const op of ops) {
      if (op.type === 'equal') {
        leftParts.push(App.esc(op.text));
        rightParts.push(App.esc(op.text));
      } else if (op.type === 'delete') {
        leftParts.push(`<span class="word-del">${App.esc(op.text)}</span>`);
      } else if (op.type === 'insert') {
        rightParts.push(`<span class="word-add">${App.esc(op.text)}</span>`);
      }
    }

    return {
      leftHtml: leftParts.join(''),
      rightHtml: rightParts.join(''),
    };
  },

  // Simple diff algorithm for word arrays
  // Uses a greedy approach: walk both arrays, match common sequences
  diffWords(a, b) {
    const ops = [];
    let i = 0, j = 0;

    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) {
        ops.push({ type: 'equal', text: a[i] });
        i++;
        j++;
      } else {
        // Look ahead for a match
        const lookA = this.findNext(a, i + 1, b[j], 30);
        const lookB = this.findNext(b, j + 1, a[i], 30);

        if (lookA !== -1 && (lookB === -1 || (lookA - i) <= (lookB - j))) {
          // Delete words from A until we match
          while (i < lookA) {
            ops.push({ type: 'delete', text: a[i] });
            i++;
          }
        } else if (lookB !== -1) {
          // Insert words from B until we match
          while (j < lookB) {
            ops.push({ type: 'insert', text: b[j] });
            j++;
          }
        } else {
          // No nearby match found, consume one from each
          ops.push({ type: 'delete', text: a[i] });
          ops.push({ type: 'insert', text: b[j] });
          i++;
          j++;
        }
      }
    }

    // Remaining
    while (i < a.length) {
      ops.push({ type: 'delete', text: a[i] });
      i++;
    }
    while (j < b.length) {
      ops.push({ type: 'insert', text: b[j] });
      j++;
    }

    return ops;
  },

  findNext(arr, start, target, maxLook) {
    const end = Math.min(start + maxLook, arr.length);
    for (let k = start; k < end; k++) {
      if (arr[k] === target) return k;
    }
    return -1;
  },
};
