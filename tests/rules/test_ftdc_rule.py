"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.shared import SEVERITY
from mongo_x_ray_hc.issues import ISSUE, ISSUE_MSG_MAP
from mongo_x_ray_hc.rules.ftdc_rule import FtdcRule

PARAMS_OK = {"diagnosticDataCollectionEnabled": True, "diagnosticDataCollectionSamplesPerChunk": 300}

PARAMS_DISABLED = {"diagnosticDataCollectionEnabled": False, "diagnosticDataCollectionSamplesPerChunk": 300}

PARAMS_SMALL_CHUNK = {"diagnosticDataCollectionEnabled": True, "diagnosticDataCollectionSamplesPerChunk": 200}

PARAMS_BOTH = {"diagnosticDataCollectionEnabled": False, "diagnosticDataCollectionSamplesPerChunk": 100}

PARAMS_EMPTY = {}


def test_ftdc_ok():
    rule = FtdcRule({})

    result, _ = rule.apply(PARAMS_OK, extra_info={"host": "localhost:27017"})
    assert result == []
    assert _ == PARAMS_OK


def test_ftdc_disabled():
    rule = FtdcRule({})

    result, _ = rule.apply(PARAMS_DISABLED, extra_info={"host": "localhost:27017"})
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.FTDC_DISABLED
    assert result[0]["severity"] == SEVERITY.HIGH
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.FTDC_DISABLED]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert _ == PARAMS_DISABLED


def test_ftdc_chunk_too_small():
    rule = FtdcRule({})

    result, _ = rule.apply(PARAMS_SMALL_CHUNK, extra_info={"host": "localhost:27017"})
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.FTDC_SAMPLES_TOO_SMALL
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.FTDC_SAMPLES_TOO_SMALL]["title"]
    assert "`200`" in result[0]["description"]


def test_ftdc_both_issues():
    rule = FtdcRule({})

    result, _ = rule.apply(PARAMS_BOTH, extra_info={"host": "localhost:27017"})
    assert len(result) == 2
    assert result[0]["id"] == ISSUE.FTDC_DISABLED
    assert result[1]["id"] == ISSUE.FTDC_SAMPLES_TOO_SMALL


def test_ftdc_missing_defaults_ok():
    rule = FtdcRule({})

    result, _ = rule.apply(PARAMS_EMPTY, extra_info={"host": "localhost:27017"})
    assert result == []


def test_ftdc_dict_shape():
    rule = FtdcRule({})

    result, _ = rule.apply(
        {
            "diagnosticDataCollectionEnabled": False,
            "diagnosticDataCollectionSamplesPerChunk": {"value": 100},
        },
        extra_info={"host": "localhost:27017"},
    )
    assert len(result) == 2
