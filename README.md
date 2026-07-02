# DCThemeFactory

A Factory Method implementation for creating consistently themed [Plotnine](https://plotnine.org/) charts, based on the `theme_dc()` custom theme.

## Overview

`DCThemeFactory` centralizes the creation of both **themes** and **figures**, ensuring every chart in a project shares the same visual identity (fonts, borders, grid, legend style) while abstracting away the boilerplate of building `ggplot` objects manually.

Two main methods are provided:

- `create_theme(x_date=False, **overrides)` — builds a `p9.theme()` object, with an optional rotated x-axis for date data.
- `create_figure(df, x, y, color, kind, ...)` — builds a full chart (data + geometry + color scale + theme) in a single call.

A `theme_dc()` function is also kept for backward compatibility with legacy code.

## Installation

```bash
pip install plotnine pandas numpy
```

## Supported chart types (`kind`)

| kind      | Geom              | Uses `fill`? | Notes                                  |
|-----------|-------------------|--------------|-----------------------------------------|
| `line`    | `geom_line`       | No           | Default chart type                      |
| `scatter` | `geom_point`      | No           | Simple point chart                      |
| `bar`     | `geom_col`        | Yes          | Supports `stacked=True/False`           |
| `area`    | `geom_area`       | Yes          | Supports `stacked=True/False`           |
| `hist`    | `geom_histogram`  | Yes          | Supports `bins`, `binwidth`, `stacked`  |

## Basic usage

```python
import pandas as pd
import numpy as np
from dc_theme_factory import DCThemeFactory, colors

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
)
fig.save("exchange_rate.png", width=8, height=5, dpi=150)
```

## Examples by chart type

### Line chart

```python
fig = DCThemeFactory.create_figure(
    df, x="data", y="value", color="variable",
    kind="line", title="EUR/BRL Exchange Rate",
    xlab="Date", ylab="Value", x_date=True,
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

### Custom theme only (no figure)

```python
theme = DCThemeFactory.create_theme(x_date=True)
fig = p9.ggplot(df, p9.aes(x="data", y="value")) + p9.geom_line() + theme
```

### Legacy-compatible usage

```python
fig = (
    p9.ggplot(df, p9.aes(x="data", y="value", color="variable"))
    + p9.geom_line(size=1)
    + p9.scale_color_manual(values=colors)
    + theme_dc(x_date=True)
)
```

## Parameters reference (`create_figure`)

| Parameter    | Type       | Default   | Description                                            |
|--------------|------------|-----------|----------------------------------------------------------|
| `df`         | DataFrame  | required  | Source data                                              |
| `x`, `y`     | str        | required* | Column names for axes (`y` optional for `hist`)          |
| `color`      | str        | `None`    | Column used for color/fill grouping                      |
| `kind`       | str        | `"line"`  | `line`, `scatter`, `bar`, `area`, or `hist`               |
| `title`      | str        | `""`      | Chart title                                               |
| `subtitle`   | str        | `None`    | Chart subtitle                                            |
| `xlab`, `ylab`| str       | `""`      | Axis labels                                                |
| `x_date`     | bool       | `False`   | Rotates x-axis labels for date axes                        |
| `palette`    | list       | `colors`  | Custom color palette override                              |
| `alpha`      | float      | `None`    | Transparency for geoms                                     |
| `stacked`    | bool       | `True`    | Stack vs. dodge/overlap for `bar`/`area`/`hist`             |
| `bins`       | int        | `30`      | Number of bins for `hist`                                  |
| `binwidth`   | float      | `None`    | Bin width for `hist` (overrides `bins`)                     |

## Notes

- Color/fill mapping is automatically switched between `color` and `fill` depending on the chart type, avoiding the common Plotnine pitfall of black-filled bars/areas.
- For overlapping distributions in histograms or areas, consider lowering `alpha` (e.g., 0.4–0.6) for better readability.
- The `Avenir Next Condensed` font must be installed locally for full theme fidelity; otherwise, Matplotlib will fall back to a default font.
