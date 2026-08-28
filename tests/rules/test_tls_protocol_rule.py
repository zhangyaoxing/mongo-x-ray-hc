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
from mongo_x_ray_hc.rules.tls_protocol_rule import TlsProtocolRule

CMDLINE_NO_DISABLED = {"parsed": {"net": {"tls": {}}}}

CMDLINE_DISABLED_TLS10_11 = {"parsed": {"net": {"tls": {"disabledProtocols": "TLS1_0,TLS1_1"}}}}

CMDLINE_DISABLED_TLS10_11_LIST = {"parsed": {"net": {"tls": {"disabledProtocols": ["TLS1_0", "TLS1_1"]}}}}

CMDLINE_DISABLED_ALL = {"parsed": {"net": {"tls": {"disabledProtocols": "TLS1_0,TLS1_1,TLS1_2,TLS1_3"}}}}

CMDLINE_UNRECOGNIZED = {"parsed": {"net": {"tls": {"disabledProtocols": "TLS1_0,TLS2_0"}}}}

CMDLINE_SPACES = {"parsed": {"net": {"tls": {"disabledProtocols": "TLS1_0, TLS1_1"}}}}


def test_no_protocols_disabled():
    rule = TlsProtocolRule({})

    result, _ = rule.apply(CMDLINE_NO_DISABLED, extra_info={"host": "localhost:27017"})
    assert result is not None
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.TLS_UNSAFE_PROTOCOLS_ENABLED
    assert result[0]["severity"] == SEVERITY.MEDIUM
    assert result[0]["title"] == ISSUE_MSG_MAP[ISSUE.TLS_UNSAFE_PROTOCOLS_ENABLED]["title"]
    assert result[0]["host"] == "localhost:27017"
    assert "TLS1_0, TLS1_1" in result[0]["description"]
    assert _ == CMDLINE_NO_DISABLED


def test_tls10_11_disabled():
    rule = TlsProtocolRule({})

    result, _ = rule.apply(CMDLINE_DISABLED_TLS10_11, extra_info={"host": "localhost:27017"})
    assert result == []


def test_tls10_11_disabled_list_shape():
    rule = TlsProtocolRule({})

    result, _ = rule.apply(CMDLINE_DISABLED_TLS10_11_LIST, extra_info={"host": "localhost:27017"})
    assert result == []


def test_all_disabled():
    rule = TlsProtocolRule({})

    result, _ = rule.apply(CMDLINE_DISABLED_ALL, extra_info={"host": "localhost:27017"})
    assert result == []


def test_partially_disabled_unsafe():
    rule = TlsProtocolRule({})

    # Only TLS1_0 disabled -> TLS1_1 still unsafe.
    result, _ = rule.apply(
        {"parsed": {"net": {"tls": {"disabledProtocols": "TLS1_0"}}}}, extra_info={"host": "localhost:27017"}
    )
    assert len(result) == 1
    assert result[0]["id"] == ISSUE.TLS_UNSAFE_PROTOCOLS_ENABLED
    assert "TLS1_1" in result[0]["description"]


def test_unrecognized_protocol():
    rule = TlsProtocolRule({})

    result, _ = rule.apply(CMDLINE_UNRECOGNIZED, extra_info={"host": "localhost:27017"})
    assert len(result) == 2
    assert result[0]["id"] == ISSUE.TLS_UNSAFE_PROTOCOLS_ENABLED
    assert result[1]["id"] == ISSUE.UNRECOGNIZABLE_TLS_PROTOCOL
    assert result[1]["severity"] == SEVERITY.LOW
    assert result[1]["title"] == ISSUE_MSG_MAP[ISSUE.UNRECOGNIZABLE_TLS_PROTOCOL]["title"]
    assert "TLS2_0" in result[1]["description"]


def test_spaces_in_csv():
    rule = TlsProtocolRule({})

    result, _ = rule.apply(CMDLINE_SPACES, extra_info={"host": "localhost:27017"})
    assert result == []
