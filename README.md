# MemFold research website

Website: https://MemFold.github.io/

Repository: https://github.com/MemFold/memfold.github.io

A responsive research blog introducing the paper, with model-selectable benchmark
results, expandable figures, and arXiv, GitHub, and Hugging Face resource buttons. No build step,
external fonts, analytics, or JavaScript dependencies are required.

## Edit and preview

- `index.html`: article, authors, links, and initial results table.
- `styles.css`: desktop and mobile layout.
- `script.js`: model selector, figure viewer, and reading navigation.
- `assets/`: paper figures, the project logo, and institutional logos.

Run `python3 -m http.server 8000 --directory website` from the manuscript root,
or `python3 -m http.server 8000` from the standalone website repository.

## Deployment

GitHub Pages publishes the `main` branch, root folder. Push this directory's
contents to the website repository root; every push deploys automatically.
`.nojekyll` keeps the site as plain static files.

## Sources

Article text is adapted from the current manuscript. Benchmark values come from
`arxiv/main_table.tex`; ablations from `arxiv/5_ablation.tex`; the case and memory
analysis from `arxiv/5_discussion.tex`. Experimental plots are redrawn as page-styled SVG using the unchanged data in
`tools/figure-data.json`. `tools/render_figures.py` generates desktop and mobile
training plots plus memory analyses (requires matplotlib). Colors match the
page, text remains vector text, and mobile layouts stack the training panels.
The framework diagram retains its PNG rendering, as requested. The logo uses
SVG paths and gradients; figure zooms use the same SVG files as the article. The full manuscript PDF is not included in the public website.

The code link follows the manuscript's current repository URL. Update it when
the code repository moves. arXiv and Hugging Face remain disabled placeholders until their URLs are available.

## Figure fidelity and responsive presentation

Figures fill the content area to the right of the desktop reading outline.
All figure containers have transparent backgrounds and no borders. The framework
PNG has a transparent alpha channel. Its two full-page white vector background
paths were removed from the source PDF export; the remaining native drawing
instructions are preserved in `tools/framework-transparent.svg`. The two memory-analysis plots and budget
cost plot share a row and identical 367.2 × 298.8 SVG viewBoxes. On smaller
screens they stack vertically.

The Discussion figures include training efficiency, budget accuracy, budget
cost, memory reliance, and the personalization example. `tools/render_case.py`
extracts all three responses from `arxiv/5_discussion.tex` and lays out responsive
SVGs using website typography. It verifies each paragraph against the extracted
source. The standalone snapshot is `tools/case-text.json`. Keep every word,
punctuation mark, label, and answer token count unchanged when restyling.

The site uses a near-white background, neutral text and borders, and blue
accents. Figure enlargement is available by clicking the images, without
additional visible interface labels.

The desktop cover fills the first viewport. The article begins below the cover
divider. Institutional logos follow the supplied TAPS-DLM website layout;
logo provenance is recorded in `assets/logos/README.md`.
