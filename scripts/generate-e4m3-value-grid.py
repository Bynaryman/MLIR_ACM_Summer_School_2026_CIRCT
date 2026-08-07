#!/usr/bin/env python3

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "images" / "arithmetic" / "e4m3-value-grid.svg"

WIDTH = 1480
HEIGHT = 680
GRID_X = 150
GRID_Y = 82
CELL_WIDTH = 78
CELL_HEIGHT = 31

INK = "#20262c"
ACCENT = "#0f766e"
GRID = "#9aa4ad"
NORMAL = "#ffffff"
ZERO = "#b9ded9"
SUBNORMAL = "#f1d998"
NAN = "#efc4ce"


def classify(exponent: int, fraction: int) -> str:
    if exponent == 0:
        return "zero" if fraction == 0 else "subnormal"
    if exponent == 0xF and fraction == 0x7:
        return "nan"
    return "normal"


def magnitude(exponent: int, fraction: int) -> float:
    if exponent == 0:
        return fraction * 2.0**-9
    return (1.0 + fraction / 8.0) * 2.0 ** (exponent - 7)


def compact_value(sign: int, exponent: int, fraction: int) -> str:
    category = classify(exponent, fraction)
    if category == "nan":
        return "NaN"
    if category == "zero":
        return "-0" if sign else "+0"

    value = magnitude(exponent, fraction)
    if value < 2.0**-6:
        text = f"{value:.3f}"
    elif value < 1:
        text = f"{value:.4f}".rstrip("0").rstrip(".")
    elif value < 16:
        text = f"{value:.3f}".rstrip("0").rstrip(".")
    else:
        text = str(int(value))

    if text.startswith("0."):
        text = text[1:]
    return f"-{text}" if sign else text


def exact_description(sign: int, exponent: int, fraction: int) -> str:
    bits = f"{sign} {exponent:04b} {fraction:03b}"
    category = classify(exponent, fraction)
    if category == "nan":
        value = "NaN"
    elif category == "zero":
        value = "-0" if sign else "+0"
    else:
        signed = -magnitude(exponent, fraction) if sign else magnitude(
            exponent, fraction
        )
        value = f"{signed:.9g}"
    return f"{bits} = {value} ({category})"


def main() -> None:
    fills = {
        "normal": NORMAL,
        "zero": ZERO,
        "subnormal": SUBNORMAL,
        "nan": NAN,
    }

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        "  <title id=\"title\">All E4M3FN encodings and values</title>",
        "  <desc id=\"desc\">A sixteen by sixteen table. Columns encode the four exponent bits and rows encode the sign and three fraction bits. Signed zero, subnormal values, and NaNs are colorized.</desc>",
        f'  <text x="{GRID_X + 8 * CELL_WIDTH}" y="24" text-anchor="middle" '
        f'font-family="Inter, Arial, sans-serif" font-size="18" font-weight="700" fill="{INK}">column: exponent eeee</text>',
        f'  <text x="{WIDTH - 28}" y="24" text-anchor="end" '
        f'font-family="IBM Plex Mono, DejaVu Sans Mono, monospace" font-size="15" fill="{INK}">cell = s eeee mmm</text>',
        f'  <text x="24" y="{GRID_Y + 8 * CELL_HEIGHT}" text-anchor="middle" '
        f'transform="rotate(-90 24 {GRID_Y + 8 * CELL_HEIGHT})" '
        f'font-family="Inter, Arial, sans-serif" font-size="18" font-weight="700" fill="{INK}">row: sign + fraction smmm</text>',
    ]

    for exponent in range(16):
        x = GRID_X + (exponent + 0.5) * CELL_WIDTH
        out.append(
            f'  <text x="{x:g}" y="67" text-anchor="middle" '
            f'font-family="IBM Plex Mono, DejaVu Sans Mono, monospace" '
            f'font-size="15" font-weight="700" fill="{INK}">{exponent:04b}</text>'
        )

    for sign_fraction in range(16):
        y = GRID_Y + (sign_fraction + 0.5) * CELL_HEIGHT + 5
        out.append(
            f'  <text x="132" y="{y:g}" text-anchor="end" '
            f'font-family="IBM Plex Mono, DejaVu Sans Mono, monospace" '
            f'font-size="15" font-weight="700" fill="{INK}">{sign_fraction:04b}</text>'
        )

        sign = sign_fraction >> 3
        fraction = sign_fraction & 0x7
        for exponent in range(16):
            x = GRID_X + exponent * CELL_WIDTH
            cell_y = GRID_Y + sign_fraction * CELL_HEIGHT
            category = classify(exponent, fraction)
            label = compact_value(sign, exponent, fraction)
            description = escape(exact_description(sign, exponent, fraction))
            weight = "700" if category != "normal" else "500"
            out.extend(
                [
                    "  <g>",
                    f"    <title>{description}</title>",
                    f'    <rect x="{x}" y="{cell_y}" width="{CELL_WIDTH}" height="{CELL_HEIGHT}" '
                    f'fill="{fills[category]}" stroke="{GRID}" stroke-width="0.8"/>',
                    f'    <text x="{x + CELL_WIDTH / 2:g}" y="{cell_y + 20.5:g}" text-anchor="middle" '
                    f'font-family="IBM Plex Mono, DejaVu Sans Mono, monospace" '
                    f'font-size="13" font-weight="{weight}" fill="{INK}">{escape(label)}</text>',
                    "  </g>",
                ]
            )

    grid_width = 16 * CELL_WIDTH
    grid_height = 16 * CELL_HEIGHT
    out.extend(
        [
            f'  <rect x="{GRID_X}" y="{GRID_Y}" width="{grid_width}" height="{grid_height}" '
            f'fill="none" stroke="{INK}" stroke-width="1.8"/>',
            f'  <line x1="{GRID_X}" y1="{GRID_Y + 8 * CELL_HEIGHT}" '
            f'x2="{GRID_X + grid_width}" y2="{GRID_Y + 8 * CELL_HEIGHT}" '
            f'stroke="{INK}" stroke-width="2.6"/>',
        ]
    )

    legend_y = 622
    legend = [
        (NORMAL, "normal finite (238)"),
        (ZERO, "signed zero (2)"),
        (SUBNORMAL, "subnormal (14)"),
        (NAN, "NaN (2)"),
    ]
    legend_x = 190
    for fill, label in legend:
        out.append(
            f'  <rect x="{legend_x}" y="{legend_y}" width="24" height="20" '
            f'fill="{fill}" stroke="{GRID}" stroke-width="1"/>'
        )
        out.append(
            f'  <text x="{legend_x + 34}" y="{legend_y + 16}" '
            f'font-family="Inter, Arial, sans-serif" font-size="16" fill="{INK}">{label}</text>'
        )
        legend_x += 270

    out.append(
        f'  <text x="{WIDTH - 54}" y="{legend_y + 16}" text-anchor="end" '
        f'font-family="Inter, Arial, sans-serif" font-size="15" fill="{INK}">values below 1 rounded for display</text>'
    )
    out.append("</svg>")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
