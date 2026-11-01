"""Name matching that survives spelling differences ('did you mean')."""
import re

from rapidfuzz import fuzz, process

_NOISE = re.compile(r"\b(private|pvt|limited|ltd|llp|india|and|co|company|the)\b")


def normalize(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    s = _NOISE.sub(" ", s)
    return " ".join(s.split())


def core(s, common):
    """Name without its common words. 'Bajaj Finanse Ltd' -> 'bajaj' (typos of common words too)."""
    return " ".join(t for t in normalize(s).split()
                    if not any(fuzz.ratio(t, c) >= 80 for c in common))


def best_matches(query, records, limit=3, min_score=70, common=None):
    """records: list of {'name':..., 'id':...}. Returns top matches with 0-100 score.
    common: words found in thousands of names ('finance'). If given, a match must also
    be close on the remaining distinctive words, so 'Bajaj Finance' won't suggest 'Eba Finance'."""
    q = normalize(query)
    choices = [normalize(r["name"]) for r in records]
    hits = process.extract(q, choices, scorer=fuzz.token_sort_ratio,
                           limit=limit * 10 if common else limit, score_cutoff=min_score)
    q_core = core(query, common) if common else ""
    if q_core:
        hits = [h for h in hits if fuzz.token_sort_ratio(q_core, core(records[h[2]]["name"], common)) >= 75]
    return [{"name": records[i]["name"], "id": records[i].get("id", ""), "score": round(s)}
            for _, s, i in hits[:limit]]


def find_by_id(reg_id, records):
    reg_id = reg_id.strip().upper()
    return [{"name": r["name"], "id": r["id"], "score": 100}
            for r in records if r.get("id", "").upper() == reg_id]
