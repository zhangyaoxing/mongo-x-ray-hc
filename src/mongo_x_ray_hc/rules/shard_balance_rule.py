"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.issues import ISSUE, create_issue
from mongo_x_ray.utils import format_size
from mongo_x_ray_hc.rules.base_rule import BaseRule


class ShardBalanceRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._imbalance_percentage = self._thresholds.get("sharding_imbalance_percentage", 0.2)
        self._rule_desc.append("Checks if shards have an imbalance")

    def apply(self, data: dict, **kwargs) -> tuple:
        """Check shard balance for any issues.

        Args:
            data (dict): The `collStats` document.
            extra_info (dict, optional): Extra information such as host.
        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        shards: list = kwargs.get("extra_info", {}).get("shards", [])
        ns: str = data["ns"]
        test_results: list = []
        shard_stats: dict = {
            s_name: {
                "size": s["size"],
                "count": s["count"],
                "avgObjSize": s.get("avgObjSize", 0),
                "storageSize": s["storageSize"],
                "nindexes": s["nindexes"],
                "totalIndexSize": s["totalIndexSize"],
                "totalSize": s["totalSize"],
            }
            for s_name, s in data["shards"].items()
        }
        # Check if collection is imbalanced.
        sizes: list[int] = [shard_stats.get(s_name, {}).get("size", 0) for s_name in shards]
        max_size = max(sizes)
        min_size = min(sizes)
        if max_size > min_size * (1 + self._imbalance_percentage):
            issue = create_issue(
                ISSUE.IMBALANCED_SHARDING,
                host="cluster",
                params={
                    "ns": ns,
                    "size_diff": format_size(max_size - min_size),
                    "imbalance_percentage": self._imbalance_percentage * 100,
                },
            )
            test_results.append(issue)

        return test_results, shard_stats
