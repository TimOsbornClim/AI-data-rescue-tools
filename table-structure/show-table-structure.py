# -*- coding: utf-8 -*-
"""
This takes data-rescue table structures produced by the UoS
data rescue pipeline and encoded in json files and creates
leaf-column paths and tree structures of the table column headings.

The reason this is needed is because the tables have hiearchical
heading/columns structures, with each heading/column sometimes
having multiple subheadings, and some of those have sub-subheadings and
even sub-sub-subheadings.

There can also be more than one table in a json file, if the original
image contained multiple tables.
"""



from pathlib import Path
import json


def process_file(json_file):

    column_counter = 0
    tree_counter = 0

    paths = []
    tree_lines = []

    def extract_paths(node, table_name, path):
        nonlocal column_counter

        current_path = path + [node["header"]]

        subheaders = node.get("subheaders", [])

        if not subheaders:
            column_counter += 1

            depth = len(current_path)  # excludes table name

            node["_leaf_number"] = column_counter

            paths.append(
                f"{column_counter:03d} "
                f"[depth={depth}] "
                f"{table_name} || "
                + " || ".join(current_path)
            )

            return

        for child in subheaders:
            extract_paths(child, table_name, current_path)

    def assign_leaf_numbers(node):
        nonlocal tree_counter

        subheaders = node.get("subheaders", [])

        if not subheaders:
            tree_counter += 1
            node["_leaf_number"] = tree_counter
            return

        for child in subheaders:
            assign_leaf_numbers(child)

    def build_tree(node, prefix="", is_last=True):

        connector = "└── " if is_last else "├── "
        subheaders = node.get("subheaders", [])

        if not subheaders:
            return

        tree_lines.append(f"{prefix}{connector}{node['header']}")

        child_prefix = prefix + ("    " if is_last else "│   ")

        for i, child in enumerate(subheaders):

            child_is_last = (i == len(subheaders) - 1)

            if child.get("subheaders"):
                build_tree(
                    child,
                    child_prefix,
                    child_is_last,
                )
            else:
                child_connector = (
                    "└── " if child_is_last else "├── "
                )

                tree_lines.append(
                    f"{child_prefix}{child_connector}"
                    f"{child['header']} "
                    f"[{child['_leaf_number']:03d}]"
                )

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    #
    # Build .paths
    #
    for table_name, table in data["metadata"].items():

        for column in table["columns"]:
            extract_paths(
                column,
                table_name,
                [],
            )

    #
    # Build .tree
    #
    tree_counter = 0

    for table_name, table in data["metadata"].items():

        tree_lines.append(table_name)

        for column in table["columns"]:
            assign_leaf_numbers(column)

        ncols = len(table["columns"])

        for i, column in enumerate(table["columns"]):

            is_last = (i == ncols - 1)

            if column.get("subheaders"):

                build_tree(
                    column,
                    "",
                    is_last,
                )

            else:
                connector = (
                    "└── " if is_last else "├── "
                )

                tree_lines.append(
                    f"{connector}"
                    f"{column['header']} "
                    f"[{column['_leaf_number']:03d}]"
                )

        tree_lines.append("")

    #
    # Write output files
    #
    json_file.with_suffix(".paths.txt").write_text(
        "\n".join(paths),
        encoding="utf-8",
    )

    json_file.with_suffix(".tree.txt").write_text(
        "\n".join(tree_lines),
        encoding="utf-8",
    )

    print(f"Processed {json_file.name}")


# --------------------------------------------------
# Process all matching JSON files
# --------------------------------------------------

for json_file in sorted(Path(".").glob("results_*.json")):
    process_file(json_file)

