#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This tries to create a JSON schema file to describe a Table structure
(with hierarchical headings, subheadings etc) from a .paths.txt file.
The .paths.txt file could be created using 'show-table-structure.py' from
an existing JSON schema file (e.g. one produced using AI header extraction
for AI-based data rescue) but the .paths.txt file could then be manually
edited to correct any mistakes and then this script could create a new,
corrected JSON schema file.
"""


import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

SEPARATOR = " || "
SIMILARITY_THRESHOLD = 0.90

# ------------------------------------------------------------
# Similarity helper
# ------------------------------------------------------------

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


# ------------------------------------------------------------
# Main parser
# ------------------------------------------------------------

def paths_to_schema(paths_file):

    # Create regular expression to parse each input line
    # ^         start of line
    # (\d+)     one or more digits, store as capture group 1
    # \s+       one or more whitespace characters
    # [depth=   [depth=
    # (\d+)     one or more digits, store as capture group 2
    # ]         ]
    # \s+       one or more whitespace characters
    # (.*)      capture everything else till the end of the line, as capture group 3
    # $         end of line
    
    line_re = re.compile(
        r'^(\d+)\s+\[depth=(\d+)\]\s+(.*)$'
    )

    metadata = {}

    #
    # State from immediately previous path
    #
    previous_table = None
    previous_headers = []
    previous_nodes = []
    previous_lineno = None

    #
    # Duplicate full-path detection
    #
    seen_paths = {}

    with open(paths_file, encoding="utf-8") as f:

        for lineno, raw in enumerate(f, start=1):

            line = raw.strip()

            if not line:
                continue

            m = line_re.match(line)

            if not m:
                raise ValueError(
                    f"Cannot parse line {lineno}:\n{line}"
                )

            colno = int(m.group(1))
            recorded_depth = int(m.group(2))
            remainder = m.group(3)

            parts = [
                p.strip()
                for p in remainder.split(SEPARATOR)
            ]

            if len(parts) < 2:
                raise ValueError(
                    f"Line {lineno}: "
                    f"must contain table name and at least one heading."
                )

            table_name = parts[0]
            headers = parts[1:]

            # ----------------------------------------------------
            # Depth validation
            # ----------------------------------------------------

            actual_depth = len(headers)

            if actual_depth != recorded_depth:

                print("\nERROR: Depth mismatch")
                print(f"Line            : {lineno}")
                print(f"Column number   : {colno}")
                print(f"Recorded depth  : {recorded_depth}")
                print(f"Actual depth    : {actual_depth}")
                print(f"Path            : {remainder}")

            # ----------------------------------------------------
            # Duplicate-path warning
            # ----------------------------------------------------

            path_key = tuple(parts)

            if path_key in seen_paths:

                print("\nWARNING: Duplicate path")

                print(
                    f"First occurrence : "
                    f"line {seen_paths[path_key]}"
                )

                print(
                    f"Current line     : "
                    f"{lineno}"
                )

                print(
                    f"Path             : "
                    f"{remainder}"
                )

            else:

                seen_paths[path_key] = lineno

            # ----------------------------------------------------
            # Similarity warnings
            # Only compare against previous line
            # ----------------------------------------------------

            if previous_table == table_name:

                max_depth = min(
                    len(previous_headers),
                    len(headers)
                )

                for level in range(max_depth):

                    previous_header = previous_headers[level]
                    current_header = headers[level]

                    if previous_header == current_header:
                        continue

                    score = similarity(
                        previous_header,
                        current_header
                    )

                    if score >= SIMILARITY_THRESHOLD:

                        print(
                            "\nWARNING: Similar headings in adjacent paths"
                        )

                        print(
                            f"Previous line : {previous_lineno}"
                        )

                        print(
                            f"Current line  : {lineno}"
                        )

                        print(
                            f"Depth         : {level + 1}"
                        )

                        print(
                            f"\n    '{previous_header}'"
                        )

                        print(
                            f"    '{current_header}'"
                        )

                        print(
                            f"\nSimilarity: {score:.3f}"
                        )

            # ----------------------------------------------------
            # Create table if required
            # ----------------------------------------------------

            if table_name not in metadata:

                metadata[table_name] = {
                    "columns": []
                }

            columns = metadata[table_name]["columns"]

            # ----------------------------------------------------
            # Longest common prefix with previous path
            # ----------------------------------------------------

            if table_name != previous_table:

                common_prefix = 0

            else:

                common_prefix = 0

                while (
                    common_prefix < len(headers)
                    and common_prefix < len(previous_headers)
                    and headers[common_prefix]
                    == previous_headers[common_prefix]
                ):

                    common_prefix += 1

            # ----------------------------------------------------
            # Determine parent for new nodes
            # ----------------------------------------------------

            if common_prefix == 0:

                parent_children = columns

            else:

                parent_node = previous_nodes[
                    common_prefix - 1
                ]

                parent_children = parent_node[
                    "subheaders"
                ]

            # ----------------------------------------------------
            # Reuse common-prefix nodes and create new
            # nodes after divergence
            # ----------------------------------------------------

            current_nodes = previous_nodes[
                :common_prefix
            ]

            for header in headers[common_prefix:]:

                node = {
                    "header": header,
                    "subheaders": []
                }

                parent_children.append(node)

                current_nodes.append(node)

                parent_children = node["subheaders"]

            # ----------------------------------------------------
            # Save current path as previous path
            # ----------------------------------------------------

            previous_table = table_name
            previous_headers = headers
            previous_nodes = current_nodes
            previous_lineno = lineno

    return {
        "metadata": metadata
    }


# ------------------------------------------------------------
# Driver
# ------------------------------------------------------------

def process_file(paths_file):

    schema = paths_to_schema(paths_file)

    output_json = paths_file.with_suffix(
        ".json"
    )

    with open(
        output_json,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            schema,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nCreated {output_json}")


# ------------------------------------------------------------
# Process one file
# ------------------------------------------------------------

#fn="results_CORFU_1852_09.paths.txt"
fn="table_CORFU_185209-185508.paths.txt"

process_file(
    Path(fn)
)

# ------------------------------------------------------------
# Or process all .paths files
# ------------------------------------------------------------
#
# for p in sorted(Path(".").glob("*.paths.txt")):
#     process_file(p)
#
