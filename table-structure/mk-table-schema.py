#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This tries to create a JSON schema file to describe a Table structure
(with hierarchical headings, subheadings etc) from a .paths.txt file.
The .paths.txt file could be created using 'cmp-table-structure.py' from
an existing JSON schema file (e.g. one produced using AI header extraction
for AI-based data rescue) but the .paths.txt file could then be manually
edited to correct any mistakes and then this script could create a new,
corrected JSON schema file.
"""


import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

SEPARATOR = " || "
SIMILARITY_THRESHOLD = 0.90

# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_or_create_child(children, header):
    """
    Return existing child if header matches exactly.
    Otherwise create a new child.

    No normalisation is performed.
    """

    for child in children:
        if child["header"] == header:
            return child

    child = {
        "header": header,
        "subheaders": []
    }

    children.append(child)

    return child


# ------------------------------------------------------------------
# Warning collection
# ------------------------------------------------------------------

warning_keys = set()
warnings = []


def check_for_near_duplicate(children, new_header, location):
    """
    Compare a new sibling heading against existing siblings.

    Warn if very similar but not identical.
    """

    for child in children:

        existing = child["header"]

        if existing == new_header:
            continue

        score = similarity(existing, new_header)

        if score >= SIMILARITY_THRESHOLD:

            key = tuple(sorted([existing, new_header])) + (location,)

            if key not in warning_keys:

                warning_keys.add(key)

                warnings.append(
                    {
                        "location": location,
                        "existing": existing,
                        "new": new_header,
                        "score": score,
                    }
                )


# ------------------------------------------------------------------
# Main reconstruction
# ------------------------------------------------------------------


def paths_to_schema(paths_file):

    metadata = {}

    line_re = re.compile(
        r'^(\d+)\s+\[depth=(\d+)\]\s+(.*)$'
    )

    with open(paths_file, encoding="utf-8") as f:

        for lineno, raw in enumerate(f, start=1):

            line = raw.strip()

            if not line:
                continue

            m = line_re.match(line)

            if not m:
                raise ValueError(
                    f"Line {lineno}: "
                    f"Cannot parse:\n{line}"
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
                    "Path must contain table name "
                    "and at least one column heading."
                )

            table_name = parts[0]
            headers = parts[1:]

            actual_depth = len(headers)

            if actual_depth != recorded_depth:

                print(
                    f"\nERROR: Depth mismatch"
                )
                print(
                    f"Line {lineno}"
                )
                print(
                    f"Recorded depth = {recorded_depth}"
                )
                print(
                    f"Actual depth   = {actual_depth}"
                )
                print(
                    f"Column number  = {colno}"
                )
                print(
                    f"Path           = {remainder}\n"
                )

            if table_name not in metadata:

                metadata[table_name] = {
                    "columns": []
                }

            columns = metadata[table_name]["columns"]

            # ----------------------------------------------------------
            # Top level
            # ----------------------------------------------------------

            top_header = headers[0]

            check_for_near_duplicate(
                columns,
                top_header,
                f"{table_name}"
            )

            current = get_or_create_child(
                columns,
                top_header
            )

            # ----------------------------------------------------------
            # Remaining levels
            # ----------------------------------------------------------

            parent_path = [top_header]

            for header in headers[1:]:

                location = (
                    f"{table_name}"
                    f"{SEPARATOR}"
                    f"{SEPARATOR.join(parent_path)}"
                )

                check_for_near_duplicate(
                    current["subheaders"],
                    header,
                    location
                )

                current = get_or_create_child(
                    current["subheaders"],
                    header
                )

                parent_path.append(header)

    return {
        "metadata": metadata
    }


# ------------------------------------------------------------------
# Driver
# ------------------------------------------------------------------


def process_file(paths_file):

    global warnings
    global warning_keys

    warnings = []
    warning_keys = set()

    schema = paths_to_schema(paths_file)

    output_json = paths_file.with_suffix(".json")

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

    print(
        f"\nCreated: {output_json}"
    )

    # --------------------------------------------------------------
    # Warning report
    # --------------------------------------------------------------

    if warnings:

        print(
            "\nPossible near-duplicate headings:"
        )

        for w in sorted(
            warnings,
            key=lambda x: -x["score"]
        ):

            print("\n--------------------------------")

            print(
                f"Parent location:\n"
                f"    {w['location']}"
            )

            print(
                f"\n    '{w['existing']}'"
            )

            print(
                f"    '{w['new']}'"
            )

            print(
                f"\nSimilarity: "
                f"{w['score']:.3f}"
            )

    else:

        print(
            "\nNo near-duplicate headings found."
        )


# ------------------------------------------------------------------
# Either process one file...
# ------------------------------------------------------------------

process_file(
    Path("results_CORFU_1852_09.paths.txt")
)

# ------------------------------------------------------------------
# ...or process all .paths files:
#
# for p in sorted(Path('.').glob('*.paths')):
#     process_file(p)
# ------------------------------------------------------------------