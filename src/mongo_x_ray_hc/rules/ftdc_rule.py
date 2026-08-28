"""
Copyright (c) 2025 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.issues import ISSUE, create_issue
from mongo_x_ray_hc.rules.base_rule import BaseRule

# The default value of diagnosticDataCollectionSamplesPerChunk.
DEFAULT_SAMPLES_PER_CHUNK = 300


class FtdcRule(BaseRule):
    def __init__(self, thresholds=None):
        super().__init__(thresholds)
        self._rule_desc.append("Checks the FTDC (Full-Time Diagnostics Data Capture) settings.")

    def apply(self, data: dict, **kwargs) -> tuple[list, dict]:
        """Check the FTDC configuration from the server parameters.

        - `diagnosticDataCollectionEnabled` is `true` by default; when it is
          explicitly set to `false`, FTDC is disabled (HIGH).
        - `diagnosticDataCollectionSamplesPerChunk` defaults to `300`; a value
          below it means the FTDC sample rate may be too small (MEDIUM).

        Args:
            data (dict): The `getParameter` output, e.g. from the
                `server_parameters` subsection of a getMongoData dump.
            extra_info (dict, optional): Extra information such as host. Defaults to None.

        Returns:
            tuple: (list of issues found, parsed data)
        """
        host = kwargs.get("extra_info", {}).get("host", "unknown")
        result = []
        enabled = data.get("diagnosticDataCollectionEnabled", True)
        if enabled is False:
            result.append(create_issue(ISSUE.FTDC_DISABLED, host=host))
        samples = data.get("diagnosticDataCollectionSamplesPerChunk", DEFAULT_SAMPLES_PER_CHUNK)
        if isinstance(samples, dict):
            samples = samples.get("value", samples)
        try:
            too_small = int(samples) < DEFAULT_SAMPLES_PER_CHUNK
        except (TypeError, ValueError):
            too_small = False
        if too_small:
            result.append(create_issue(ISSUE.FTDC_SAMPLES_TOO_SMALL, host=host, params={"value": samples}))
        return result, data
