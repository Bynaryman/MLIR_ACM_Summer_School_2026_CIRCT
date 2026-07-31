# Microprocessor Trend Data

The five `.dat` files contain historical `year value` samples for transistor
count, clock frequency, typical power, logical cores, and single-thread SPECint
performance through 2021.

They are copied from Karl Rupp's
[`microprocessor-trend-data`](https://github.com/karlrupp/microprocessor-trend-data)
repository, directory `50yrs/`. The original data through 2010 was collected by
Mark Horowitz, Fred Labonte, Ofer Shacham, Kunle Olukotun, Lance Hammond, and
Chris Batten; Karl Rupp collected the 2010-2021 additions.

The historical data is licensed under CC BY 4.0.

`recent.csv` adds directly comparable public product specifications through
July 2026. Recent frequency values use the published base clock; power uses TDP
or AMD's Default CPU Power; logical threads use the vendor's published total.
The rows link to the corresponding official AMD and Intel product pages. These
points are kept separate from the historical source and drawn with an outline.

The historical SPECint series is not extended. Current SPEC CPU benchmark
generations are not numerically interchangeable with the older series.

`processor-summary.dat` is the slide-facing view of the upper-panel data. It
uses representative medians near selected milestone years instead of plotting
the full product cloud. The 2024 and 2026 rows summarize the official public
specifications in `recent.csv`; `nan` marks unavailable or intentionally
uncombined values.

The lower panel uses three small, documented relative series:

- `cpu-relative.dat` contains representative medians from the historical
  SPECint samples, normalized to 1999.
- `dram-bandwidth-relative.dat` uses the maximum mainstream module bandwidth
  for each JEDEC DRAM generation reported by Hanindhito et al., Part II,
  normalized to DDR-400.
- `dram-latency-relative.dat` records Chang's observation that DRAM latency
  performance improved only about 1.3x over roughly two decades. Its dashed
  continuation is a visual guide, not a new measurement.

Hanindhito et al.'s 2025/2026 survey updates the well-known processor trend
figure with measurements through 2023 and projections through 2030:

- Part I: <https://doi.org/10.1177/10943420251348799>
- Part II: <https://doi.org/10.1177/10943420251347461>
- Chang dissertation: <https://arxiv.org/abs/1712.08304>

The editable plot source is `figures/microprocessor-trends.tex`.

Regenerate the course figures with:

```bash
./scripts/generate-microprocessor-trends.sh
```
