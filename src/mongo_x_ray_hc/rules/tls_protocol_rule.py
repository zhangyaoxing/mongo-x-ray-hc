"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_hc.issues import ISSUE, create_issue
from mongo_x_ray_hc.rules.base_rule import BaseRule

KNOWN_PROTOCOLS = ("TLS1_0", "TLS1_1", "TLS1_2", "TLS1_3")
UNSAFE_PROTOCOLS = ("TLS1_0", "TLS1_1")


def _parse_protocols(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [p.strip() for p in value.split(",") if p.strip()]
    if isinstance(value, (list, tuple)):
        return [str(p).strip() for p in value if str(p).strip()]
    return []


class TlsProtocolRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks that insecure TLS protocols are disabled.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check `net.tls.disabledProtocols` from the command line options.

        - TLS1_0 and TLS1_1 are considered insecure: if either is not in the
          disabled list, a MEDIUM alert is raised.
        - Any protocol outside TLS1_0..TLS1_3 is unrecognized: a LOW alert is
          raised.

        Args:
            data (dict): The getCmdLineOpts output.
            extra_info (dict, optional): Extra information such as host. Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        result = []
        tls = data.get("parsed", {}).get("net", {}).get("tls", {})
        disabled = _parse_protocols(tls.get("disabledProtocols"))

        unsafe = [p for p in UNSAFE_PROTOCOLS if p not in disabled]
        if unsafe:
            result.append(
                create_issue(
                    ISSUE.TLS_UNSAFE_PROTOCOLS_ENABLED,
                    host=host,
                    params={"protocols": ", ".join(unsafe)},
                )
            )
        unrecognized = [p for p in disabled if p not in KNOWN_PROTOCOLS]
        if unrecognized:
            result.append(
                create_issue(
                    ISSUE.UNRECOGNIZABLE_TLS_PROTOCOL,
                    host=host,
                    params={"protocols": ", ".join(unrecognized)},
                )
            )
        return result, data
