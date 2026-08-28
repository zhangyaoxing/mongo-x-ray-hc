"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.issues import ISSUE, ISSUE_MSG_MAP
from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_hc.rules.write_concern_rule import WriteConcernRule

SERVER_STATUS_CLEAN = {
    "process": "mongod",
    "defaultRWConcern": {
        "defaultReadConcern": {"level": "local"},
        "defaultWriteConcern": {"w": "majority", "wtimeout": 5000},
    },
}

SERVER_STATUS_MAJORITY_ZERO_TIMEOUT = {
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

SERVER_STATUS_NON_DEFAULT_WITH_TIMEOUT = {
    "process": "mongod",
    "defaultRWConcern": {
        "defaultWriteConcern": {"w": "1", "wtimeout": 10000},
    },
}

# No defaultRWConcern -> w defaults to majority, wtimeout to 0 (no timeout).
SERVER_STATUS_NO_WRITE_CONCERN = {"process": "mongod"}

# defaultRWConcern present but no defaultWriteConcern -> majority default, no timeout.
SERVER_STATUS_NO_DEFAULT_WRITE_CONCERN = {
    "process": "mongod",
    "defaultRWConcern": {"defaultReadConcern": {"level": "local"}},
}


def test_write_concern_clean():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_CLEAN, extra_info={"host": "localhost:27017"})
    assert result == []
    assert _ == SERVER_STATUS_CLEAN


def test_write_concern_zero_timeout():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_MAJORITY_ZERO_TIMEOUT, extra_info={"host": "localhost:27017"})
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.ZERO_WRITE_CONCERN_TIMEOUT
    assert result[0]["severity"] == SEVERITY.LOW
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.ZERO_WRITE_CONCERN_TIMEOUT]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert _ == SERVER_STATUS_MAJORITY_ZERO_TIMEOUT


def test_write_concern_missing_defaults_to_majority():
    rule = WriteConcernRule({})

    # No defaultRWConcern at all: w is majority, but there is no timeout.
    result, _ = rule.apply(SERVER_STATUS_NO_WRITE_CONCERN, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.ZERO_WRITE_CONCERN_TIMEOUT

    result, _ = rule.apply(SERVER_STATUS_NO_DEFAULT_WRITE_CONCERN, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.ZERO_WRITE_CONCERN_TIMEOUT


def test_write_concern_non_default_string():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_NON_DEFAULT_STR, extra_info={"host": "localhost:27017"})
    assert len(result) == 2
    assert result[0]["id"] == ISSUE.NON_DEFAULT_WRITE_CONCERN
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.NON_DEFAULT_WRITE_CONCERN]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert "`1`" in result[0]["description"]
    assert result[1]["id"] == ISSUE.ZERO_WRITE_CONCERN_TIMEOUT
    assert _ == SERVER_STATUS_NON_DEFAULT_STR


def test_write_concern_non_default_number():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_NON_DEFAULT_NUM, extra_info={"host": "localhost:27017"})
    assert len(result) == 2
    assert result[0]["id"] == ISSUE.NON_DEFAULT_WRITE_CONCERN
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[1]["id"] == ISSUE.ZERO_WRITE_CONCERN_TIMEOUT


def test_write_concern_non_default_with_timeout():
    rule = WriteConcernRule({})

    result, _ = rule.apply(SERVER_STATUS_NON_DEFAULT_WITH_TIMEOUT, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.NON_DEFAULT_WRITE_CONCERN
    assert result[0]["severity"] == SEVERITY.MEDIUM
