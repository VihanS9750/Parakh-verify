"""Name matching that survives spelling differences ('did you mean')."""
import re

from rapidfuzz import fuzz, process

_NOISE = re.compile(r"\b(private|pvt|limited|ltd|llp|india|and|co|company|the)\b")


def normalize(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    s = _NOISE.sub(" ", s)
    return " ".join(s.split())


def best_matches(query, records, limit=3, min_score=70):
    """records: list of {'name':..., 'id':...}. Returns top matches with 0-100 score."""
    q = normalize(query)
    choices = [normalize(r["name"]) for r in records]
    hits = process.extract(q, choices, scorer=fuzz.token_sort_ratio,
                           limit=limit, score_cutoff=min_score)
    return [{"name": records[i]["name"], "id": records[i].get("id", ""), "score": round(s)}
            for _, s, i in hits]


def find_by_id(reg_id, records):
    reg_id = reg_id.strip().upper()
    return [{"name": r["name"], "id": r["id"], "score": 100}
            for r in records if r.get("id", "").upper() == reg_id]
