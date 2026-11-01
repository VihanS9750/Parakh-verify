"""For lists you download by hand (RBI blocks scripts): PDF -> CSV -> searchable,
always carrying the download date so we can say 'from the list downloaded on ...'."""
import csv
import os
from datetime import datetime

from base import result
from matching import best_matches, find_by_id


def pdf_to_csv(pdf_path, csv_path, name_col=1, id_col=None):
    """Rough PDF table extractor. Open the CSV afterwards and check the columns."""
    import pdfplumber
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    cells = [(c or "").strip() for c in row]
                    if not cells[0].isdigit():  # skip header rows like "Sr. No | Name | ..."
                        continue
                    if len(cells) > name_col and cells[name_col]:
                        rows.append({"name": cells[name_col],
                                     "id": cells[id_col] if id_col is not None and len(cells) > id_col else ""})
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "id"])
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{"name": r["name"], "id": r.get("id", "")} for r in csv.DictReader(f)]


def search_list(source, query, csv_path, source_url, downloaded_on=None, common=None):
    """downloaded_on: 'YYYY-MM-DD' you saved the file; defaults to the file's date.
    common: words too frequent in this list to count for 'did you mean' (see best_matches)."""
    if downloaded_on is None:
        downloaded_on = datetime.fromtimestamp(os.path.getmtime(csv_path)).strftime("%Y-%m-%d")
    records = load_csv(csv_path)
    matches = find_by_id(query, records) or best_matches(query, records, common=common)
    return result(source, query, "found" if matches else "not_found", matches,
                  source_url=source_url, data_as_of=downloaded_on,
                  note=f"From the list downloaded on {downloaded_on}")
