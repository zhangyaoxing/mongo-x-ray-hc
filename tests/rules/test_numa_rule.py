"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray.version import Version
from mongo_x_ray_hc.issues import ISSUE
from mongo_x_ray_hc.rules.numa_rule import NumaRule

DATA_DISABLED = {"system": {"numaEnabled": False}}

DATA_ENABLED = {"system": {"numaEnabled": True}}

VERSION_6_0 = Version.parse("6.0.2")
VERSION_8_0 = Version.parse("8.0.15")


def test_numa_rule_disabled_no_alert():
    # NUMA disabled is the recommended state on every MongoDB version.
    rule = NumaRule({})
    for version in (VERSION_6_0, VERSION_8_0):
        issues, _ = rule.apply(DATA_DISABLED, extra_info={"host": "localhost", "version": version})
        assert len(issues) == 0


def test_numa_rule_enabled_alert_on_all_versions():
    rule = NumaRule({})
    for version in (VERSION_6_0, VERSION_8_0):
        issues, _ = rule.apply(DATA_ENABLED, extra_info={"host": "localhost", "version": version})
        assert len(issues) == 1
        assert issues[0]["id"] == ISSUE.NUMA_ENABLED
        assert issues[0]["severity"] == SEVERITY.HIGH
