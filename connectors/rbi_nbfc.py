"""RBI NBFC lists: companies registered with RBI, and companies whose registration (CoR)
RBI has cancelled. RBI blocks scripts, so both Excel files are downloaded by hand from
https://www.rbi.org.in/Scripts/BS_NBFCList.aspx and turned into CSVs (name, id=CIN)."""
import csv
import os
import re

from base import safe
from local_list import search_list

SOURCE_URL = "https://www.rbi.org.in/Scripts/BS_NBFCList.aspx"
LIST_DATE = "2026-09-30"      # "as on" date printed in both files
DOWNLOADED_ON = "2026-11-01"  # the day we saved them
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
REGISTERED = {"label": "RBI list of registered NBFCs and ARCs",
              "xlsx": os.path.join(DATA, "rbi_nbfc_registered_2026-09-30.xlsx"),
              "csv": os.path.join(DATA, "rbi_nbfc_registered.csv")}
CANCELLED = {"label": "RBI list of NBFCs whose registration was cancelled",
             "xlsx": os.path.join(DATA, "rbi_nbfc_cancelled_2026-09-30.xlsx"),
             "csv": os.path.join(DATA, "rbi_nbfc_cancelled.csv")}
# (sheet, name column, CIN column) — column numbers start at 0. "Record" sheet in the
# cancelled file lists firms RBI restored, so it is left out on purpose.
SHEETS = {"registered": [("List of NBFCs", 1, 5), ("ARCs", 1, 3)],
          "cancelled": [("Cancelled List", 1, None)]}
FORMERLY = re.compile(r"\(\s*formerly\s*:?\s*(.*?)\)\s*$", re.I)
# "Old A Limited and Old B Limited" -> two old names (only split after Limited/Ltd)
OLD_NAMES_SPLIT = re.compile(r"(?<=limited)\s+and\s+|(?<=ltd)\s+and\s+|(?<=ltd\.)\s+and\s+", re.I)
# Words in thousands of NBFC names; ignored when judging "did you mean"
COMMON = {"finance", "financial", "finserv", "fincorp", "finvest", "capital", "credit",
          "investment", "investments", "leasing", "holdings", "securities", "services",
          "trading", "enterprises", "ventures", "savings", "loans", "money", "fintech"}


def build(which):
    """Excel -> CSV. Rows with a number in the first column are data; the rest are headers."""
    import openpyxl
    cfg = REGISTERED if which == "registered" else CANCELLED
    wb = openpyxl.load_workbook(cfg["xlsx"], read_only=True)
    rows = []
    for sheet, name_col, id_col in SHEETS[which]:
        for r in wb[sheet].iter_rows(values_only=True):
            if not isinstance(r[0], (int, float)) or not r[name_col]:
                continue
            name = " ".join(str(r[name_col]).split())  # drop stray newlines/double spaces
            cin = str(r[id_col]).strip() if id_col is not None and r[id_col] else ""
            old = FORMERLY.search(name)
            if old:  # "New Ltd (Formerly: Old Ltd)": make both names searchable
                rows += [{"name": o.strip(), "id": cin} for o in OLD_NAMES_SPLIT.split(old.group(1))]
                name = name[:old.start()].strip()
            rows.append({"name": name, "id": cin})
    with open(cfg["csv"], "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "id"])
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def _search(cfg, query):
    def run():
        res = search_list(cfg["label"], query, cfg["csv"], SOURCE_URL, DOWNLOADED_ON, COMMON)
        res["note"] = f"From RBI's list as on {LIST_DATE}, downloaded {DOWNLOADED_ON}."
        return res

    return safe(cfg["label"], query, SOURCE_URL, run)


def search(query):
    """Is this company registered with RBI as an NBFC/ARC? Name or CIN."""
    return _search(REGISTERED, query)


def search_cancelled(query):
    """Did RBI cancel this company's registration? Name only (the file has no CIN)."""
    return _search(CANCELLED, query)


if __name__ == "__main__":
    import json, sys
    # python rbi_nbfc.py build                -> both Excel files to CSV (run once)
    # python rbi_nbfc.py "Bajaj Finance"      -> registered list
    # python rbi_nbfc.py cancelled "Agroha"   -> cancelled list
    if sys.argv[1] == "build":
        print(build("registered"), "registered rows,", build("cancelled"), "cancelled rows")
    elif sys.argv[1] == "cancelled":
        print(json.dumps(search_cancelled(sys.argv[2]), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(search(sys.argv[1]), indent=2, ensure_ascii=False))
