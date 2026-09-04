"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.issues import ISSUE
from mongo_x_ray_hc.rules.security_rule import SecurityRule

DATA_WITH_ISSUES = {
    "parsed": {
        "net": {"port": 27017, "bindIp": "0.0.0.0"},
        "processManagement": {"fork": True},
        "replication": {"replSet": "shard01"},
        "sharding": {"clusterRole": "shardsvr"},
        "storage": {
            "dbPath": "/data/rs1/db",
            "wiredTiger": {"engineConfig": {"cacheSizeGB": 1}},
        },
        "systemLog": {
            "destination": "file",
            "path": "/data/rs1/mongod.log",
        },
    }
}

DATA_WITH_ISSUES_2 = {
    "parsed": {
        "net": {"port": 37017, "bindIp": "192.168.0.1", "tls": {"mode": "allowTLS"}},
        "security": {
            "keyFile": "/data/keyfile",
            "redactClientLogData": True,
            "enableEncryption": True,
            "encryptionKeyFile": "/path/to/keyfile",
        },
        "processManagement": {"fork": True},
        "replication": {"replSet": "shard01"},
        "sharding": {"clusterRole": "shardsvr"},
        "storage": {
            "dbPath": "/data/rs1/db",
            "wiredTiger": {"engineConfig": {"cacheSizeGB": 1}},
        },
        "systemLog": {
            "destination": "file",
            "path": "/data/rs1/mongod.log",
        },
        "auditLog": {"destination": "file", "path": "/data/rs1/audit.log"},
    }
}
DATA_WITH_NO_ISSUES = {
    "parsed": {
        "net": {"port": 37017, "bindIp": "192.168.0.1", "tls": {"mode": "requireTLS"}},
        "security": {
            "keyFile": "/data/keyfile",
            "redactClientLogData": True,
            "enableEncryption": True,
            "kmip": {
                "serverName": "kmip.example.com",
                "port": 5696,
                "clientCertificateFile": "/path/to/cert.pem",
                "serverCAFile": "/path/to/ca.pem",
            },
        },
        "processManagement": {"fork": True},
        "replication": {"replSet": "shard01"},
        "sharding": {"clusterRole": "shardsvr"},
        "storage": {
            "dbPath": "/data/rs1/db",
            "wiredTiger": {"engineConfig": {"cacheSizeGB": 1}},
        },
        "systemLog": {
            "destination": "file",
            "path": "/data/rs1/mongod.log",
        },
        "auditLog": {"destination": "file", "path": "/data/rs1/audit.log"},
    }
}


def test_security_rule_issues():
    rule = SecurityRule({})
    results, _ = rule.apply(DATA_WITH_ISSUES)

    assert len(results) == 7

    issue_ids = {issue["id"] for issue in results}
    expected_issue_ids = {
        ISSUE.AUTHORIZATION_DISABLED,
        ISSUE.LOG_REDACTION_DISABLED,
        ISSUE.TLS_DISABLED,
        ISSUE.OPEN_BIND_IP,
        ISSUE.DEFAULT_PORT_USED,
        ISSUE.AUDITING_DISABLED,
        ISSUE.ENCRYPTION_AT_REST_DISABLED,
    }

    assert issue_ids == expected_issue_ids


def test_security_rule_issues_2():
    rule = SecurityRule({})
    results, _ = rule.apply(DATA_WITH_ISSUES_2)

    assert len(results) == 2

    issue_ids = {issue["id"] for issue in results}
    expected_issue_ids = {
        ISSUE.OPTIONAL_TLS,
        ISSUE.ENCRYPTION_AT_REST_USING_KEYFILE,
    }

    assert issue_ids == expected_issue_ids


def test_security_rule_no_issues():
    rule = SecurityRule({})
    results, _ = rule.apply(DATA_WITH_NO_ISSUES)

    assert len(results) == 0


MONGOS_CMDLINE = {
    "argv": ["/usr/bin/mongos", "--configdb", "cfg/rs:27019"],
    "parsed": {
        "net": {"port": 27017, "bindIp": "0.0.0.0"},
        "sharding": {"configDB": "cfg/rs:27019"},
        "processManagement": {"fork": True},
        "systemLog": {"destination": "file", "path": "/var/log/mongos.log"},
    },
}

MONGOD_CMDLINE = {
    "argv": ["/usr/bin/mongod", "--replSet", "rs0"],
    "parsed": {
        "net": {"port": 27017, "bindIp": "0.0.0.0"},
        "storage": {"dbPath": "/data/db"},
        "replication": {"replSet": "rs0"},
    },
}


def test_security_rule_mongos_skips_encryption_at_rest():
    rule = SecurityRule({})
    results, _ = rule.apply(MONGOS_CMDLINE)

    issue_ids = {issue["id"] for issue in results}
    assert ISSUE.ENCRYPTION_AT_REST_DISABLED not in issue_ids
    # Other mongos checks still run.
    assert ISSUE.AUTHORIZATION_DISABLED in issue_ids
    assert ISSUE.TLS_DISABLED in issue_ids


def test_security_rule_mongod_reports_encryption_at_rest():
    rule = SecurityRule({})
    results, _ = rule.apply(MONGOD_CMDLINE)

    issue_ids = {issue["id"] for issue in results}
    assert ISSUE.ENCRYPTION_AT_REST_DISABLED in issue_ids
