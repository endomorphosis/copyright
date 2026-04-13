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
        <div style="margin-top:8px;display:flex;gap:16px;align-items:center">
          <a href="#/section/${secNum}" style="color:var(--accent);font-size:13px">&larr; Back to section</a>
          <a href="#/ramseyer/${secNum}/${effectiveA}/${effectiveB}" style="color:var(--accent);font-size:13px">View as Ramseyer (inline)</a>
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

  // Two-phase diff: Myers diff on lines, then word-level diff within changed lines
  wordDiff(textA, textB) {
    const linesA = textA.split('\n');
    const linesB = textB.split('\n');

    // Phase 1: diff lines using Myers algorithm
    const lineDiff = this.myers(linesA, linesB);

    let leftParts = [];
    let rightParts = [];

    // Phase 2: group consecutive del/ins lines and word-diff them
    let i = 0;
    while (i < lineDiff.length) {
      const op = lineDiff[i];
      if (op.type === 'equal') {
        leftParts.push(App.esc(op.text));
        rightParts.push(App.esc(op.text));
        i++;
      } else {
        // Collect consecutive del and ins
        const dels = [];
        const inss = [];
        while (i < lineDiff.length && lineDiff[i].type !== 'equal') {
          if (lineDiff[i].type === 'delete') dels.push(lineDiff[i].text);
          else inss.push(lineDiff[i].text);
          i++;
        }
        // Word-diff paired lines
        const pairs = Math.min(dels.length, inss.length);
        for (let p = 0; p < pairs; p++) {
          const { left, right } = this.wordDiffLine(dels[p], inss[p]);
          leftParts.push(left);
          rightParts.push(right);
        }
        // Remaining unpaired deletions
        for (let p = pairs; p < dels.length; p++) {
          leftParts.push(`<span class="word-del">${App.esc(dels[p])}</span>`);
        }
        // Remaining unpaired insertions
        for (let p = pairs; p < inss.length; p++) {
          rightParts.push(`<span class="word-add">${App.esc(inss[p])}</span>`);
        }
      }
    }

    return {
      leftHtml: leftParts.join('\n'),
      rightHtml: rightParts.join('\n'),
    };
  },

  // Word-level diff within a single changed line pair
  wordDiffLine(lineA, lineB) {
    const wordsA = lineA.split(/(\s+)/);
    const wordsB = lineB.split(/(\s+)/);
    const ops = this.myers(wordsA, wordsB);

    let left = '', right = '';
    for (const op of ops) {
      if (op.type === 'equal') {
        left += App.esc(op.text);
        right += App.esc(op.text);
      } else if (op.type === 'delete') {
        left += `<span class="word-del">${App.esc(op.text)}</span>`;
      } else {
        right += `<span class="word-add">${App.esc(op.text)}</span>`;
      }
    }
    return { left, right };
  },

  // Myers diff algorithm - produces minimal edit script
  myers(a, b) {
    const N = a.length, M = b.length;
    if (N === 0 && M === 0) return [];
    if (N === 0) return b.map(t => ({ type: 'insert', text: t }));
    if (M === 0) return a.map(t => ({ type: 'delete', text: t }));

    // For very large inputs, fall back to a simpler LCS to avoid memory issues
    if (N + M > 10000) return this.simpleDiff(a, b);

    const MAX = N + M;
    const size = 2 * MAX + 1;
    const vf = new Array(size).fill(0);
    const vb = new Array(size).fill(0);
    const trace = [];

    for (let d = 0; d <= MAX; d++) {
      // Record current state for backtracking
      trace.push(vf.slice());

      for (let k = -d; k <= d; k += 2) {
        const idx = k + MAX;
        let x;
        if (k === -d || (k !== d && vf[idx - 1] < vf[idx + 1])) {
          x = vf[idx + 1]; // move down
        } else {
          x = vf[idx - 1] + 1; // move right
        }
        let y = x - k;
        // Follow diagonal (equal elements)
        while (x < N && y < M && a[x] === b[y]) {
          x++;
          y++;
        }
        vf[idx] = x;
        if (x >= N && y >= M) {
          return this.buildResult(trace, a, b, N, M, MAX);
        }
      }
    }
    // Should not reach here
    return this.simpleDiff(a, b);
  },

  buildResult(trace, a, b, N, M, MAX) {
    const ops = [];
    let x = N, y = M;

    for (let d = trace.length - 1; d >= 0; d--) {
      const v = trace[d];
      const k = x - y;
      const idx = k + MAX;

      let prevK;
      if (k === -d || (k !== d && v[idx - 1] < v[idx + 1])) {
        prevK = k + 1; // came from above (insert)
      } else {
        prevK = k - 1; // came from left (delete)
      }

      const prevIdx = prevK + MAX;
      let prevX = d > 0 ? v[prevIdx] : 0;
      let prevY = prevX - prevK;

      // Diagonal (equal)
      while (x > prevX && y > prevY) {
        x--;
        y--;
        ops.push({ type: 'equal', text: a[x] });
      }

      if (d > 0) {
        if (k === -d || (k !== d && v[idx - 1] < v[idx + 1])) {
          // Insert
          y--;
          ops.push({ type: 'insert', text: b[y] });
        } else {
          // Delete
          x--;
          ops.push({ type: 'delete', text: a[x] });
        }
      }
    }

    ops.reverse();
    return ops;
  },

  // Fallback for very large inputs
  simpleDiff(a, b) {
    const ops = [];
    // Use hash-based line matching
    const bSet = new Map();
    b.forEach((line, idx) => {
      if (!bSet.has(line)) bSet.set(line, []);
      bSet.get(line).push(idx);
    });

    let j = 0;
    for (let i = 0; i < a.length; i++) {
      const positions = bSet.get(a[i]);
      if (positions) {
        const nextJ = positions.find(p => p >= j);
        if (nextJ !== undefined) {
          // Emit inserts for skipped b elements
          while (j < nextJ) {
            ops.push({ type: 'insert', text: b[j] });
            j++;
          }
          ops.push({ type: 'equal', text: a[i] });
          j++;
          continue;
        }
      }
      ops.push({ type: 'delete', text: a[i] });
    }
    while (j < b.length) {
      ops.push({ type: 'insert', text: b[j] });
      j++;
    }
    return ops;
  },
};
