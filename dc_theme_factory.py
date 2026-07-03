# -*- coding: utf-8 -*-
"""
dc_theme_factory.py

DCThemeFactory: A Factory Method implementation for creating consistently
themed Plotnine charts based on the custom `theme_dc()` theme.

Author:  Diego Carvalho
Contact: diego.carvalho@cefet-rj.br
Institution: CEFET/RJ - Centro Federal de Educacao Tecnologica
             Celso Suckow da Fonseca

Copyright (c) 2026 Diego Carvalho

This work is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).
To view a copy of this license, visit:
    https://creativecommons.org/licenses/by-sa/4.0/

You are free to:
  - Share    : copy and redistribute the material in any medium or format.
  - Adapt    : remix, transform, and build upon the material for any
               purpose, even commercially.

Under the following terms:
  - Attribution  : You must give appropriate credit, provide a link to
                   the license, and indicate if changes were made.
  - ShareAlike   : If you remix, transform, or build upon the material,
                   you must distribute your contributions under the same
                   license as the original.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""

import pandas as pd
import plotnine as p9
import numpy as np
import os

#colors = ["#0C87D1", "#40b8d0", "#193375", "#19AE47", "#FFCB05", "#b2d183", "#FDDC02",]

p_colors = [
    "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF",
    "#BDB2FF", "#FFC6FF", "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9",
    "#BAE1FF", "#D4A5A5", "#C9C9FF", "#FFCCE5", "#B5EAD7", "#C7CEEA",
    "#FFDAC1", "#E2F0CB", "#B2DFDB", "#F8C8DC", "#D0F4DE", "#A9DEF9",
    "#E4C1F9", "#FCF6BD", "#FF99C8", "#FCF6B1", "#D0BDF4", "#8EECF5",
    "#B9FBC0", "#F1C0E8",
]

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

    FILL_GEOMS = {"bar", "area", "hist"}

    @classmethod
    def create_theme(cls, x_date: bool = False, **overrides) -> p9.theme:
        axis_text_x = (
            p9.element_text(colour="black", size=10, angle=30, hjust=1)
            if x_date
            else p9.element_text(colour="black", size=10, hjust=1)
        )
        kwargs = dict(cls.BASE_KWARGS)
        kwargs["axis_text_x"] = axis_text_x
        kwargs.update(overrides)
        return p9.theme(**kwargs) # type: ignore

    @classmethod
    def create_figure(cls, df, x, y=None, color=None, kind="line",
                       title="", subtitle=None, xlab="", ylab="",
                       x_date=False, palette=None, alpha=None,
                       stacked=True, bins=30, binwidth=None,
                       **theme_overrides):
        palette = palette or colors
        uses_fill = kind in cls.FILL_GEOMS

        mapping = {"x": x}
        if kind != "hist":
            mapping["y"] = y

        if color:
            if uses_fill:
                mapping["fill"] = color
                if kind in ("bar", "hist"):
                    mapping["group"] = color
            else:
                mapping["color"] = color

        fig = p9.ggplot(df, p9.aes(**mapping)) + p9.labs(
            title=title, subtitle=subtitle, x=xlab, y=ylab
        )

        geom_kwargs = {}
        if alpha is not None:
            geom_kwargs["alpha"] = alpha

        if kind == "bar":
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
            geom_kwargs["position"] = "stack" if stacked else p9.position_dodge(preserve="single")
            geom = p9.geom_col(**geom_kwargs)
        elif kind == "area":
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
            if stacked:
                geom_kwargs["position"] = "stack"
            else:
                geom_kwargs["position"] = "identity"
                geom_kwargs.setdefault("alpha", 0.6)
            geom = p9.geom_area(**geom_kwargs)
        elif kind == "hist":
            geom_kwargs["colour"] = "black"
            geom_kwargs["size"] = 0.3
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
        elif kind == "line":
            geom = p9.geom_line(size=1, **geom_kwargs)
        elif kind == "scatter":
            geom = p9.geom_point(size=2, **geom_kwargs)
        else:
            raise ValueError(f"Unsupported chart kind: {kind}")

        fig += geom

        if color:
            if uses_fill:
                fig += p9.scale_fill_manual(values=palette)
            else:
                fig += p9.scale_color_manual(values=palette)

        fig += cls.create_theme(x_date=x_date, **theme_overrides)
        return fig


def theme_dc(*args, **kwargs):
    if len(args) > 0:
        raise ValueError("theme_dc() does not accept positional arguments. Please use keyword arguments only.")
    return DCThemeFactory.create_theme(**kwargs)
