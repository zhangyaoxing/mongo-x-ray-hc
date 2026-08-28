"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

from mongo_x_ray_hc.parsers.query_targeting_parser import QueryTargetingParser  # type: ignore

QT_INFOS = [
    {
        "set_name": "shard02",
        "host": "localhost:30022",
        "query_targeting": {"scanned/returned": 0.9633964673334752, "scanned_obj/returned": 0.96451372632475},
    },
    {
        "set_name": "shard02",
        "host": "localhost:30023",
        "query_targeting": {"scanned/returned": 0.9612366104571004, "scanned_obj/returned": 0.9623501962032028},
    },
]


def test_query_targeting_parser():
    parser = QueryTargetingParser()
    result = parser.parse(QT_INFOS)
    assert len(result) == 1
    table = result[0]
    assert table["type"] == "table"
    assert table["caption"] == "Query Targeting"
    assert table["header"] == [
        {"text": "Component", "width": "120px"},
        {"text": "Host", "width": "*"},
        {"text": "Scanned / Returned", "width": "250px"},
        {"text": "Scanned Objects / Returned", "width": "250px"},
    ]
    assert len(table["rows"]) == 2
    assert table["rows"][0] == ["shard02", "localhost:30022", "0.96", "0.96"]
    assert table["rows"][1] == ["shard02", "localhost:30023", "0.96", "0.96"]


def test_query_targeting_parser_no_data():
    parser = QueryTargetingParser()
    result = parser.parse(
        [
            {
                "set_name": "shard02",
                "host": "localhost:30022",
                "query_targeting": None,
            }
        ]
    )
    assert len(result) == 1
    table = result[0]
    assert table["type"] == "table"
    assert table["caption"] == "Query Targeting"
    assert table["header"] == [
        {"text": "Component", "width": "120px"},
        {"text": "Host", "width": "*"},
        {"text": "Scanned / Returned", "width": "250px"},
        {"text": "Scanned Objects / Returned", "width": "250px"},
    ]
    assert len(table["rows"]) == 1
    assert table["rows"][0] == ["shard02", "localhost:30022", "N/A", "N/A"]
