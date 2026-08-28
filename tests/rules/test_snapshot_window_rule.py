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
from mongo_x_ray_hc.rules.snapshot_window_rule import SnapshotWindowRule

SERVER_PARAMETERS_DEFAULT = {"minSnapshotHistoryWindowInSeconds": 300}

SERVER_PARAMETERS_HIGH = {"minSnapshotHistoryWindowInSeconds": 3600}

SERVER_PARAMETERS_RECOMMENDED = {"minSnapshotHistoryWindowInSeconds": 5}

SERVER_PARAMETERS_LOW = {"minSnapshotHistoryWindowInSeconds": 0}

SERVER_PARAMETERS_ABSENT = {}


def test_high_snapshot_window():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply(SERVER_PARAMETERS_DEFAULT, extra_info={"host": "localhost:27017"})
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.HIGH_MIN_SNAPSHOT_WINDOW
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.HIGH_MIN_SNAPSHOT_WINDOW]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert "`300`" in result[0]["description"]
    assert _ == SERVER_PARAMETERS_DEFAULT


def test_high_snapshot_window_very_high():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply(SERVER_PARAMETERS_HIGH, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.HIGH_MIN_SNAPSHOT_WINDOW


def test_recommended_snapshot_window():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply(SERVER_PARAMETERS_RECOMMENDED, extra_info={"host": "localhost:27017"})
    assert result == []


def test_low_snapshot_window():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply(SERVER_PARAMETERS_LOW, extra_info={"host": "localhost:27017"})
    assert result == []


def test_snapshot_window_absent():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply(SERVER_PARAMETERS_ABSENT, extra_info={"host": "localhost:27017"})
    assert result == []


def test_snapshot_window_dict_shape():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply(
        {"minSnapshotHistoryWindowInSeconds": {"value": 300}}, extra_info={"host": "localhost:27017"}
    )
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.HIGH_MIN_SNAPSHOT_WINDOW


def test_snapshot_window_string_value():
    rule = SnapshotWindowRule({})

    result, _ = rule.apply({"minSnapshotHistoryWindowInSeconds": "300"}, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.HIGH_MIN_SNAPSHOT_WINDOW
