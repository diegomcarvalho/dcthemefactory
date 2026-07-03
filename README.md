# DCThemeFactory

A Factory Method implementation for creating consistently themed [Plotnine](https://plotnine.org/) charts, supporting multiple visual "looks" — including the original custom `theme_dc()` style and a look inspired by **The Economist**'s chart style.

## Overview

`DCThemeFactory` centralizes the creation of both **themes** and **figures**, ensuring every chart in a project shares a consistent visual identity while abstracting away the boilerplate of building `ggplot` objects manually.

Two main methods are provided:

- `create_theme(look="dc", x_date=False, **overrides)` — builds a `p9.theme()` object for the requested look, with an optional rotated x-axis for date data.
- `create_figure(df, x, y, color, kind, look="dc", ...)` — builds a full chart (data + geometry + color scale + theme) in a single call.

`theme_dc()` and `theme_economist()` convenience wrappers are also provided for direct theme-only usage.

## Installation

```bash
pip install plotnine pandas numpy
```

## Supported looks (`look`)

| look        | Background      | Grid                     | Palette (default)      | Style notes                                      |
|-------------|------------------|---------------------------|--------------------------|---------------------------------------------------|
| `dc`        | White            | Light-gray, both axes     | `colors` (32 saturated)  | Boxed panel border, black outlines on filled geoms |
| `economist` | Light blue (`#D7E9F5`) | White, horizontal only | `ECON_PALETTE` (32 colors) | No panel border, bottom axis line, no forced outlines |

Both looks share the same `create_figure()` API — only the visual styling and default palette change.

## Supported chart types (`kind`)

| kind      | Geom              | Uses `fill`? | Notes                                    |
|-----------|-------------------|--------------|--------------------------------------------|
| `line`    | `geom_line`       | No           | Default chart type                         |
| `scatter` | `geom_point`      | No           | Simple point chart                         |
| `bar`     | `geom_col`        | Yes          | Supports `stacked=True/False`              |
| `area`    | `geom_area`       | Yes          | Supports `stacked=True/False`              |
| `hist`    | `geom_histogram`  | Yes          | Supports `bins`, `binwidth`, `stacked`     |
| `boxplot` | `geom_boxplot`    | Yes          | `y` required; supports jitter or beeswarm overlay |

## Basic usage

```python
import pandas as pd
import numpy as np
from dc_theme_factory import DCThemeFactory

dates = pd.date_range("2026-01-01", periods=30, freq="D")
df = pd.DataFrame({
    "data": np.tile(dates, 2),
    "value": np.concatenate([
        5.2 + np.cumsum(np.random.normal(0, 0.02, 30)),
        5.4 + np.cumsum(np.random.normal(0, 0.02, 30)),
    ]),
    "variable": ["EUR"] * 30 + ["USD"] * 30,
})

fig = DCThemeFactory.create_figure(
    df, x="data", y="value", color="variable",
    kind="line", title="EUR/BRL Exchange Rate",
    xlab="Date", ylab="Value", x_date=True,
    look="dc",  # or "economist"
)
fig.save("exchange_rate.png", width=8, height=5, dpi=150)
```

## Examples by chart type

### Line chart (dc look)

```python
fig = DCThemeFactory.create_figure(
    df, x="data", y="value", color="variable",
    kind="line", title="EUR/BRL Exchange Rate",
    xlab="Date", ylab="Value", x_date=True, look="dc",
)
```

### Line chart (Economist look, with subtitle and caption)

```python
fig = DCThemeFactory.create_figure(
    df, x="data", y="value", color="variable",
    kind="line", title="EUR/BRL Exchange Rate",
    subtitle="Daily exchange rate", caption="Source: example data",
    xlab="Date", ylab="Value", x_date=True, look="economist",
)
```

### Bar chart (grouped, not stacked)

```python
df_bar = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar"] * 2,
    "value": [5.1, 5.3, 5.2, 5.4, 5.6, 5.5],
    "variable": ["EUR"] * 3 + ["USD"] * 3,
})

fig = DCThemeFactory.create_figure(
    df_bar, x="month", y="value", color="variable",
    kind="bar", title="Monthly Average Rate",
    xlab="Month", ylab="Value", stacked=False,
)
```

### Area chart (overlapping, not stacked)

```python
fig = DCThemeFactory.create_figure(
    df, x="data", y="value", color="variable",
    kind="area", title="EUR/BRL Exchange Rate (Area)",
    xlab="Date", ylab="Value", x_date=True,
    stacked=False, alpha=0.6,
)
```

### Histogram

```python
df_hist = pd.DataFrame({
    "value": np.concatenate([
        np.random.normal(5.2, 0.15, 200),
        np.random.normal(5.6, 0.15, 200),
    ]),
    "variable": ["EUR"] * 200 + ["USD"] * 200,
})

fig = DCThemeFactory.create_figure(
    df_hist, x="value", color="variable",
    kind="hist", title="Exchange Rate Distribution",
    xlab="Value", ylab="Frequency",
    stacked=False, bins=25,
)
```

### Boxplot with random jitter overlay

```python
fig = DCThemeFactory.create_figure(
    df_hist, x="variable", y="value", color="variable",
    kind="boxplot", title="Exchange Rate Distribution",
    xlab="Currency", ylab="Value",
    jitter_width=0.15, jitter_size=1.5, jitter_alpha=0.6,
)
```

### Boxplot with deterministic beeswarm overlay

```python
fig = DCThemeFactory.create_figure(
    df_hist, x="variable", y="value", color="variable",
    kind="boxplot", title="Exchange Rate Distribution (Beeswarm)",
    xlab="Currency", ylab="Value",
    swarm=True, swarm_width=0.3, swarm_bins=25,
    look="economist",
)
```

### Custom theme only (no figure)

```python
import plotnine as p9

theme = DCThemeFactory.create_theme(look="economist", x_date=True)
fig = p9.ggplot(df, p9.aes(x="data", y="value")) + p9.geom_line() + theme
```

### Legacy-compatible usage

```python
from dc_theme_factory import theme_dc, theme_economist, colors

fig = (
    p9.ggplot(df, p9.aes(x="data", y="value", color="variable"))
    + p9.geom_line(size=1)
    + p9.scale_color_manual(values=colors)
    + theme_dc(x_date=True)
)

# or, for the Economist look:
fig = (
    p9.ggplot(df, p9.aes(x="data", y="value", color="variable"))
    + p9.geom_line(size=1)
    + theme_economist(x_date=True)
)
```

## Parameters reference (`create_figure`)

| Parameter       | Type       | Default   | Description                                                      |
|-----------------|------------|-----------|--------------------------------------------------------------------|
| `df`            | DataFrame  | required  | Source data                                                        |
| `x`, `y`        | str        | required* | Column names for axes (`y` optional for `hist`)                    |
| `color`         | str        | `None`    | Column used for color/fill grouping                                 |
| `kind`          | str        | `"line"`  | `line`, `scatter`, `bar`, `area`, `hist`, or `boxplot`               |
| `look`          | str        | `"dc"`    | `"dc"` or `"economist"` — controls theme, default palette, and outline styling |
| `title`         | str        | `""`      | Chart title                                                          |
| `subtitle`      | str        | `None`    | Chart subtitle                                                       |
| `caption`       | str        | `None`    | Chart caption/source note (styled distinctly in the `economist` look) |
| `xlab`, `ylab`  | str        | `""`      | Axis labels                                                          |
| `x_date`        | bool       | `False`   | Rotates x-axis labels for date axes                                  |
| `palette`       | list       | look-dependent | Custom color palette override (defaults to `colors` for `dc`, `ECON_PALETTE` for `economist`) |
| `alpha`         | float      | `None`    | Transparency for geoms                                               |
| `stacked`       | bool       | `True`    | Stack vs. dodge/overlap for `bar`/`area`/`hist`                       |
| `bins`          | int        | `30`      | Number of bins for `hist`                                            |
| `binwidth`      | float      | `None`    | Bin width for `hist` (overrides `bins`)                              |
| `jitter_width`, `jitter_height` | float | `0.15`, `0.0` | Spread of random jitter overlay for `boxplot` (ignored if `swarm=True`) |
| `jitter_size`, `jitter_alpha`   | float | `1.5`, `0.6`  | Marker size/transparency for `boxplot` point overlay (jitter or swarm) |
| `swarm`         | bool       | `False`   | If `True`, uses a deterministic beeswarm layout instead of random jitter for `boxplot` |
| `swarm_width`, `swarm_bins`     | float, int | `0.3`, `30`   | Spread and bin granularity for the beeswarm layout |

## Notes

- Color/fill mapping is automatically switched between `color` and `fill` depending on the chart type, avoiding the common Plotnine pitfall of black-filled bars/areas.
- For overlapping distributions in histograms or areas, consider lowering `alpha` (e.g., 0.4–0.6) for better readability.
- The `dc` look expects the `Avenir Next Condensed` font, and the `economist` look expects `Roboto`; if not installed locally, Matplotlib falls back to a default font (a harmless warning is printed).
- Extending the factory with a new look only requires adding an entry to `LOOKS`, a `_create_<look>_theme()` classmethod, and a default palette in `DEFAULT_PALETTES`.
- Extending with a new chart `kind` only requires adding it to `FILL_GEOMS` (if applicable) and a new branch inside `create_figure()`'s geometry-selection block.