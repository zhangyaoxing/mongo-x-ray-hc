"""Healthcheck parser base — subclass of the shared core parser."""

import os

from x_ray.parsers.base_parser import TABLE_ALIGNMENT
from x_ray.parsers.base_parser import BaseParser as CoreBaseParser


class BaseParser(CoreBaseParser):
    """Render healthcheck results using the common table/chart format."""

    TEMPLATE_FOLDER = os.path.join("templates", "healthcheck", "snippets")
    TEMPLATE_PACKAGE = "x_ray_healthcheck"


__all__ = ["BaseParser", "TABLE_ALIGNMENT"]
