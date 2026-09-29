'use strict';
const methods = ['Full Text', 'xRAG', 'AutoCompressor', 'MemGen', 'GRPO', 'OPSD', 'MemFold'];
// Accuracy values transcribed from arxiv/main_table.tex. Null denotes no valid outputs.
const results = {
  '3b': {name: 'Qwen2.5-3B-Instruct', rows: [[46,21.9,12.9,26.6],[36,55.8,8.5,10.2],[32,30.5,null,null],[54,66.1,13.3,3.8],[68,58.4,11.3,26],[54,29.6,12.8,26.2],[70,88.4,19.9,32.4]]},
  '7b': {name: 'Qwen2.5-7B-Instruct', rows: [[60,24,14,25.4],[62,64.9,10.9,12.2],[66,30.7,null,9.6],[76,78.5,14.1,11],[70,62.2,14.1,25],[64,47.2,13.2,25],[88,94.4,14.1,36.8]]},
  '4b': {name: 'Qwen3-4B', rows: [[56,4.3,13.6,27.8],[66,65.2,2.8,6.6],[58,30.8,null,14.2],[56,65.7,12.3,10.4],[62,65.7,13.8,27.4],[74,39.5,13.8,26],[84,89.4,15.2,38.6]]}
};
const selector = document.querySelector('#backbone');
selector.addEventListener('change', () => {
  const selected = results[selector.value];
  const body = document.querySelector('#results-table tbody');
  body.replaceChildren(...selected.rows.map((values, i) => {
    const row = document.createElement('tr');
    if (i === 6) row.className = 'ours';
    const label = document.createElement('th'); label.scope = 'row'; label.textContent = methods[i]; row.append(label);
    values.forEach(value => {const cell = document.createElement('td'); cell.textContent = value === null ? '—' : value.toFixed(1); row.append(cell);});
    return row;
  }));
  document.querySelector('#results-table caption').textContent = `Benchmark accuracy for ${selected.name}`;
  const bestBaseline = Math.max(...selected.rows.slice(0, 6).map(row => row[1]));
  const accuracy = selected.rows[6][1];
  document.querySelector('#result-insight').textContent = `On PersonaMem-128K, MemFold reaches ${accuracy.toFixed(1)}% accuracy, ${(accuracy - bestBaseline).toFixed(1)} percentage points above the strongest baseline in this comparison.${selector.value === '7b' ? ' On PrefEval, it ties MemGen and GRPO at 14.1%.' : ''}`;
});
const dialog = document.querySelector('#image-dialog');
const expandedImage = document.querySelector('#expanded-image');
document.querySelectorAll('[data-zoom]').forEach(button => {
  button.addEventListener('click', () => {
    expandedImage.src = button.dataset.current || button.querySelector('img').currentSrc || button.dataset.zoom;
    expandedImage.alt = button.querySelector('img').alt;
    dialog.showModal();
  });
});
document.querySelector('#close-dialog').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {if (event.target === dialog) dialog.close();});
const progress = document.querySelector('#progress');
const links = [...document.querySelectorAll('.contents nav a')];
function updatePosition() {
  const available = document.documentElement.scrollHeight - innerHeight;
  progress.style.width = `${available > 0 ? Math.min(100, scrollY / available * 100) : 0}%`;
  let current = links[0];
  for (const link of links) {if (document.querySelector(link.hash).getBoundingClientRect().top <= 160) current = link;}
  for (const link of links) {
    link.classList.toggle('active', link === current);
    if (link === current) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
  }
}
let scheduled = false;
addEventListener('scroll', () => {if (!scheduled) {scheduled = true; requestAnimationFrame(() => {updatePosition(); scheduled = false;});}}, {passive:true});
addEventListener('resize', updatePosition);
updatePosition();

const copyBibtex = document.querySelector('#copy-bibtex');
copyBibtex.addEventListener('click', async () => {
  const code = document.querySelector('#bibtex-code');
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(code.textContent);
    copyBibtex.textContent = 'Copied';
    status.textContent = 'BibTeX copied to clipboard.';
    setTimeout(() => { copyBibtex.textContent = 'Copy BibTeX'; }, 2000);
  } catch {
    const range = document.createRange();
    range.selectNodeContents(code);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'BibTeX selected. Use your keyboard to copy it.';
  }
});

// Chart reveal: inline each plot SVG and sweep its data layer in from left to right.
const SVG_NS = 'http://www.w3.org/2000/svg';
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const ease = t => t < .5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;
let chartCount = 0;

function chartSource(button) {
  const img = button.querySelector('img');
  for (const source of button.querySelectorAll('source')) {
    if (!source.media || matchMedia(source.media).matches) return source.getAttribute('srcset');
  }
  return img.getAttribute('src');
}

