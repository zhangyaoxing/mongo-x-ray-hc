"""
Copyright (c) 2025 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY

from mongo_x_ray_hc.issues import ISSUE, ISSUE_MSG_MAP
from mongo_x_ray_hc.rules.journaling_rule import JournalingRule

CONFIG_JOURNALING_DISABLED = {
    "config": {
        "_id": "shard01",
        "version": 2,
        "term": 558,
        "writeConcernMajorityJournalDefault": False,
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

CONFIG_JOURNALING_ENABLED = {
    "config": {
        "_id": "shard01",
        "version": 2,
        "term": 558,
        "writeConcernMajorityJournalDefault": True,
        "members": CONFIG_JOURNALING_DISABLED["config"]["members"],
    }
}

# writeConcernMajorityJournalDefault defaults to true when not present in the config.
CONFIG_JOURNALING_NOT_SET = {
    "config": {
        "_id": "shard01",
        "version": 2,
        "term": 558,
        "members": CONFIG_JOURNALING_DISABLED["config"]["members"],
    }
}


def test_journaling_disabled():
    rule = JournalingRule({})

    result, _ = rule.apply(CONFIG_JOURNALING_DISABLED, extra_info={"host": "cluster"})
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.JOURNALING_DISABLED
    assert result[0]["severity"] == SEVERITY.HIGH
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.JOURNALING_DISABLED]["title"]
    assert result[0]["host"] == "cluster"
    assert _ == CONFIG_JOURNALING_DISABLED


def test_journaling_enabled():
    rule = JournalingRule({})

    result, _ = rule.apply(CONFIG_JOURNALING_ENABLED, extra_info={"host": "cluster"})
    assert result == []
    assert _ == CONFIG_JOURNALING_ENABLED


def test_journaling_default_enabled():
    rule = JournalingRule({})

    result, _ = rule.apply(CONFIG_JOURNALING_NOT_SET, extra_info={"host": "cluster"})
    assert result == []
    assert _ == CONFIG_JOURNALING_NOT_SET
