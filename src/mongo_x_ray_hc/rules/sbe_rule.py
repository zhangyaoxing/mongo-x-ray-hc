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


class SbeRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks that the slot-based execution engine (SBE) is disabled on MongoDB 6.0 and 7.0.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check that SBE is disabled on MongoDB 6.0 and 7.0.

        The slot-based execution engine has been known to cause performance
        issues on MongoDB 6.0 and 7.0:

        - 6.0: SBE is disabled when `internalQueryForceClassicEngine` is `true`
          (the parameter defaults to `false`, i.e. SBE enabled).
        - 7.0: SBE is disabled when `internalQueryFrameworkControl` is
          `forceClassicEngine` (any other value means SBE enabled).

        Args:
            data (dict): The `getParameter` output, e.g. from the
                `server_parameters` subsection of a getMongoData dump.
            extra_info (dict, optional): Extra information such as host and
                version (a `mongo_x_ray.version.Version`). Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        version = kwargs.get("extra_info", {}).get("version")
        result = []
        if version is None:
            return result, data

        if version.major_version == 6:
            # Default is false -> SBE enabled.
            force_classic = data.get("internalQueryForceClassicEngine", False)
            if force_classic is not True:
                result.append(
                    create_issue(
                        ISSUE.SBE_ENABLED,
                        host=host,
                        params={
                            "version": "6.0",
                            "parameter": "internalQueryForceClassicEngine",
                            "value": force_classic,
                        },
                    )
                )
        elif version.major_version == 7:
            # Default is not forceClassicEngine -> SBE enabled.
            framework_control = data.get("internalQueryFrameworkControl", "trySbeRestricted")
            if framework_control != "forceClassicEngine":
                result.append(
                    create_issue(
                        ISSUE.SBE_ENABLED,
                        host=host,
                        params={
                            "version": "7.0",
                            "parameter": "internalQueryFrameworkControl",
                            "value": framework_control,
                        },
                    )
                )
        return result, data
