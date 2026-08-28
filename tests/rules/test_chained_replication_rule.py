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

from mongo_x_ray_hc.rules.chained_replication_rule import ChainedReplicationRule

RS_CONFIG = {
    "config": {
        "_id": "shard01",
        "version": 2,
        "term": 558,
        "members": [
            {
                "_id": 0,
                "host": "localhost:30018",
                "arbiterOnly": False,
                "hidden": False,
                "priority": 1,
                "secondaryDelaySecs": 0,
                "votes": 1,
            },
            {
                "_id": 1,
                "host": "localhost:30019",
                "arbiterOnly": False,
                "hidden": False,
                "priority": 1,
                "secondaryDelaySecs": 0,
                "votes": 1,
            },
            {
                "_id": 2,
                "host": "localhost:30020",
                "arbiterOnly": False,
                "hidden": False,
                "priority": 1,
                "secondaryDelaySecs": 0,
                "votes": 1,
            },
        ],
    }
}

CONFIG_CHAINING_ALLOWED = {"config": {**RS_CONFIG["config"], "settings": {"chainingAllowed": True}}}

# chainingAllowed defaults to true when missing from the config.
CONFIG_CHAINING_NOT_SET = {"config": {**RS_CONFIG["config"]}}

CONFIG_CHAINING_DISABLED = {"config": {**RS_CONFIG["config"], "settings": {"chainingAllowed": False}}}

SERVER_PARAMETERS_OVERRIDE_ENABLED = {"enableOverrideClusterChainingSetting": True}

SERVER_PARAMETERS_OVERRIDE_DISABLED = {"enableOverrideClusterChainingSetting": False}


def _apply(rule, config, server_parameters=None, host="cluster"):
    data = {"config": config["config"]}
    if server_parameters is not None:
        data["server_parameters"] = server_parameters
    return rule.apply(data, extra_info={"host": host})


def test_chaining_allowed():
    rule = ChainedReplicationRule({})

    result, _ = _apply(rule, CONFIG_CHAINING_ALLOWED)
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.CHAINED_REPLICATION_ALLOWED
    assert result[0]["severity"] == SEVERITY.LOW
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.CHAINED_REPLICATION_ALLOWED]["title"]
    assert result[0]["host"] == "cluster"
    assert "chainingAllowed" in result[0]["description"]
    assert _ == {"config": CONFIG_CHAINING_ALLOWED["config"]}


def test_chaining_default_allowed():
    rule = ChainedReplicationRule({})

    result, _ = _apply(rule, CONFIG_CHAINING_NOT_SET)
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.CHAINED_REPLICATION_ALLOWED
    assert result[0]["severity"] == SEVERITY.LOW


def test_chaining_disabled_no_override():
    rule = ChainedReplicationRule({})

    result, _ = _apply(rule, CONFIG_CHAINING_DISABLED, SERVER_PARAMETERS_OVERRIDE_DISABLED)
    assert result == []


def test_chaining_disabled_no_params():
    rule = ChainedReplicationRule({})

    result, _ = _apply(rule, CONFIG_CHAINING_DISABLED)
    assert result == []


def test_chaining_disabled_with_override():
    rule = ChainedReplicationRule({})

    result, _ = _apply(rule, CONFIG_CHAINING_DISABLED, SERVER_PARAMETERS_OVERRIDE_ENABLED)
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.CHAINED_REPLICATION_ALLOWED
    assert result[0]["severity"] == SEVERITY.LOW


def test_chaining_override_dict_shape():
    rule = ChainedReplicationRule({})

    # Some getParameter values are wrapped in a dict with a "value" key.
    result, _ = _apply(
        rule,
        CONFIG_CHAINING_DISABLED,
        {"enableOverrideClusterChainingSetting": {"value": True}},
    )
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.CHAINED_REPLICATION_ALLOWED

    result, _ = _apply(
        rule,
        CONFIG_CHAINING_DISABLED,
        {"enableOverrideClusterChainingSetting": {"value": False}},
    )
    assert result == []
