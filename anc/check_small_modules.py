"""Exhaustive search: no module with 0 or 1 auxiliary vertices has the parity property.

Standard library only.  Usage:  python3 check_small_modules.py

Block notation as in the paper: s = s_j, t = t_j, auxiliary vertices, and
contact blocks X, Y, Z.  A candidate module is any set of arcs from
{s} + blocks to blocks + {t} (no loops; the arc s->t is allowed).  It has the
*parity property* if for every F subset of {X, Y, Z} there is a Hamiltonian
s->t path through (auxiliaries + F) exactly when |F| is even.

For k = 0 and k = 1 auxiliary vertices this script enumerates all 2^13 resp.
2^21 arc sets and reports how many have the parity property.  The expected
output is 0 for both, i.e. at least two auxiliary vertices are needed within
this class.  As a sanity check of the test itself, the same routine is applied
to the 14-arc module of parity_boundary.json (two auxiliary vertices), which
must pass, and to that module plus the arc X->t, which must fail.  (This is a
remark in the paper; the main theorem does not depend on it.)
"""

from __future__ import annotations

import itertools
import json

CONTACTS = ("X", "Y", "Z")


def has_parity(aux: tuple[str, ...], arcs: set) -> bool:
    for r in range(4):
        for F in itertools.combinations(CONTACTS, r):
            has = any(all(e in arcs for e in zip(("s",) + p, p + ("t",)))
                      for p in itertools.permutations(aux + F))
            if has != (r % 2 == 0):
                return False
    return True


def search(aux: tuple[str, ...], cand=None) -> dict:
    blocks = aux + CONTACTS
    if cand is None:
        cand = [(a, b) for a in ("s",) + blocks for b in blocks + ("t",) if a != b]
    index = {e: i for i, e in enumerate(cand)}
    profiles = []  # (even?, list of path masks)
    for r in range(4):
        for F in itertools.combinations(CONTACTS, r):
            masks = []
            for p in itertools.permutations(aux + F):
                route = ("s",) + p + ("t",)
                edges = list(zip(route, route[1:]))
                if not all(e in index for e in edges):
                    continue  # uses an arc outside the candidate list
                m = 0
                for e in edges:
                    m |= 1 << index[e]
                masks.append(m)
            profiles.append((r % 2 == 0, masks))
    # check cheap profiles first
    profiles.sort(key=lambda x: len(x[1]))
    n = len(cand)
    good = []
    for S in range(1 << n):
        ok = True
        for even, masks in profiles:
            has = any(m & S == m for m in masks)
            if has != even:
                ok = False
                break
        if ok:
            good.append([cand[i] for i in range(n) if S >> i & 1])
    return {"aux": list(aux), "candidate_arcs": n, "arc_sets": 1 << n,
            "with_parity_property": len(good), "examples": good[:3],
            "all_found": good}


def main() -> None:
    from pathlib import Path
    gadget = {tuple(e) for e in json.loads(
        Path(__file__).with_name("parity_boundary.json").read_text())["arcs"]}
    assert has_parity(("A", "B"), gadget)
    assert not has_parity(("A", "B"), gadget | {("X", "t")})
    # positive control for the fast search: two auxiliaries, candidate arcs =
    # the 14 gadget arcs plus six others; the gadget itself must be found.
    extra = [("X", "t"), ("s", "A"), ("A", "Z"), ("Y", "t"), ("Z", "X"), ("B", "t")]
    ctrl = search(("A", "B"), sorted(gadget) + extra)
    assert ctrl["with_parity_property"] >= 1
    res = [search(()), search(("A",))]
    for r in res:  # cross-check the fast search with the direct test
        for ex in r["examples"]:
            assert has_parity(tuple(r["aux"]), {tuple(e) for e in ex})
    assert sorted(gadget) in [sorted(map(tuple, g)) for g in ctrl["all_found"]]
    assert all(r["with_parity_property"] == 0 for r in res), res
    for r in res + [ctrl]:
        del r["all_found"]
    print(json.dumps({"result": "PASS", "searches": res,
                      "positive_control_two_aux_restricted": {
                          "candidate_arcs": ctrl["candidate_arcs"],
                          "with_parity_property": ctrl["with_parity_property"]}}))


if __name__ == "__main__":
    main()
