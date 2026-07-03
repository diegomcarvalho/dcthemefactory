import pandas as pd
import numpy as np
from src.dc_theme_factory.dc_theme_factory import DCThemeFactory, colors

dates = pd.date_range("2026-01-01", periods=60, freq="D")
df = pd.DataFrame({
    "data": np.tile(dates, 2),
    "value": np.concatenate([
        5.2 + np.cumsum(np.random.normal(0, 0.02, 60)),
        5.4 + np.cumsum(np.random.normal(0, 0.02, 60)),
    ]),
    "variable": ["EUR"] * 60 + ["USD"] * 60,
})

fig = DCThemeFactory.create_figure(
    df, x="data", y="value", color="variable",
    kind="line", title="EUR/BRL Exchange Rate",
    xlab="Date", ylab="Value", x_date=True,
)
fig.save("exchange_rate.png", width=8, height=5, dpi=150)

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
fig.save("monthly_average_rate.png", width=8, height=5, dpi=150)

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

fig.save("exchange_rate_distribution.png", width=8, height=5, dpi=150)

fig = DCThemeFactory.create_figure(
    df, x="variable", y="value", color="variable",
    kind="boxplot", swarm=True,
    swarm_width=0.05, swarm_bins=25,
    jitter_size=1.0, jitter_alpha=0.3,
)

fig.save("exchange_rate_boxplot.png", width=8, height=5, dpi=150)
