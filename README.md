# MLIR/CIRCT Summer School Quarto Deck

The active presentation is `mlir-circt-summer-school.qmd`. Quarto is configured
to render only this file and to place generated output in `dist/`.

## Project layout

- `assets/`: source and rendered visual assets
- `styles/`: general, shared-code, MLIR, and Python stylesheets
- `syntax/`: custom Pandoc syntax definitions
- `filters/`: Pandoc filters used by the active deck
- `references/`: course program and supporting documents
- `dist/`: generated presentation ready to open or distribute, ignored by Git
- `tmp/`: temporary notebooks and scratch files, ignored by Git

## Generated output

`dist` is short for **distribution**. It contains the final files produced from
the source deck, including `reveal.html`, Reveal.js dependencies, stylesheets,
and the background image.

Files in `dist/` should not be edited directly because the next render can
replace them. The directory can be deleted safely and recreated with
`quarto render`.

## Render

The Python environment used by Quarto must be able to import `circt`.

```bash
quarto render
```

The presentation is written to `dist/reveal.html`.

For live preview:

```bash
quarto preview mlir-circt-summer-school.qmd --to revealjs
```

There is currently no automated test suite. A successful `quarto render` is the
project's build check.
