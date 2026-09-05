"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_hc.issues import ISSUE, create_issue
from mongo_x_ray_hc.rules.base_rule import BaseRule


class NumaRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks that NUMA is disabled.")

    def apply(self, data: dict, **kwargs) -> tuple:
        """Check the NUMA node configuration for any issues.

        NUMA should be disabled for database servers on all MongoDB versions.

        Args:
            data (dict): The `hostInfo` command result.
        Returns:
            tuple: (list of issues found, list of parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        version = kwargs.get("extra_info", {}).get("version", None)
        test_result = []
        numa_enabled = data.get("system", {}).get("numaEnabled", None)
        if numa_enabled is not None and numa_enabled:
            issue = create_issue(ISSUE.NUMA_ENABLED, host, params={"version": version, "host": host})
            test_result.append(issue)

        return test_result, data
