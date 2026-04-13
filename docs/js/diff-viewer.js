/* diff-viewer.js -- Renders unified diffs from pre-computed JSON */

const DiffViewer = {
  render(files) {
    if (!files || files.length === 0) return '';

    return files.map(file => {
      const hunksHtml = (file.hunks || []).map(hunk => {
        const linesHtml = (hunk.lines || []).map(line => {
          const type = line.type;
          const prefix = type === 'add' ? '+' : type === 'del' ? '-' : ' ';
          const cls = type === 'add' ? 'add' : type === 'del' ? 'del' : 'ctx';
          return `<div class="diff-line ${cls}"><span class="line-prefix">${prefix}</span>${App.esc(line.text)}</div>`;
        }).join('');
        return `<div class="diff-hunk">${linesHtml}</div>`;
      }).join('');

      return `
        <div class="diff-file">
          <div class="diff-file-header">${App.esc(file.path)}</div>
          ${hunksHtml}
        </div>
      `;
    }).join('');
  },
};
