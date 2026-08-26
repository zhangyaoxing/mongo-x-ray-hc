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
from mongo_x_ray_hc.rules.write_concern_rule import WriteConcernRule

SERVER_STATUS_MAJORITY = {
    "process": "mongod",
    "defaultRWConcern": {
        "defaultReadConcern": {"level": "local"},
        "defaultWriteConcern": {"w": "majority", "wtimeout": 0},
    },
}

SERVER_STATUS_NON_DEFAULT_STR = {
    "process": "mongod",
    "defaultRWConcern": {
        "defaultWriteConcern": {"w": "1", "wtimeout": 0},
    },
}

SERVER_STATUS_NON_DEFAULT_NUM = {
    "process": "mongod",
    "defaultRWConcern": {
        "defaultWriteConcern": {"w": 1, "wtimeout": 0},
    },
}

# No defaultRWConcern -> the default write concern is still majority.
SERVER_STATUS_NO_WRITE_CONCERN = {"process": "mongod"}

# defaultRWConcern present but no defaultWriteConcern -> majority default.
SERVER_STATUS_NO_DEFAULT_WRITE_CONCERN = {"process": "mongod", "defaultRWConcern": {"defaultReadConcern": {"level": "local"}}}


def test_write_concern_majority():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_MAJORITY, extra_info={"host": "localhost:27017"})
    assert result == []
    assert _ == SERVER_STATUS_MAJORITY


def test_write_concern_missing_defaults_to_majority():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_NO_WRITE_CONCERN, extra_info={"host": "localhost:27017"})
    assert result == []

    result, _ = rule.apply(SERVER_STATUS_NO_DEFAULT_WRITE_CONCERN, extra_info={"host": "localhost:27017"})
    assert result == []


def test_write_concern_non_default_string():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_NON_DEFAULT_STR, extra_info={"host": "localhost:27017"})
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.NON_DEFAULT_WRITE_CONCERN
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.NON_DEFAULT_WRITE_CONCERN]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert "`1`" in result[0]["description"]
    assert _ == SERVER_STATUS_NON_DEFAULT_STR


def test_write_concern_non_default_number():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_NON_DEFAULT_NUM, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.NON_DEFAULT_WRITE_CONCERN
    assert result[0]["severity"] == SEVERITY.MEDIUM
