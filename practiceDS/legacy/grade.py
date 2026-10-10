#!/usr/bin/env python3
"""
Grader for the refund lab. Checks your findings against the sealed manifest.

    python grade.py --seed 1337 --catalog          # the vocabulary of possible defects
    python grade.py --seed 1337 --guess tz_mixed   # record a finding
    python grade.py --seed 1337 --score            # scoreboard
    python grade.py --seed 1337 --hint             # families still outstanding
    python grade.py --seed 1337 --reveal           # burn it down
"""

from __future__ import annotations

import argparse
import base64
import json
import zlib
from pathlib import Path

from generate import CATALOG


def load_manifest(d: Path) -> dict:
    txt = (d / ".manifest.b64").read_text().strip().splitlines()[-1]
    return json.loads(zlib.decompress(base64.b64decode(txt)))


def load_attempts(d: Path) -> list:
    p = d / ".attempts.json"
    return json.loads(p.read_text()) if p.exists() else []


def save_attempts(d: Path, a: list):
    (d / ".attempts.json").write_text(json.dumps(a, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--data", default="data")
    ap.add_argument("--guess", action="append", default=[])
    ap.add_argument("--catalog", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--hint", action="store_true")
    ap.add_argument("--reveal", action="store_true")
    args = ap.parse_args()

    d = Path(args.data) / f"seed_{args.seed}"

    if args.catalog:
        fam = {}
        for k, (f, desc) in CATALOG.items():
            fam.setdefault(f, []).append((k, desc))
        print("Possible defects (not all are present in any given seed):\n")
        for f in sorted(fam):
            print(f"  [{f}]")
            for k, desc in sorted(fam[f]):
                print(f"    {k:<26} {desc}")
            print()
        return

    man = load_manifest(d)
    planted = {e["id"] for e in man["defects"]}
    attempts = load_attempts(d)

    for g in args.guess:
        g = g.strip()
        if g not in CATALOG:
            print(f"?? '{g}' is not in the catalog. Run --catalog for valid ids.")
            continue
        already = any(a["id"] == g for a in attempts)
        hit = g in planted
        attempts.append({"id": g, "hit": hit})
        if already:
            print(f"(already guessed) {g}")
        print(f"{'HIT ' if hit else 'MISS'}  {g}")
        if hit:
            e = next(e for e in man["defects"] if e["id"] == g)
            print(f"      {e['description']}")
            print(f"      params: {json.dumps(e['params'])}")
    if args.guess:
        save_attempts(d, attempts)
        found = {a["id"] for a in attempts if a["hit"]}
        print(f"\n  {len(found)}/{man['n_planted']} found, "
              f"{len([a for a in attempts if not a['hit']])} false positives")
        return

    if args.hint:
        found = {a["id"] for a in attempts if a["hit"]}
        rem = [e for e in man["defects"] if e["id"] not in found]
        fam = {}
        for e in rem:
            fam[e["family"]] = fam.get(e["family"], 0) + 1
        print(f"{len(rem)} defect(s) still hiding:")
        for f, n in sorted(fam.items()):
            print(f"  {f:<14} {n}")
        return

    if args.reveal:
        print(f"seed {man['seed']} -- {man['n_planted']} planted\n")
        for e in man["defects"]:
            print(f"  {e['id']}  [{e['family']}]")
            print(f"    {e['description']}")
            print(f"    {json.dumps(e['params'])}\n")
        return

    # default: score
    found = {a["id"] for a in attempts if a["hit"]}
    fp = [a["id"] for a in attempts if not a["hit"]]
    print(f"seed {args.seed}: {len(found)}/{man['n_planted']} found")
    for f in sorted(found):
        print(f"  HIT  {f}")
    for f in sorted(set(fp)):
        print(f"  MISS {f}")


if __name__ == "__main__":
    main()
