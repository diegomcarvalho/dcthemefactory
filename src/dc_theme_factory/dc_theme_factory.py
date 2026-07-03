# -*- coding: utf-8 -*-
"""
dc_theme_factory.py

DCThemeFactory: A Factory Method implementation for creating consistently
themed Plotnine charts based on the custom `theme_dc()` theme.

Author: Diego Carvalho
Contact: diego.carvalho@cefet-rj.br
Institution: CEFET/RJ - Centro Federal de Educação Tecnológica
Celso Suckow da Fonseca

Copyright (c) 2026 Diego Carvalho

This work is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).
To view a copy of this license, visit:
https://creativecommons.org/licenses/by-sa/4.0/

You are free to:
- Share : copy and redistribute the material in any medium or format.
- Adapt : remix, transform, and build upon the material for any
purpose, even commercially.

Under the following terms:
- Attribution : You must give appropriate credit, provide a link to
the license, and indicate if changes were made.
- ShareAlike : If you remix, transform, or build upon the material,
you must distribute your contributions under the same license as the 
original.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""

import pandas as pd
import plotnine as p9
import numpy as np
import os


def _compute_beeswarm_offsets(values, width=0.3, nbins=30):
    """
    Compute horizontal offsets for a 1D array of values so that points
    sharing similar y-values are spread symmetrically side-by-side,
    mimicking a "beeswarm" layout instead of a random jitter.

    Parameters
    ----------
    values : array-like
        The y-values (e.g. a single group's measurements) to offset.
    width : float
        Maximum horizontal spread (in the same units as the categorical
        x positions, typically 0-1) applied within a bin.
    nbins : int
        Number of bins used to group nearby values together before
        spreading them horizontally. More bins -> finer-grained packing.

    Returns
    -------
    numpy.ndarray
        Horizontal offsets, same length and order as `values`.
    """
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return np.array([])
    lo, hi = values.min(), values.max()
    if lo == hi:
        bins = np.array([lo])
        bin_idx = np.zeros(len(values), dtype=int)
    else:
        bins = np.linspace(lo, hi, nbins)
        bin_idx = np.digitize(values, bins)

    offsets = np.zeros(len(values))
    for b in np.unique(bin_idx):
        mask = bin_idx == b
        n = mask.sum()
        if n > 1:
            spread = np.linspace(-width, width, n)
        else:
            spread = [0.0]
        offsets[mask] = spread
    return offsets


# Legacy palette (kept for reference / rollback). Not used by default.
# colors = ["#0C87D1", "#40b8d0", "#193375", "#19AE47", "#FFCB05", "#b2d183", "#FDDC02"]

# Pastel palette: soft, low-saturation colors. Best used on dark backgrounds
# where contrast against the panel/grid is not an issue; on light/gray
# backgrounds (default theme_dc panel) these colors tend to wash out.
p_colors = [
    "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF",
    "#BDB2FF", "#FFC6FF", "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9",
    "#BAE1FF", "#D4A5A5", "#C9C9FF", "#FFCCE5", "#B5EAD7", "#C7CEEA",
    "#FFDAC1", "#E2F0CB", "#B2DFDB", "#F8C8DC", "#D0F4DE", "#A9DEF9",
    "#E4C1F9", "#FCF6BD", "#FF99C8", "#FCF6B1", "#D0BDF4", "#8EECF5",
    "#B9FBC0", "#F1C0E8",
]

# Default palette: 32 saturated, high-contrast colors. Designed to stand out
# clearly against the light-gray panel grid (#d3d3d3) used in theme_dc.
colors = [
    "#0082C8", "#3CB44B", "#F58231", "#911EB4", "#E6194B",
    "#46F0F0", "#F032E6", "#D2F53C", "#FABEBE", "#008080",
    "#E6BEFF", "#AA6E28", "#800000", "#AAFFC3", "#808000",
    "#FFD8B1", "#000080", "#FF4500", "#8B008B", "#2E8B57",
    "#1E90FF", "#B8860B", "#DC143C", "#00CED1", "#FF69B4",
    "#4682B4", "#556B2F", "#9932CC", "#FF6347", "#20B2AA",
    "#C71585", "#6A5ACD",
]


class DCThemeFactory:
    """
    Factory Method for building theme_dc-based Plotnine themes and charts.

    This class centralizes:
      1. The shared visual style ("theme_dc") used across all charts
         (fonts, borders, grid, legend layout).
      2. A higher-level "product" builder (`create_figure`) that assembles
         a complete ggplot object (data + geometry + color scale + theme)
         from simple keyword arguments, so callers do not need to know
         Plotnine's API in detail.

    Adding a new chart type only requires extending `FILL_GEOMS` (if the
    geom uses `fill` instead of `color`) and adding a branch inside
    `create_figure`'s geom-selection block.
    """

    # Theme attributes shared by every variant returned by create_theme().
    # Only axis_text_x changes between variants (date vs. non-date axis).
    BASE_KWARGS = dict(
        panel_border=p9.element_rect(colour="black", fill=None, size=0.5),
        text=p9.element_text(family='Avenir Next Condensed'),
        axis_text_y=p9.element_text(colour="black", size=10),
        legend_key=p9.element_rect(fill="white", colour="white"),
        legend_position="top",
        legend_direction="horizontal",
        legend_title=p9.element_blank(),
        panel_grid_major=p9.element_line(colour="#d3d3d3"),
        panel_grid_minor=p9.element_blank(),
        plot_title=p9.element_text(size=14, face="bold", ha='left'),
        plot_subtitle=p9.element_text(size=12, face="italic"),
        legend_key_size=5,
        legend_spacing=0.5,
    )

    # Geoms that use the `fill` aesthetic for coloring (as opposed to
    # `color`, which only affects outlines/points/lines). Any new geom
    # that fills an area (e.g. a future "violin" plot) should be added
    # here so create_figure() maps the grouping variable correctly.
    FILL_GEOMS = {"bar", "area", "hist", "boxplot"}

    @classmethod
    def create_theme(cls, x_date: bool = False, **overrides) -> p9.theme:
        """
        Build a p9.theme() object based on BASE_KWARGS.

        Parameters
        ----------
        x_date : bool
            If True, rotates x-axis tick labels by 30 degrees and adjusts
            horizontal alignment, which is useful when the x-axis holds
            dense date labels that would otherwise overlap.
        **overrides :
            Any theme attribute in BASE_KWARGS (or new ones) can be
            overridden here, e.g. create_theme(legend_position="right").

        Returns
        -------
        p9.theme
            Ready to be added to a ggplot object with `+`.
        """
        # Only the x-axis text style depends on whether the axis holds
        # dates; everything else is shared across both branches.
        axis_text_x = (
            p9.element_text(colour="black", size=10, angle=30, hjust=1)
            if x_date
            else p9.element_text(colour="black", size=10, hjust=1)
        )

        # Start from the shared base, then layer axis_text_x and any
        # caller-provided overrides on top (overrides always win).
        kwargs = dict(cls.BASE_KWARGS)
        kwargs["axis_text_x"] = axis_text_x
        kwargs.update(overrides)
        return p9.theme(**kwargs)  # type: ignore

    @classmethod
    def create_figure(cls, df, x, y=None, color=None, kind="line",
                       title="", subtitle=None, xlab="", ylab="",
                       x_date=False, palette=None, alpha=None,
                       stacked=True, bins=30, binwidth=None,
                       jitter_width=0.15, jitter_height=0.0,
                       jitter_size=1.5, jitter_alpha=0.6,
                       swarm=False, swarm_width=0.3, swarm_bins=30,
                       **theme_overrides):
        """
        Build a complete themed ggplot figure in one call.

        This is the "product" method of the factory: it wires together
        the aesthetic mapping, the geometry, the color/fill scale, and
        the theme_dc-based theme, based on the requested `kind`.

        Parameters
        ----------
        df : pandas.DataFrame
            Source data.
        x, y : str
            Column names mapped to the x and y aesthetics. `y` is ignored
            when kind == "hist" (histograms compute counts internally).
        color : str, optional
            Column used to group/color series. Depending on `kind`, this
            is mapped either to the `color` aesthetic (line, scatter) or
            to `fill` (bar, area, hist, boxplot) -- see FILL_GEOMS.
        kind : str
            One of "line", "scatter", "bar", "area", "hist", "boxplot".
        title, subtitle, xlab, ylab : str
            Passed directly to p9.labs().
        x_date : bool
            Forwarded to create_theme(); rotates x-axis labels for dense
            date axes.
        palette : list[str], optional
            Overrides the default `colors` palette.
        alpha : float, optional
            Transparency applied to the geom. For area/hist with
            stacked=False, a default of 0.6 is applied automatically if
            alpha is not explicitly set, so overlapping series stay
            legible.
        stacked : bool
            Controls whether bar/area/hist series are stacked (True,
            default) or placed side-by-side / overlapped (False):
              - bar : dodge (side-by-side bars) instead of stacking.
              - area: identity position (each series drawn independently)
                instead of accumulating values.
              - hist: identity position instead of stacking bin counts.
            Ignored for "boxplot".
        bins, binwidth : int / float, optional
            Only used when kind == "hist". `binwidth` takes precedence
            over `bins` when both are provided.
        jitter_width, jitter_height : float, optional
            Only used when kind == "boxplot" and swarm=False. Control the
            horizontal and vertical spread of the overlaid geom_jitter
            points. Defaults (0.15, 0.0) spread points sideways only,
            preserving each point's true y value.
        jitter_size, jitter_alpha : float, optional
            Only used when kind == "boxplot". Control the marker size and
            transparency of the overlaid points (jitter or beeswarm),
            useful for tuning legibility when the sample size is large.
        swarm : bool, optional
            Only used when kind == "boxplot". If True, replaces the random
            geom_jitter overlay with a deterministic "beeswarm" layout:
            points sharing similar y-values are packed symmetrically
            side-by-side (like a fishbone), instead of being randomly
            scattered. jitter_size/jitter_alpha are still used to style
            the points; jitter_width/jitter_height are ignored in favor
            of swarm_width.
        swarm_width, swarm_bins : float / int, optional
            Only used when swarm=True. `swarm_width` controls the maximum
            horizontal spread within a bin; `swarm_bins` controls how many
            y-value bins are used to group nearby points together before
            packing them (finer bins -> tighter, more literal packing).
        **theme_overrides :
            Forwarded to create_theme(), allowing ad-hoc theme tweaks
            per figure (e.g. legend_position="right").

        Returns
        -------
        p9.ggplot
            Fully assembled figure, ready to `.save()` or display.

        Raises
        ------
        ValueError
            If `kind` is not one of the supported chart types.
        """
        # Fall back to the module-level default palette if none provided.
        palette = palette or colors

        # Determine whether this chart type colors via `fill` (areas/bars/
        # histograms/boxplots) or via `color` (lines/points).
        uses_fill = kind in cls.FILL_GEOMS

        # For beeswarm boxplots, the x-axis must be continuous (so points
        # can be offset by fractional amounts), so categories are first
        # converted to numeric codes; the original labels are restored
        # via scale_x_continuous(breaks=..., labels=...) further below.
        _swarm_categories = None
        if kind == "boxplot" and swarm:
            df = df.copy()
            _swarm_categories = list(pd.Categorical(df[x]).categories)
            df["_dcf_x_code"] = pd.Categorical(
                df[x], categories=_swarm_categories
            ).codes.astype(float)
            x = "_dcf_x_code"

        # Base aesthetic mapping. Histograms do not take an explicit `y`
        # (Plotnine computes bin counts automatically).
        mapping = {"x": x}
        if kind != "hist":
            mapping["y"] = y

        if color:
            if uses_fill:
                # Map the grouping variable to fill so the geom's interior
                # gets colored (not just its outline).
                mapping["fill"] = color
                # bar/hist also need an explicit `group` so that dodge/
                # stack positions correctly separate the categories.
                # boxplot uses `fill` directly as its own grouping variable,
                # so no extra `group` mapping is required (except in the
                # numeric-x swarm case, handled below).
                if kind in ("bar", "hist"):
                    mapping["group"] = color
            else:
                mapping["color"] = color

        # Base plot: data + aesthetic mapping + labels.
        fig = p9.ggplot(df, p9.aes(**mapping)) + p9.labs(
            title=title, subtitle=subtitle, x=xlab, y=ylab
        )

        # Common geom kwargs; alpha is added here if explicitly requested,
        # and may be overridden with a default further below for the
        # "not stacked" cases.
        geom_kwargs = {}
        if alpha is not None:
            geom_kwargs["alpha"] = alpha

        # --- Geometry selection ---------------------------------------
        # Each branch below builds the appropriate geom_*, using `colour`
        # (black outline) plus `fill` (via the aes mapping above) for
        # bar/area/hist/boxplot, so filled shapes are never left with
        # the default black fill.
        if kind == "bar":
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
            # stacked=True -> bars stack on top of each other (default
            # ggplot behavior). stacked=False -> bars are dodged
            # side-by-side per category, avoiding overlap.
            geom_kwargs["position"] = (
                "stack" if stacked else p9.position_dodge(preserve="single")
            )
            geom = p9.geom_col(**geom_kwargs)

        elif kind == "area":
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
            if stacked:
                geom_kwargs["position"] = "stack"
            else:
                # identity: each series' area is drawn independently
                # (not accumulated), so a translucency default is applied
                # to keep overlapping series readable.
                geom_kwargs["position"] = "identity"
                geom_kwargs.setdefault("alpha", 0.6)
            geom = p9.geom_area(**geom_kwargs)

        elif kind == "hist":
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
            # binwidth takes precedence over bins when both are given,
            # matching Plotnine's own geom_histogram() semantics.
            if binwidth is not None:
                geom_kwargs["binwidth"] = binwidth
            else:
                geom_kwargs["bins"] = bins
            if stacked:
                geom_kwargs["position"] = "stack"
            else:
                geom_kwargs["position"] = "identity"
                geom_kwargs.setdefault("alpha", 0.6)
            geom = p9.geom_histogram(**geom_kwargs)

        elif kind == "boxplot":
            # geom_boxplot fills each box according to the `fill`
            # aesthetic (mapped above from `color`) and draws a black
            # outline for contrast. `stacked` and `bins`/`binwidth` do
            # not apply here and are simply ignored.
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
            # Outliers are hidden on the boxplot itself because every
            # individual point is already shown via the point overlay
            # below (jitter or beeswarm); keeping both would duplicate
            # outlier markers.
            geom_kwargs["outlier_shape"] = ""
            # Boxes are drawn semi-transparent so the overlaid points
            # underneath/inside remain visible.
            geom_kwargs.setdefault("alpha", 0.5)
            if swarm:
                # x is now numeric (codes), so boxplot needs an explicit
                # narrow width and a `group` aesthetic to keep boxes
                # separated per category instead of merging into one.
                geom_kwargs.setdefault("width", 0.5)
                mapping["group"] = x
            geom = p9.geom_boxplot(**geom_kwargs)

            if swarm:
                # Beeswarm layout: compute deterministic horizontal
                # offsets per category so points with similar y-values
                # are packed symmetrically side-by-side (fishbone shape),
                # instead of being randomly scattered like geom_jitter.
                df["_dcf_x_swarm"] = df[x]
                for code in np.unique(df[x]):
                    mask = df[x] == code
                    df.loc[mask, "_dcf_x_swarm"] = code + _compute_beeswarm_offsets(
                        df.loc[mask, y].values,
                        width=swarm_width,
                        nbins=swarm_bins,
                    )

                point_mapping = {"x": "_dcf_x_swarm", "y": y}
                if color:
                    point_mapping["colour"] = color

                point_kwargs = dict(size=jitter_size, alpha=jitter_alpha)
                geom_jitter = p9.geom_point(p9.aes(**point_mapping), data=df, **point_kwargs)

                # Re-map the numeric x-axis codes back to the original
                # category labels for display.
                fig_extra_scale = p9.scale_x_continuous(
                    breaks=list(range(len(_swarm_categories))), # type: ignore
                    labels=_swarm_categories,
                )
            else:
                # Overlay raw data points with random horizontal jitter
                # (no vertical jitter, since y is a continuous measured
                # value) so the underlying distribution/sample size is
                # visible alongside the box summary statistics.
                jitter_kwargs = dict(
                    width=jitter_width, height=jitter_height,
                    size=jitter_size, alpha=jitter_alpha,
                )
                if color:
                    jitter_kwargs["colour"] = "black"  # pyright: ignore[reportArgumentType]
                geom_jitter = p9.geom_jitter(**jitter_kwargs) # pyright: ignore[reportArgumentType]
                fig_extra_scale = None

        elif kind == "line":
            geom = p9.geom_line(size=1, **geom_kwargs)

        elif kind == "scatter":
            geom = p9.geom_point(size=2, **geom_kwargs)

        else:
            # Fail fast on unsupported chart types instead of silently
            # producing an incomplete figure.
            raise ValueError(f"Unsupported chart kind: {kind}")

        fig += geom
        if kind == "boxplot":
            fig += geom_jitter # pyright: ignore[reportPossiblyUnboundVariable]
            if swarm and fig_extra_scale is not None: # pyright: ignore[reportPossiblyUnboundVariable]
                fig += fig_extra_scale # pyright: ignore[reportPossiblyUnboundVariable]

        # --- Color/fill scale -------------------------------------------
        # Apply the palette through the correct scale depending on whether
        # this geom uses `fill` or `color` (see uses_fill above).
        if color:
            if uses_fill:
                fig += p9.scale_fill_manual(values=palette)
            else:
                fig += p9.scale_color_manual(values=palette)

        # --- Theme --------------------------------------------------------
        # Apply the shared theme_dc-based theme last, so it does not get
        # overridden by any of the geom/scale layers above.
        fig += cls.create_theme(x_date=x_date, **theme_overrides)
        return fig


def theme_dc(*args, **kwargs):
    """
    Backward-compatible wrapper around DCThemeFactory.create_theme().

    Kept so that legacy code written before the factory existed
    (e.g. `... + theme_dc(x_date=True)`) continues to work unchanged.
    Only keyword arguments are accepted, matching the original API.
    """
    if len(args) > 0:
        raise ValueError(
            "theme_dc() does not accept positional arguments. "
            "Please use keyword arguments only."
        )
    return DCThemeFactory.create_theme(**kwargs)
