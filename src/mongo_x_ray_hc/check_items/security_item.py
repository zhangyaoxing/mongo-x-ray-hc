"""
Copyright (c) 2025 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.utils import yellow

from mongo_x_ray_hc.check_items.base_item import BaseItem
from mongo_x_ray_hc.parsers.base_parser import BaseParser
from mongo_x_ray_hc.parsers.security_parser import SecurityParser
from mongo_x_ray_hc.rules.security_rule import SecurityRule
from mongo_x_ray_hc.rules.tls_protocol_rule import TlsProtocolRule
from mongo_x_ray_hc.shared import MAX_MONGOS_PING_LATENCY, discover_nodes, enum_all_nodes, enum_result_items


class SecurityItem(BaseItem):
    """
    This module defines a checklist item for collecting and reviewing security-related information in MongoDB.
    """

    def __init__(self, output_folder, config=None):
        super().__init__(output_folder, config)
        self._name = "Authentication & Security"
        self._rules["security"] = SecurityRule(config)
        self._rules["tls_protocol"] = TlsProtocolRule(config)

    def test(self, *args, **kwargs):
        client = kwargs.get("client")
        parsed_uri = kwargs.get("parsed_uri")

        nodes = discover_nodes(client, parsed_uri)

        def func_node(name, node, **kwargs):
            client = node["client"]
            host = node["host"]
            if "pingLatencySec" in node and node["pingLatencySec"] > MAX_MONGOS_PING_LATENCY:
                self._logger.warning(
                    yellow(
                        f"Skip {host} because it has been irresponsive for {node['pingLatencySec'] / 60:.2f} minutes."
                    )
                )
                return None, None
            raw_result = client.admin.command("getCmdLineOpts")
            test_result, _ = self._rules["security"].apply(raw_result, extra_info={"host": host})
            self.append_test_results(test_result)
            test_result, _ = self._rules["tls_protocol"].apply(raw_result, extra_info={"host": host})
            self.append_test_results(test_result)

            return test_result, raw_result

        result = enum_all_nodes(
            nodes,
            func_rs_member=func_node,
            func_mongos_member=func_node,
            func_shard_member=func_node,
            func_config_member=func_node,
        )

        self.captured_sample = result

    @property
    def review_result_markdown(self) -> str:
        raw_result = self.captured_sample
        raw_results: list = []

        def func_node(set_name, node, **kwargs):
            raw_results.append(
                {
                    "set_name": set_name,
                    "host": node.get("host"),
                    "command_line_opts": node.get("rawResult"),
                }
            )

        enum_result_items(
            raw_result,
            func_rs_member=func_node,
            func_mongos_member=func_node,
            func_shard_member=func_node,
            func_config_member=func_node,
        )
        parser: BaseParser = SecurityParser()
        return parser.markdown(raw_results)
