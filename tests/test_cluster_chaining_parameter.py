"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

# `enableOverrideClusterChainingSetting` is queried through getParameter for the
# chained replication rule, but recent server versions no longer know the option
# and answer `InvalidOptions: no option found to get` (code 72). That reply used
# to abort the whole cluster level check, so the replica set lost its status,
# config and journaling findings as well.
import pytest
from pymongo.errors import OperationFailure

from mongo_x_ray_hc.check_items.cluster_item import ClusterItem

INVALID_OPTIONS = OperationFailure(
    "no option found to get",
    72,
    {"ok": 0.0, "errmsg": "no option found to get", "code": 72, "codeName": "InvalidOptions"},
)


class _FakeAdmin:
    """Admin database whose getParameter replies with *reply* for known options."""

    def __init__(self, get_parameter):
        self._get_parameter = get_parameter
        self.commands: list = []

    def command(self, name, *args, **_kwargs):
        self.commands.append((name, args))
        if name == "getParameter":
            if isinstance(self._get_parameter, Exception):
                raise self._get_parameter
            return self._get_parameter
        if name == "replSetGetStatus":
            return {"set": "rs0", "members": []}
        if name == "replSetGetConfig":
            return {"config": {"_id": "rs0", "settings": {"chainingAllowed": True}}}
        raise AssertionError(f"unexpected command {name}")


class _FakeClient:
    def __init__(self, get_parameter):
        self.admin = _FakeAdmin(get_parameter)
        self.host = "host1"


class _FakeRule:
    """Rule stub that records what it was applied to and finds nothing."""

    def __init__(self):
        self.applied: list = []

    def apply(self, data, **_kwargs):
        self.applied.append(data)
        return [], data


def _item_with_fake_rules():
    item = ClusterItem("output/")
    item._rules = {name: _FakeRule() for name in ("rs_status", "rs_config", "journaling", "chained_replication")}
    return item


def _node(get_parameter):
    return {"client": _FakeClient(get_parameter), "host": "host1", "pingLatencySec": 0}


def test_chaining_override_is_used_when_the_server_supports_it():
    item = _item_with_fake_rules()
    client = _FakeClient({"enableOverrideClusterChainingSetting": {"value": True}})

    assert item._get_chaining_override(client) == {"enableOverrideClusterChainingSetting": {"value": True}}


def test_chaining_override_missing_on_newer_servers():
    item = _item_with_fake_rules()
    client = _FakeClient(INVALID_OPTIONS)

    # A server that dropped the option is treated as "not set" instead of raising.
    assert item._get_chaining_override(client) == {}


@pytest.mark.parametrize("code", [13, 18])
def test_other_get_parameter_errors_are_not_swallowed(code):
    item = _item_with_fake_rules()
    client = _FakeClient(OperationFailure("not authorized on admin", code))

    with pytest.raises(OperationFailure):
        item._get_chaining_override(client)


def test_cluster_checks_still_produce_results_without_the_option():
    item = _item_with_fake_rules()

    test_result, raw_result = item._check_rs("rs0", _node(INVALID_OPTIONS))

    assert test_result == []
    assert raw_result["replsetStatus"] == {"set": "rs0", "members": []}
    # The chained replication rule still ran, with an empty parameter set.
    assert item._rules["chained_replication"].applied == [
        {"config": {"_id": "rs0", "settings": {"chainingAllowed": True}}, "server_parameters": {}}
    ]
    # Every cluster level rule was applied: the missing option no longer aborts them.
    for name in ("rs_status", "rs_config", "journaling"):
        assert item._rules[name].applied, f"{name} did not run"
