# MLIR/CIRCT Summer School 2026

This repository keeps the developing course material and the CIRCT programming
exercise in one place. `my_plan.md` is the source for what the talk should say;
the canonical Quarto deck is being rebuilt from it one section at a time. The
previous full prototype remains in `mlir-circt-summer-school-old.qmd` as a
reference for content and layouts, but Quarto does not render it.

The project retains two render profiles for the later exercises:

- `student`: exercises without the solution appendix;
- `instructor`: exercises with links to uncounted solution slides.

## File hierarchy

```text
.
|-- mlir-circt-summer-school.qmd   # Canonical, incremental slide source
|-- mlir-circt-summer-school-old.qmd # Archived prototype; not rendered
|-- my_plan.md                     # Personal content and speaking ideas
|-- _quarto.yml                    # Shared Quarto project configuration
|-- _quarto-student.yml            # Student output directory
|-- _quarto-instructor.yml         # Instructor output directory
|-- assets/images/                 # Images used by the deck
|-- styles/                        # Reveal.js presentation CSS
|-- syntax/mlir.xml                # MLIR syntax-highlighting grammar
|-- filters/slide-layout.lua       # Slide title/body layout filter
|-- scripts/render-course-decks.sh # Builds both deck editions
|-- tutorial/                      # CIRCT tour, AIG analysis, ARITHmetic pass exercise
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
| `styles/course.css` | Layouts specific to this course: who-am-I, roadmap, stack, exercises, and HLS slides |
| `styles/diagrams.css` | Reusable lowering flows, bit fields, circuit stages, and exercise timing diagrams |
| `styles/multiplier.css` | Incremental E4M3 multiplier schematic and solution workbench |
| `styles/code.css` | Shared code-block sizing, borders, scrolling, and highlighted lines |
| `styles/code-mlir.css` | Colors for MLIR token classes emitted by the MLIR grammar |

### Syntax and layout filter

`syntax/mlir.xml` is a Pandoc/KDE-style language definition. It recognizes MLIR
operations, types, values, attributes, numbers, strings, and comments. Pandoc
turns those categories into token classes; `styles/code-mlir.css` colors them.

`filters/slide-layout.lua` keeps a regular slide heading separate from its
body. This lets `styles/lecture.css` keep the heading at the top while centering
the body vertically. It does not modify title slides or section-title slides.

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