// Matplotlib reuses ids across files; prefix them so several inline SVGs can coexist.
function scopeIds(text, prefix) {
  const ids = [...text.matchAll(/\sid="([^"]+)"/g)].map(match => match[1]);
  for (const id of new Set(ids)) {
    text = text.split(`id="${id}"`).join(`id="${prefix}${id}"`).split(`#${id})`).join(`#${prefix}${id})`).split(`"#${id}"`).join(`"#${prefix}${id}"`);
  }
  return text;
}

function prepareReveal(svg, prefix) {
  const width = svg.viewBox.baseVal.width;
  const height = svg.viewBox.baseVal.height;
  const defs = svg.querySelector('defs') || svg.insertBefore(document.createElementNS(SVG_NS, 'defs'), svg.firstChild);
  const sweeps = [];
  svg.querySelectorAll('g[id*="axes_"]').forEach((axes, index) => {
    const lines = [...axes.querySelectorAll('g[id*="line2d_"]')].filter(group => {
      const path = group.querySelector(':scope > path[clip-path]');
      return path && (path.getAttribute('d').match(/L/g) || []).length >= 2;
    });
    const data = [...lines, ...axes.querySelectorAll(':scope > g[id*="PathCollection_"]')];
    if (!data.length) return;
    const clipId = (lines[0]?.querySelector('path') || data[0].querySelector('[clip-path]'))?.getAttribute('clip-path')?.match(/#([^)]+)/)?.[1];
    const plot = clipId && svg.getElementById(clipId)?.querySelector('rect');
    const top = plot ? plot.y.baseVal.value : 0;
    const left = plot ? plot.x.baseVal.value - 10 : 0;
    // Value and series labels sit inside or beside the plot; the panel title sits above it.
    const labels = [...axes.querySelectorAll(':scope > g[id*="text_"]')].filter(label => {
      const box = label.getBBox();
      return box.y + box.height > top;
    });
    const clip = document.createElementNS(SVG_NS, 'clipPath');
    clip.id = `${prefix}reveal-${index}`;
    const rect = document.createElementNS(SVG_NS, 'rect');
    rect.setAttribute('x', left); rect.setAttribute('y', 0);
    rect.setAttribute('width', 0); rect.setAttribute('height', height);
    clip.append(rect); defs.append(clip);
    const layer = document.createElementNS(SVG_NS, 'g');
    layer.setAttribute('clip-path', `url(#${clip.id})`);
    axes.insertBefore(layer, data[0]);
    layer.append(...data, ...labels);
    sweeps.push({rect, span: width - left, delay: sweeps.length * 220});
  });
  return sweeps;
}

function playReveal(sweeps, duration = 1300) {
  const start = performance.now();
  const frame = now => {
    let running = false;
    for (const {rect, span, delay} of sweeps) {
      const t = Math.min(1, Math.max(0, (now - start - delay) / duration));
      rect.setAttribute('width', span * ease(t));
      if (t < 1) running = true;
    }
    if (running) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}

const revealObserver = 'IntersectionObserver' in window && new IntersectionObserver(entries => {
  for (const entry of entries) {
    if (!entry.isIntersecting) continue;
    revealObserver.unobserve(entry.target);
    entry.target.dataset.revealed = '';
    playReveal(entry.target.sweeps);
  }
}, {threshold: .4});

async function inlineChart(button) {
  const url = chartSource(button);
  if (button.dataset.current === url) return;
  try {
    const response = await fetch(url);
    if (!response.ok) return;
    const prefix = `c${++chartCount}-`;
    const svg = new DOMParser().parseFromString(scopeIds(await response.text(), prefix), 'image/svg+xml').documentElement;
    if (svg.nodeName !== 'svg') return;
    svg.removeAttribute('width'); svg.removeAttribute('height');
    svg.classList.add('chart-svg');
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', button.querySelector('img').alt);
    button.querySelector('svg.chart-svg')?.remove();
    button.append(svg);
    button.classList.add('chart-inline');
    button.dataset.current = url;
    const wasRevealed = 'revealed' in button.dataset;
    const sweeps = prepareReveal(svg, prefix);
    if (reducedMotion.matches || wasRevealed || !revealObserver) {
      sweeps.forEach(({rect, span}) => rect.setAttribute('width', span));
    } else {
      button.sweeps = sweeps;
      revealObserver.observe(button);
    }
  } catch {
    // Keep the static image if the SVG cannot be inlined.
  }
}

const charts = [...document.querySelectorAll('[data-chart]')];
charts.forEach(inlineChart);
matchMedia('(max-width: 600px)').addEventListener('change', () => charts.forEach(inlineChart));
