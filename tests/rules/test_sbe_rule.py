"""
Copyright (c) 2025 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.issues import ISSUE, ISSUE_MSG_MAP
from mongo_x_ray.shared import SEVERITY
from mongo_x_ray.version import Version

from mongo_x_ray_hc.rules.sbe_rule import SbeRule

V6 = Version.parse("6.0.30")
V7 = Version.parse("7.0.37")
V5 = Version.parse("5.0.0")
V8 = Version.parse("8.0.0")

PARAMS_6_CLASSIC = {"internalQueryForceClassicEngine": True}
PARAMS_6_SBE = {"internalQueryForceClassicEngine": False}
PARAMS_7_CLASSIC = {"internalQueryFrameworkControl": "forceClassicEngine"}
PARAMS_7_SBE = {"internalQueryFrameworkControl": "trySbeRestricted"}
PARAMS_EMPTY = {}


def _apply(rule, params, version, host="localhost:27017"):
    return rule.apply(params, extra_info={"host": host, "version": version})


def test_sbe_disabled_6_0():
    rule = SbeRule({})

    result, _ = _apply(rule, PARAMS_6_CLASSIC, V6)
    assert result == []
    assert _ == PARAMS_6_CLASSIC


def test_sbe_enabled_6_0():
    rule = SbeRule({})

    result, _ = _apply(rule, PARAMS_6_SBE, V6)
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.SBE_ENABLED
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.SBE_ENABLED]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert "internalQueryForceClassicEngine" in result[0]["description"]


def test_sbe_enabled_6_0_missing_param_defaults_to_enabled():
    rule = SbeRule({})

    result, _ = _apply(rule, PARAMS_EMPTY, V6)
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.SBE_ENABLED


def test_sbe_disabled_7_0():
    rule = SbeRule({})

    result, _ = _apply(rule, PARAMS_7_CLASSIC, V7)
    assert result == []
    assert _ == PARAMS_7_CLASSIC


def test_sbe_enabled_7_0():
    rule = SbeRule({})

    result, _ = _apply(rule, PARAMS_7_SBE, V7)
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.SBE_ENABLED
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert "internalQueryFrameworkControl" in result[0]["description"]


def test_sbe_enabled_7_0_missing_param_defaults_to_enabled():
    rule = SbeRule({})

    result, _ = _apply(rule, PARAMS_EMPTY, V7)
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.SBE_ENABLED


def test_sbe_not_checked_on_other_versions():
    rule = SbeRule({})

    for params in (PARAMS_6_SBE, PARAMS_7_SBE):
        assert _apply(rule, params, V5)[0] == []
        assert _apply(rule, params, V8)[0] == []


def test_sbe_not_checked_without_version():
    rule = SbeRule({})

    result, _ = rule.apply(PARAMS_7_SBE, extra_info={"host": "localhost:27017"})
    assert result == []
