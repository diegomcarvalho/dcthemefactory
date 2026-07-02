# -*- coding: utf-8 -*-
"""
__init__.py

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

from dc_theme_factory import DCThemeFactory, theme_dc

__all__ = ["DCThemeFactory", "theme_dc"]