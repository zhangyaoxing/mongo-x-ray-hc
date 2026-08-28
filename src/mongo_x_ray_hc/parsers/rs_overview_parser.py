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


class RSOverviewParser(BaseParser):
    def parse(self, data: list, **kwargs) -> list:
        """
        Parse replica set information data.

        Args:
            data (list): Each element is a tuple: (`RS name`, `RS config dict or None`)

        Returns:
            list: The parsed replica set information as a list of table items.
        """
        rows: list[list] = []
        overview_table = {
            "type": "table",
            "caption": "Components Overview",
            "header": [
                {"text": "Name", "width": "*"},
                {"text": "#Members", "width": "120px"},
                {"text": "#Votings", "width": "120px"},
                {"text": "#Arbiters", "width": "120px"},
                {"text": "#Hiddens", "width": "120px"},
            ],
            "rows": rows,
        }
        for set_name, rs_config in data:
            if rs_config is None:
                rows.append([set_name, "N/A" * 4])
                continue
            members = rs_config["members"]
            num_members = len(members)
            num_voting = sum(1 for m in members if m["votes"] > 0)
            num_arbiters = sum(1 for m in members if m["arbiterOnly"])
            num_hidden = sum(1 for m in members if m["hidden"])
            rows.append(
                [
                    escape_markdown(rs_config["_id"]),
                    num_members,
                    num_voting,
                    num_arbiters,
                    num_hidden,
                ]
            )
        return [overview_table]
