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


class WriteConcernRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks the default write concern settings of the server.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check the server's default write concern settings.

        The default write concern `w` is `majority` by default; when it has been
        changed (e.g. to a numeric count), writes using the default write concern
        may be acknowledged without majority durability. Additionally, a
        `wtimeout` of `0` means writes can block indefinitely waiting for the
        write concern to be satisfied.

        Args:
            data (dict): The serverStatus output.
            extra_info (dict, optional): Extra information such as host. Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        result = []
        default_rw_concern = data.get("defaultRWConcern") or {}
        default_write_concern = default_rw_concern.get("defaultWriteConcern") or {}
        # `majority` is the default when the setting is absent.
        w = default_write_concern.get("w", "majority")
        if w != "majority":
            issue = create_issue(
                ISSUE.NON_DEFAULT_WRITE_CONCERN,
                host=host,
                params={"w": w},
            )
            result.append(issue)
        # `0` is the default when the setting is absent: no timeout at all.
        wtimeout = default_write_concern.get("wtimeout", 0)
        if wtimeout == 0:
            issue = create_issue(
                ISSUE.ZERO_WRITE_CONCERN_TIMEOUT,
                host=host,
            )
            result.append(issue)
        return result, data
