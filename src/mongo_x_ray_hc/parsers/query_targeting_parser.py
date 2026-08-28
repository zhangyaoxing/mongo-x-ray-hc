"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.utils import escape_markdown
from mongo_x_ray_hc.parsers.base_parser import BaseParser


class QueryTargetingParser(BaseParser):
    def parse(self, data, **kwargs) -> list:
        output_list: list = []
        rows: list[list[str]] = []
        qt_table: dict = {
            "type": "table",
            "caption": "Query Targeting",
            "header": [
                {"text": "Component", "width": "120px"},
                {"text": "Host", "width": "*"},
                {"text": "Scanned / Returned", "width": "250px"},
                {"text": "Scanned Objects / Returned", "width": "250px"},
            ],
            "rows": rows,
        }
        output_list.append(qt_table)
        for item in data:
            set_name = item.get("set_name", "unknown_set")
            host = item.get("host", "unknown_host")
            query_targeting = item.get("query_targeting", None)
            if not query_targeting:
                qt_table["rows"].append([escape_markdown(set_name), host, "N/A", "N/A"])
                continue
            qt_table["rows"].append(
                [
                    escape_markdown(set_name),
                    host,
                    f"{query_targeting.get('scanned/returned', 0):.2f}",
                    f"{query_targeting.get('scanned_obj/returned', 0):.2f}",
                ]
            )
        return output_list
