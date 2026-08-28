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


class JournalingRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks that the replica set persists majority writes to the journal.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check that the replica set config keeps `writeConcernMajorityJournalDefault` enabled.

        `writeConcernMajorityJournalDefault` is true by default. When it is explicitly
        set to `false`, majority writes are acknowledged without being written to the
        on-disk journal, so acknowledged writes can be lost in the event of a failover.

        Args:
            data (dict): The replica set configuration data in the form
                ``{"config": <replica set config>}``, the same shape consumed by
                :class:`~mongo_x_ray_hc.rules.rs_config_rule.RSConfigRule`.
            extra_info (dict, optional): Extra information such as host. Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        result = []
        config = data["config"]
        set_name: str = config["_id"]
        # The option defaults to true when absent from the config, so only alert
        # when it is explicitly set to false.
        if config.get("writeConcernMajorityJournalDefault") is False:
            issue = create_issue(
                ISSUE.JOURNALING_DISABLED,
                host="cluster",
                params={"set_name": set_name},
            )
            result.append(issue)
        return result, data
