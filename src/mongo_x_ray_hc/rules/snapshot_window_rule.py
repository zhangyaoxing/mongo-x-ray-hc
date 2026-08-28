"""
Copyright (c) 2025 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.issues import ISSUE, create_issue

from mongo_x_ray_hc.rules.base_rule import BaseRule

# Recommended value on data-bearing nodes (MongoDB 5.0+): 5 seconds.
RECOMMENDED_MIN_SNAPSHOT_HISTORY_WINDOW = 5


class SnapshotWindowRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks that `minSnapshotHistoryWindowInSeconds` is not set too high.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check that `minSnapshotHistoryWindowInSeconds` is not too high.

        A high value has been known to cause performance issues on MongoDB 5.0
        and above, because the cache keeps excessive snapshot history. The
        general recommendation is 5 seconds on data-bearing nodes when the
        snapshot read concern is not needed.

        Args:
            data (dict): The `getParameter` output, e.g. from the
                `server_parameters` subsection of a getMongoData dump.
            extra_info (dict, optional): Extra information such as host. Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        result = []
        value = data.get("minSnapshotHistoryWindowInSeconds")
        if isinstance(value, dict):
            value = value.get("value", value)
        if value is not None:
            try:
                too_high = int(value) > RECOMMENDED_MIN_SNAPSHOT_HISTORY_WINDOW
            except (TypeError, ValueError):
                too_high = False
            if too_high:
                issue = create_issue(
                    ISSUE.HIGH_MIN_SNAPSHOT_WINDOW,
                    host=host,
                    params={"value": int(value)},
                )
                result.append(issue)
        return result, data
