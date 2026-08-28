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


class ChainedReplicationRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks that chained replication is disabled for the replica set.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check whether chained replication is possible for the replica set.

        Chained replication is allowed when ``settings.chainingAllowed`` is true
        (the default when the setting is missing from the config), or when the
        ``enableOverrideClusterChainingSetting`` server parameter is true, which
        permits chaining even when ``chainingAllowed`` is false.

        Args:
            data (dict): Dictionary with:
                - config: the replica set configuration in the form
                  ``{"config": <replica set config>}``, the same shape consumed by
                  :class:`~mongo_x_ray_hc.rules.rs_config_rule.RSConfigRule`.
                - server_parameters: the ``getParameter`` output, e.g. from the
                  ``server_parameters`` subsection of a getMongoData dump.
            extra_info (dict, optional): Extra information such as host. Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        result = []
        config = data["config"]
        set_name: str = config["_id"]
        server_parameters = data.get("server_parameters") or {}

        settings = config.get("settings", {})
        chaining_allowed = settings.get("chainingAllowed", True)
        override = server_parameters.get("enableOverrideClusterChainingSetting", False)
        if isinstance(override, dict):
            override = override.get("value", False)

        if chaining_allowed or override:
            issue = create_issue(
                ISSUE.CHAINED_REPLICATION_ALLOWED,
                host="cluster",
                params={
                    "set_name": set_name,
                    "chaining_allowed": chaining_allowed,
                    "override": override,
                },
            )
            result.append(issue)
        return result, data
