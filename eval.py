"""Run every test forward through Parakh and report how it did.

Owner: Rahul (Day 2 task, scaffolded here). Run:  python eval.py
This is a regression gate, not a benchmark: 23 forwards is too few to claim an accuracy figure, so we
report counts with Wilson 95% intervals and keep "couldn't decide" separate from right and wrong.
"""
import json
import math
from pathlib import Path

import agent

HERE = Path(__file__).parent


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes out of n."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def main():
    forwards = json.loads((HERE / "test_forwards" / "forwards.json").read_text(encoding="utf-8"))
    rows = []
    for f in forwards:
        rep = agent.run_check(f["text"], on_step=lambda s: None)
        rows.append({**f, "headline": rep["headline"], "ms": rep["duration_ms"], "mode": rep["mode"],
                     "items": rep["items"], "flags": [x["code"] for x in rep["flags"]]})
        print(f"{f['id']:9} scam={f['scam']!s:5} -> {rep['headline']:10} {rep['duration_ms']:>6} ms  {rep['items']}")

    scams = [r for r in rows if r["scam"]]
    genuine = [r for r in rows if not r["scam"]]
    high = sum(r["headline"] == "HIGH_RISK" for r in scams)
    caution = sum(r["headline"] == "CAUTION" for r in scams)
    missed = sum(r["headline"] == "CONSISTENT" for r in scams)
    false_alarms = sum(r["headline"] == "HIGH_RISK" for r in genuine)
    confirmed = sum(r["headline"] == "CONSISTENT" for r in genuine)
    times = sorted(r["ms"] for r in rows)

    lo, hi = wilson(high, len(scams))
    flo, fhi = wilson(false_alarms, len(genuine))
    lines = [
        f"# Parakh evaluation ({rows[0]['mode']} mode)",
        "",
        f"{len(rows)} forwards: {len(scams)} scam examples from official advisories and news (some partial or rebuilt from descriptions; see test_forwards), {len(genuine)} genuine messages.",
        "A regression gate, not a benchmark: too few forwards to claim an accuracy figure.",
        "The warning-sign rules were written from the same SEBI, RBI, I4C and PIB advisories these examples come from,",
        "so expect lower numbers on messages the team has never seen. Add fresh forwards before quoting results.",
        "",
        "| Measure | Result |",
        "|---|---|",
        f"| Scams rated **High risk** | {high} of {len(scams)} (95% range {lo:.0%} to {hi:.0%}) |",
        f"| Scams rated **Be careful** (not confirmed, not condemned) | {caution} of {len(scams)} |",
        f"| Scams wrongly rated **Consistent** (the dangerous error) | {missed} of {len(scams)} |",
        f"| Genuine messages wrongly rated **High risk** | {false_alarms} of {len(genuine)} (95% range {flo:.0%} to {fhi:.0%}) |",
        f"| Genuine messages rated **Consistent** | {confirmed} of {len(genuine)} |",
        f"| Median time per check | {times[len(times) // 2] / 1000:.1f} s |",
        "",
        "| ID | Real scam? | Result | Items checked | Warning signs |",
        "|---|---|---|---|---|",
    ] + [f"| {r['id']} | {'yes' if r['scam'] else 'no'} | {r['headline']} | "
         f"{'; '.join(f'{k}: {v}' for k, v in r['items'].items()) or '-'} | {', '.join(r['flags']) or '-'} |"
         for r in rows]
    out = HERE / "docs" / f"eval-results-{rows[0]['mode'].split()[0].lower()}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:13]))
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
