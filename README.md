# MLIR/CIRCT Summer School 2026

This repository keeps the developing course material and the CIRCT programming
exercise in one place. `my_plan.md` is the source for what the talk should say;
the canonical Quarto deck is being rebuilt from it one section at a time. The
previous full prototype remains in `mlir-circt-summer-school-old.qmd` as a
reference for content and layouts, but Quarto does not render it.

The project retains two render profiles for the later exercises:

- `student`: exercise prompts without answers;
- `instructor`: the same slides with answers revealed as fragments.

## File hierarchy

```text
.
|-- mlir-circt-summer-school.qmd   # Canonical, incremental slide source
|-- mlir-circt-summer-school-old.qmd # Archived prototype; not rendered
|-- my_plan.md                     # Personal content and speaking ideas
|-- slides/motivation.qmd          # Geometry-to-logic opening narrative
|-- slides/digital-design.qmd      # Digital-design refresher chapter
|-- slides/circt.qmd               # CIRCT concepts through the E4M3 example
|-- slides/circt-tools.qmd         # Command-line tour and timed exercises
|-- slides/arithmetic.qmd          # E4M3 lowering and implementation choices
|-- slides/hls-eurollvm.qmd        # EuroLLVM HLS chapter included by the deck
|-- _quarto.yml                    # Shared Quarto project configuration
|-- _quarto-student.yml            # Student output directory
|-- _quarto-instructor.yml         # Instructor output directory
|-- figures/digital-design/        # Editable SystemVerilog for generated schematics
|-- figures/arithmetic/            # Editable TikZ for the staged E4M3 datapath
|-- assets/images/digital-design/  # Reference figures and generated Yosys schematics
|-- assets/images/arithmetic/      # Generated transparent E4M3 SVG layers
|-- assets/images/hls/             # EuroLLVM HLS figures and PPA plots
|-- assets/images/logos/           # Project and institution logos
|-- styles/                        # Reveal.js presentation CSS
|-- syntax/mlir.xml                # MLIR syntax-highlighting grammar
|-- filters/slide-layout.lua       # Slide title/body layout filter
|-- scripts/render-course-decks.sh # Builds both deck editions
|-- scripts/generate-digital-design-schematics.sh # Regenerates Yosys SVGs
|-- scripts/generate-e4m3-rewrite-datapath.sh # Regenerates staged TikZ SVGs
|-- tutorial/                      # Original CIRCT tool tour plus arithmetic pass exercises
|-- .github/workflows/             # GHCR image publication
|-- dist/                          # Generated slides; ignored
|-- tmp/                           # Scratch and test output; ignored
```

## Slide infrastructure

### Quarto configuration

- `_quarto.yml` selects the slide source, copies image resources, and declares
  `student` as the default profile.
- `_quarto-student.yml` writes the public deck to `dist/student/`.
- `_quarto-instructor.yml` writes the deck with solutions to
  `dist/instructor/`.

### Styles

The styles are separated by responsibility so `lecture.css` does not become a
single large file:

| File | Responsibility |
|---|---|
| `styles/lecture.css` | Global Reveal.js typography, slide alignment, columns, and callouts |
| `styles/course.css` | Layouts specific to this course: title, who-am-I, roadmap, stack, and exercises |
| `styles/diagrams.css` | Reusable lowering flows, bit fields, circuit stages, and exercise timing diagrams |
| `styles/motivation.css` | Shared typography for the motivation and digital-design visual sequence |
| `styles/multiplier.css` | Vertical E4M3 datapath layers and matching solution panels |
| `styles/hls.css` | EuroLLVM HLS flow diagrams, result layouts, rotated physical-design views, and PPA slides |
| `styles/code.css` | Shared code-block sizing, borders, scrolling, and highlighted lines |
| `styles/code-mlir.css` | Colors for MLIR token classes emitted by the MLIR grammar |

The shared accent color is `--course-accent` in `styles/lecture.css`.
Markdown bold text uses it automatically:

```markdown
This is **important**.
```

For a pen-style highlight across the lower half of selected words, use a
Pandoc span:

```markdown
This is [the value to remember]{.marker}.
```

The `.marker` treatment uses the same accent color, so both forms remain
consistent with the title-slide event line and the course diagrams.

### Syntax and layout filter

`syntax/mlir.xml` is a Pandoc/KDE-style language definition. It recognizes MLIR
operations, types, values, attributes, numbers, strings, and comments. Pandoc
turns those categories into token classes; `styles/code-mlir.css` colors them.

`filters/slide-layout.lua` keeps a regular slide heading separate from its
body. This lets `styles/lecture.css` keep the heading at the top while centering
the body vertically. It does not modify title slides or section-title slides.

### HLS chapter

`slides/hls-eurollvm.qmd` is included from the final HLS stack in the canonical
deck. It ports the EuroLLVM sequence from application workloads through tensor
and loop IRs, HAriCo lowering, CIRCT `comb`/`seq`/`hw`, ASIC/FPGA results, and
the workload PPA study. MLIR examples are fenced `mlir` blocks, so they use the
local grammar instead of being baked into screenshots. Figures copied from the
source presentation live under `assets/images/hls/`; their provenance is listed
in `assets/images/ATTRIBUTIONS.md`.

### Digital-design schematics

The introductory E4M3 normal-path schematic is generated from
`figures/digital-design/concepts.sv` rather than drawn manually. It uses the
same fields and signal names as the MLIR and hands-on examples. Regenerate the
SVG asset with:

```bash
./scripts/generate-digital-design-schematics.sh
```

The script runs Yosys from the local `openroad/orfs:latest` image and Graphviz
on the host. Intermediate DOT files stay under the ignored `tmp/` directory.

### Arithmetic rewrite figure

`figures/arithmetic/e4m3-rewrite-datapath.tex` defines the vertical E4M3
multiplier once, then exports transparent layers for the target operation,
sign, significand, normalization, exponent, and packing stages:

```bash
./scripts/generate-e4m3-rewrite-datapath.sh
```

The generated SVGs have an identical view box, so Reveal.js can unveil each
circuit layer together with the corresponding Python rewrite code.

## Build the slides

The slides are made with quarto, an open source technical publishing system for creating beautiful articles, websites, blogs, books, slides, and more.

Build students and teacher editions:

```bash
./scripts/render-course-decks.sh
```

The generated decks are:

```text
dist/student/mlir-circt-summer-school-2026.html
dist/instructor/mlir-circt-summer-school-2026.html
```

Preview one edition while editing:

```bash
quarto preview mlir-circt-summer-school.qmd --profile instructor
```

## Tutorial container

Students start the published environment with one command. Docker downloads it
automatically the first time:

```bash
docker run -it ghcr.io/bynaryman/mlir-summer-school-2026-circt:latest
```

Build the same image locally when changing the Dockerfile or exercise:

```bash
docker build -t mlir-summer-school-2026-circt tutorial
docker run -it mlir-summer-school-2026-circt
```

The exercise structure and commands are documented in `tutorial/README.md`.
