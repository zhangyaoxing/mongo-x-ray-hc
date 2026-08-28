"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray.utils import yellow
from mongo_x_ray.version import Version
from mongo_x_ray_hc.check_items.base_item import BaseItem
from mongo_x_ray_hc.rules.ftdc_rule import FtdcRule
from mongo_x_ray_hc.rules.sbe_rule import SbeRule
from mongo_x_ray_hc.rules.snapshot_window_rule import SnapshotWindowRule
from mongo_x_ray_hc.shared import MAX_MONGOS_PING_LATENCY, discover_nodes, enum_all_nodes, enum_result_items

# Parameters shown in the review table, in display order.
REVIEW_PARAMETERS = [
    "minSnapshotHistoryWindowInSeconds",
]


class ServerParametersItem(BaseItem):
    def __init__(self, output_folder, config=None):
        super().__init__(output_folder, config)
        self._name = "Server Parameters"
        self._rules["snapshot_window"] = SnapshotWindowRule(config)
        self._rules["sbe"] = SbeRule(config)
        self._rules["ftdc"] = FtdcRule(config)

    def test(self, *args, **kwargs):
        """Collect `getParameter: "*"` on every node and run parameter-level rules."""
        client = kwargs.get("client")
        parsed_uri = kwargs.get("parsed_uri")

        def func_member(set_name, node, **kwargs):
            host = node["host"]
            if "pingLatencySec" in node and node["pingLatencySec"] > MAX_MONGOS_PING_LATENCY:
                self._logger.warning(
                    yellow(
                        f"Skip {host} because it has been irresponsive for {node['pingLatencySec'] / 60:.2f} minutes."
                    )
                )
                return None, None
            server_parameters = node["client"].admin.command("getParameter", "*")
            test_result = []
            # Parameter rules that only apply to data-bearing nodes.
            if set_name != "mongos":
                result, _ = self._rules["snapshot_window"].apply(server_parameters, extra_info={"host": host})
                test_result.extend(result)
                version = node.get("version")
                if version is None:
                    # BuildInfoItem normally records the version on the node;
                    # fall back to fetching it here so the order of items does
                    # not matter.
                    try:
                        build_info = node["client"].admin.command("buildInfo")
                        version = Version(build_info.get("versionArray", None))
                    except Exception as exc:
                        self._logger.debug("Cannot read buildInfo on %s: %s", host, exc)
                        version = None
                result, _ = self._rules["sbe"].apply(server_parameters, extra_info={"host": host, "version": version})
                test_result.extend(result)
                result, _ = self._rules["ftdc"].apply(server_parameters, extra_info={"host": host})
                test_result.extend(result)
            self.append_test_results(test_result)
            return test_result, {"server_parameters": server_parameters}

        nodes = discover_nodes(client, parsed_uri)
        result = enum_all_nodes(
            nodes,
            func_mongos_member=func_member,
            func_rs_member=func_member,
            func_shard_member=func_member,
            func_config_member=func_member,
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
                    "server_parameters": node.get("rawResult"),
                }
            )

        enum_result_items(
            raw_result,
            func_rs_member=func_node,
            func_mongos_member=func_node,
            func_shard_member=func_node,
            func_config_member=func_node,
        )
        if not raw_results:
            return ""

        headers = "| Host | Set | " + " | ".join(REVIEW_PARAMETERS) + " |\n"
        separators = "|" + "---|" * (len(REVIEW_PARAMETERS) + 2) + "\n"
        output = headers + separators
        for r in raw_results:
            params = (r["server_parameters"] or {}).get("server_parameters") or {}
            cells = [f"`{r['host']}`", f"`{r['set_name']}`"]
            cells += [f"`{params.get(param, 'n/a')}`" for param in REVIEW_PARAMETERS]
            output += "| " + " | ".join(cells) + " |\n"
        return output
