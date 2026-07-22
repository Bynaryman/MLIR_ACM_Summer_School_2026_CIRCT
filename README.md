# MLIR/CIRCT Summer School 2026

This repository keeps the developing course material and the CIRCT programming
exercise in one place. The content is still being designed. `my_plan.md` is the
source for what the talk should say; the Quarto deck is the current prototype.

The deck has two render profiles:

- `student`: exercises without the solution appendix;
- `instructor`: exercises with links to uncounted solution slides.

## File hierarchy

```text
.
|-- mlir-circt-summer-school.qmd   # Slide source
|-- my_plan.md                     # Personal content and speaking ideas
|-- _quarto.yml                    # Shared Quarto project configuration
|-- _quarto-student.yml            # Student output directory
|-- _quarto-instructor.yml         # Instructor output directory
|-- assets/images/                 # Images used by the deck
|-- styles/                        # Reveal.js presentation CSS
|-- syntax/mlir.xml                # MLIR syntax-highlighting grammar
|-- filters/slide-layout.lua       # Slide title/body layout filter
|-- scripts/render-course-decks.sh # Builds both deck editions
|-- tutorial/                      # CIRCT tour, AIG analysis, pass exercise
|-- references/program/            # Summer-school program source material
|-- .github/workflows/             # GHCR image publication
|-- dist/                          # Generated slides; ignored
|-- tmp/                           # Scratch and test output; ignored
`-- venv/                          # Optional local Python environment; ignored
```

`assets/images/ATTRIBUTIONS.md` records the source and license of each external
image. The PDF and Markdown files under `references/program/` are reference
material, not presentation build inputs.

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

## Python environment

`venv/` was created for earlier executable Quarto experiments using Jupyter and
the CIRCT Python bindings. It currently contains `circt==1.152.0`, IPython, and
Jupyter.

The current deck does not execute Python, so `venv/` is not required to render
the slides. The C++ exercise also does not use it: its Docker image contains
CIRCT `1.147.0` and the required CMake toolchain. The AIG and exhaustive-test
scripts use the container's system Python, not this virtual environment. The
environment is local, ignored by Git, and can be deleted if those earlier
Python experiments are no longer needed.

Activate it only when working on Python/CIRCT experiments:

```bash
source venv/bin/activate
```

## Build the slides

Build both editions:

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

## Git and generated files

Yes, from the repository root you can stage the current work with:

```bash
git add .
```

The ignore rules exclude:

- `.quarto/` and `dist/`;
- `tmp/`;
- `venv/` and `.venv/`;
- Python caches and Quarto notebook intermediates;
- `tutorial/build/`, generated MLIR/SystemVerilog, and compile commands;
- common editor and operating-system files.

`git add .` also stages deletions of obsolete tracked files, which is intended
for the current cleanup. Inspect the exact staged result before committing:

```bash
git status --short
git diff --cached --stat
```
