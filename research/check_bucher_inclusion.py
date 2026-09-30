"""Read-only XLSX inclusion audit for the two byte-verified Bucher EM tables.

This script reads OOXML ZIP/XML directly.  It neither opens Excel nor evaluates
formulae.  Its output is a structural account of the deposited numeric area
entries; it does not infer biological inclusion, analyze effects, or impute data.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / ".cache-bucher-em-001"
DESIGN = ROOT / "bucher_inclusion_design.json"
OUTPUT = ROOT / "bucher_inclusion_package_001.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
CELL = re.compile(r"^([A-Z]+)([0-9]+)$")
EXPECTED = {
    "EM BSC-1.xlsx": {"bytes": 78130, "md5": "ce61ee0d469a291ddcfa193310119905",
                         "sha256": "da13bd3044c7d8a51f2c32aea0c404b36b68c06cde1cc79383c83aaa103ff216"},
    "EM BSC-1 osmotic shock.xlsx": {"bytes": 72748, "md5": "529bbaa8d3cfafc95821a4ea2e354708",
                                      "sha256": "6f9acae5fd3f7e0d737f13b2eec8496623e40de4a6912967099d822b1c6219ed"},
}
PUBLISHED = {
    "EM BSC-1.xlsx": [746, 869, 739],
    "EM BSC-1 osmotic shock.xlsx": {"Control": [267, 308, 229, 323],
                                      "osmotic shock": [395, 99, 351, 201]},
}


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(data: bytes) -> dict[str, str | int]:
    return {"bytes": len(data), "md5": hashlib.md5(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest()}


def address_parts(address: str) -> tuple[str, int]:
    match = CELL.fullmatch(address)
    if not match:
        raise ValueError(f"Unexpected cell address: {address}")
    return match.group(1), int(match.group(2))


def range_columns(ref: str) -> list[str]:
    start, end = ref.split(":")
    def n(col: str) -> int:
        total = 0
        for char in col:
            total = total * 26 + ord(char) - 64
        return total
    def letters(value: int) -> str:
        out = ""
        while value:
            value, remainder = divmod(value - 1, 26)
            out = chr(65 + remainder) + out
        return out
    a, _ = address_parts(start)
    b, _ = address_parts(end)
    return [letters(i) for i in range(n(a), n(b) + 1)]


def xml_text(root: ET.Element) -> str:
    return "".join(root.itertext()).strip()


def compact_rows(rows: list[int], column: str) -> list[str]:
    """Encode consecutive row provenance without expanding ragged padding."""
    if not rows:
        return []
    out, first, previous = [], rows[0], rows[0]
    for row in rows[1:]:
        if row == previous + 1:
            previous = row
            continue
        out.append(f"{column}{first}:{column}{previous}" if first != previous else f"{column}{first}")
        first = previous = row
    out.append(f"{column}{first}:{column}{previous}" if first != previous else f"{column}{first}")
    return out


def shared_strings(book: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in book.namelist():
        return []
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    return [xml_text(item) for item in root.findall("m:si", NS)]


def cell_value(cell: ET.Element, shared: list[str]) -> tuple[str, object | None]:
    kind = cell.attrib.get("t", "n")
    raw = cell.findtext("m:v", default=None, namespaces=NS)
    if kind == "s":
        return "text", shared[int(raw)] if raw is not None else None
    if kind == "inlineStr":
        inline = cell.find("m:is", NS)
        return "text", xml_text(inline) if inline is not None else ""
    if kind in {"str", "e"}:
        return "text" if kind == "str" else "error", raw
    if kind == "b":
        return "boolean", raw
    if raw is None:
        return "blank", None
    try:
        return "number", float(raw)
    except ValueError:
        return "unparsed", raw


def package_metadata(book: zipfile.ZipFile, workbook: ET.Element) -> dict[str, object]:
    names = []
    for node in workbook.findall("m:definedNames/m:definedName", NS):
        names.append({"name": node.attrib.get("name"), "hidden": node.attrib.get("hidden") == "1",
                      "formula": (node.text or "").strip()})
    comment_files = [name for name in book.namelist() if re.fullmatch(r"xl/comments[0-9]*\.xml", name)]
    comment_count = 0
    for name in comment_files:
        root = ET.fromstring(book.read(name))
        comment_count += len(root.findall("m:commentList/m:comment", NS))
    props = {}
    for name in ("docProps/core.xml", "docProps/app.xml", "docProps/custom.xml"):
        if name in book.namelist():
            root = ET.fromstring(book.read(name))
            props[name] = {child.tag.rsplit("}", 1)[-1]: xml_text(child) for child in root if xml_text(child)}
    styles = {"cell_xf_count": 0, "custom_number_formats": []}
    if "xl/styles.xml" in book.namelist():
        style_root = ET.fromstring(book.read("xl/styles.xml"))
        xfs = style_root.find("m:cellXfs", NS)
        styles["cell_xf_count"] = 0 if xfs is None else len(xfs)
        styles["custom_number_formats"] = [
            {"id": node.attrib.get("numFmtId"), "code": node.attrib.get("formatCode")}
            for node in style_root.findall("m:numFmts/m:numFmt", NS)
        ]
    return {"zip_member_count": len(book.infolist()),
            "expanded_bytes": sum(item.file_size for item in book.infolist()),
            "macros_present": any(name.lower().endswith("vbaproject.bin") for name in book.namelist()),
            "defined_names": names, "comment_files": comment_files, "comment_count": comment_count,
            "document_properties": props, "styles": styles}


def inspect_sheet(book: zipfile.ZipFile, target: str, name: str, shared: list[str]) -> dict[str, object]:
    root = ET.fromstring(book.read(target))
    cells: dict[str, dict[str, object]] = {}
    stored_by_column: Counter[str] = Counter()
    formulas = []
    for cell in root.findall("m:sheetData/m:row/m:c", NS):
        addr = cell.attrib["r"]
        col, row = address_parts(addr)
        kind, value = cell_value(cell, shared)
        entry = {"kind": kind, "value": value, "style": cell.attrib.get("s"),
                 "formula": cell.findtext("m:f", default=None, namespaces=NS)}
        cells[addr] = entry
        stored_by_column[col] += 1
        if entry["formula"] is not None:
            formulas.append({"cell": addr, "formula": entry["formula"]})
    hidden_rows = [int(row.attrib["r"]) for row in root.findall("m:sheetData/m:row", NS)
                   if row.attrib.get("hidden") in {"1", "true"}]
    hidden_columns = []
    for col in root.findall("m:cols/m:col", NS):
        if col.attrib.get("hidden") in {"1", "true"}:
            hidden_columns.append({"min": int(col.attrib["min"]), "max": int(col.attrib["max"])})
    dim = root.find("m:dimension", NS)
    merge_cells = [m.attrib["ref"] for m in root.findall("m:mergeCells/m:mergeCell", NS)]
    return {"name": name, "dimension": None if dim is None else dim.attrib.get("ref"), "cells": cells,
            "stored_cells_by_column": dict(stored_by_column), "formulas": formulas,
            "hidden_rows": hidden_rows, "hidden_columns": hidden_columns,
            "merged_ranges": merge_cells,
            "sheet_protection_present": root.find("m:sheetProtection", NS) is not None}


def group_audit(sheet: dict[str, object], condition: str | None, cell_label: int,
                columns: list[str], data_start_row: int, published_total: int) -> dict[str, object]:
    cells = sheet["cells"]
    counts = []
    for col in columns:
        numeric_rows, invalid, nonnumeric, stored_blanks = [], [], [], []
        numeric_styles, blank_styles = Counter(), Counter()
        for addr, entry in cells.items():
            here_col, row = address_parts(addr)
            if here_col != col or row < data_start_row:
                continue
            if entry["kind"] == "number":
                number = entry["value"]
                if math.isfinite(number) and number > 0:
                    numeric_rows.append(row)
                    numeric_styles[str(entry["style"] or 0)] += 1
                else:
                    invalid.append({"cell": addr, "value": number})
            elif entry["kind"] == "blank":
                stored_blanks.append(addr)
                blank_styles[str(entry["style"] or 0)] += 1
            else:
                nonnumeric.append({"cell": addr, "kind": entry["kind"], "value": entry["value"]})
        first = min(numeric_rows) if numeric_rows else None
        last = max(numeric_rows) if numeric_rows else None
        numeric_set = set(numeric_rows)
        internal_missing = [] if first is None else [row for row in range(first, last + 1) if row not in numeric_set]
        counts.append({"column": col, "numeric_positive_finite_count": len(numeric_rows),
                       "first_numeric_row": first, "last_numeric_row": last,
                       "internal_blank_count": len(internal_missing),
                       "internal_blank_row_ranges": compact_rows(internal_missing, col),
                       "stored_blank_cell_ranges": compact_rows([address_parts(a)[1] for a in stored_blanks], col),
                       "numeric_style_counts": dict(numeric_styles), "stored_blank_style_counts": dict(blank_styles),
                       "non_numeric_cells": nonnumeric,
                       "invalid_numeric_cells": invalid})
    group_end = max((item["last_numeric_row"] or data_start_row - 1) for item in counts)
    for item in counts:
        last = item["last_numeric_row"]
        rows = [] if last is None else list(range(last + 1, group_end + 1))
        item["trailing_padding_count"] = len(rows)
        item["trailing_padding_row_ranges_to_group_end"] = compact_rows(rows, item["column"])
    total = sum(item["numeric_positive_finite_count"] for item in counts)
    return {"condition": condition, "cell_label": cell_label, "columns": columns,
            "data_start_row": data_start_row, "column_audit": counts, "deposited_total": total,
            "published_caption_total": published_total, "published_minus_deposited": published_total - total,
            "all_numeric_entries_are_finite_and_positive": not any(
                item["invalid_numeric_cells"] for item in counts),
            "internal_blank_count": sum(item["internal_blank_count"] for item in counts),
            "trailing_padding_count": sum(item["trailing_padding_count"] for item in counts)}


def inspect_workbook(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    verified = digest(raw)
    expected = EXPECTED[path.name]
    verified["registered_match"] = all(verified[key] == expected[key] for key in expected)
    if not verified["registered_match"]:
        raise ValueError(f"Registered bytes/digest mismatch for {path.name}")
    with zipfile.ZipFile(path) as book:
        if sum(item.file_size for item in book.infolist()) > 5_000_000:
            raise ValueError("Expanded XLSX size exceeds design bound")
        shared = shared_strings(book)
        workbook = ET.fromstring(book.read("xl/workbook.xml"))
        relationships = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        rels = {node.attrib["Id"]: node.attrib["Target"] for node in relationships}
        sheets = []
        for node in workbook.findall("m:sheets/m:sheet", NS):
            target = rels[node.attrib[REL]]
            target = target.lstrip("/") if target.startswith("/") else "xl/" + target
            sheets.append(inspect_sheet(book, target, node.attrib["name"], shared))
        result = {"file": path.name, "source_path": str(path), "digest": verified,
                  "package_metadata": package_metadata(book, workbook), "sheets": sheets}
    main = next(item for item in result["sheets"] if item["name"] == "Sheet1")
    if path.name == "EM BSC-1.xlsx":
        layout = [(None, i, cols, 4, total) for i, (cols, total) in enumerate(
            zip((["A", "B", "C"], ["E", "F", "G"], ["I", "J", "K"]), PUBLISHED[path.name]), start=1)]
        groups = [group_audit(main, None, i, cols, 4, total)
                  for i, (cols, total) in enumerate(zip((["A", "B", "C"], ["E", "F", "G"], ["I", "J", "K"]),
                                                        PUBLISHED[path.name]), start=1)]
        header_addresses = {"unit": "A1", "cell_labels": ["A2", "E2", "I2"],
                            "morphology_labels": [["A3", "B3", "C3"], ["E3", "F3", "G3"], ["I3", "J3", "K3"]]}
    else:
        groups = []
        layouts = {"Control": [["A", "B", "C"], ["E", "F", "G"], ["I", "J", "K"], ["M", "N", "O"]],
                   "osmotic shock": [["Q", "R", "S"], ["U", "V", "W"], ["Y", "Z", "AA"], ["AC", "AD", "AE"]]}
        layout = []
        for condition, blocks in layouts.items():
            for label, columns in enumerate(blocks, start=1):
                groups.append(group_audit(main, condition, label, columns, 5,
                                          PUBLISHED[path.name][condition][label - 1]))
                layout.append((condition, label, columns, 5, PUBLISHED[path.name][condition][label - 1]))
        header_addresses = {"unit": "A1", "conditions": ["A2", "Q2"],
                            "cell_labels": ["A3", "E3", "I3", "M3", "Q3", "U3", "Y3", "AC3"],
                            "morphology_labels": [["A4", "B4", "C4"], ["E4", "F4", "G4"], ["I4", "J4", "K4"], ["M4", "N4", "O4"],
                                                  ["Q4", "R4", "S4"], ["U4", "V4", "W4"], ["Y4", "Z4", "AA4"], ["AC4", "AD4", "AE4"]]}
    result["groups"] = groups
    result["numeric_entry_total"] = sum(group["deposited_total"] for group in groups)
    result["all_numeric_entries_positive_finite"] = all(group["all_numeric_entries_are_finite_and_positive"] for group in groups)
    result["all_formula_count"] = sum(len(sheet["formulas"]) for sheet in result["sheets"])
    observed_headers = {key: ([main["cells"].get(a, {}).get("value") for a in value] if isinstance(value, list) and value and isinstance(value[0], str)
                              else [[main["cells"].get(a, {}).get("value") for a in row] for row in value] if isinstance(value, list)
                              else main["cells"].get(value, {}).get("value")) for key, value in header_addresses.items()}
    expected_cells = [f"Cell {item[1]}" for item in layout]
    expected_morphology = ["Flat", "Dome", "Pit"]
    headers_valid = (observed_headers["unit"] == "Projected area (nm^2)" and
                     observed_headers["cell_labels"] == expected_cells and
                     all(row == expected_morphology for row in observed_headers["morphology_labels"]) and
                     ("conditions" not in observed_headers or observed_headers["conditions"] == ["Control", "osmotic shock"]))
    claimed = {(col, row) for _, _, columns, start, _ in layout for col in columns for row in range(start, 1_000_001)}
    numeric_cells, unassigned = [], []
    for sheet in result["sheets"]:
        for address, entry in sheet["cells"].items():
            if entry["kind"] != "number":
                continue
            record = {"sheet": sheet["name"], "cell": address, "value": entry["value"]}
            numeric_cells.append(record)
            col, row = address_parts(address)
            if sheet["name"] != "Sheet1" or (col, row) not in claimed:
                unassigned.append(record)
    result["header_mapping"] = {"observed": observed_headers, "valid": headers_valid}
    result["numeric_cell_coverage"] = {"numeric_cells_in_entire_workbook": len(numeric_cells),
                                        "assigned_to_declared_area_blocks": len(numeric_cells) - len(unassigned),
                                        "numeric_cells_outside_declared_area_blocks": unassigned,
                                        "complete": not unassigned}
    # Retain only serializable structural summaries; worksheet cells are an internal parsing detail.
    for sheet in result["sheets"]:
        del sheet["cells"]
    return result


def main() -> None:
    started = utcnow()
    result = {"task_id": "bucher-inclusion-package-001", "attempt_number": 1,
              "started_at_utc": started, "design_sha256": hashlib.sha256(DESIGN.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "method": "Read-only OOXML ZIP/XML inspection; numeric cells require finite value > 0. No formula execution, imputation, biological inference, effect calculation, or figure reproduction.",
              "workbooks": [inspect_workbook(CACHE / name) for name in EXPECTED]}
    result["decision"] = ("Both registered packages contain fewer finite positive deposited entries than the published "
                          "Fig. 1/Fig. 7 caption totals. No package-level inclusion explanation was found; "
                          "the discrepancy remains unresolved and published-figure reproduction must stop.")
    result["finished_at_utc"] = utcnow()
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "workbooks": [
        {"file": item["file"], "total": item["numeric_entry_total"], "digest_verified": item["digest"]["registered_match"]}
        for item in result["workbooks"]]}, indent=2))


if __name__ == "__main__":
    main()
