"""Check the finite tables printed in the paper against parity_boundary.json.

Standard library only.  Usage:  python3 check_tables.py [parity_boundary.json]

Block notation (as in the paper): s = s_j, t = t_j, A and B are the auxiliary
vertices, and a contact letter C in {X, Y, Z} stands for the block
C^l -> C^r (an arc into C ends at C^l, an arc out of C starts at C^r).

Checks:
  1. The 14-arc table of the paper equals the arc set of the JSON certificate.
  2. Hamiltonian s->t paths through {A, B} + F exist iff |F| is even, and the
     paths listed in the paper are exactly the Hamiltonian paths.
  3. Every completeness walk in the paper uses only listed arcs, visits A, B and
     every false contact, never enters a true contact, and has the stated unit
     cost (9 if the equation X+Y+Z=1 holds, 10 otherwise) and portal count.
  4. The three connector walks have unit cost 6, 6, 3 and one portal pair.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

CONTACTS = ("X", "Y", "Z")

# Table 2 of the paper (tail -> heads).
PAPER_ARCS = {
    "s": ("B", "Z"),
    "A": ("B", "X", "t"),
    "B": ("A", "Y"),
    "X": ("A", "Y", "Z"),
    "Y": ("B", "X"),
    "Z": ("Y", "t"),
}

# Table 4 of the paper: false set -> list of s->t walks (one per portal pair).
PAPER_WALKS = {
    "": ["sBAt"],
    "X": ["sBAXAt"],
    "Y": ["sBYBAt"],
    "Z": ["sZt", "sBAt"],
    "XY": ["sBYXAt"],
    "XZ": ["sBAXZt"],
    "YZ": ["sZYBAt"],
    "XYZ": ["sZYXABAt"],
}
PAPER_COST = {F: (9 if len(F) % 2 == 0 else 10) for F in PAPER_WALKS}
PAPER_PORTALS = {F: len(w) for F, w in PAPER_WALKS.items()}

# Hamiltonian paths listed in the paper (Lemma on the parity property).
PAPER_HAM = {"": ["sBAt"], "XY": ["sBYXAt"], "XZ": ["sBAXZt"], "YZ": ["sZYBAt"]}

# Connector walks (component joining in the completeness proof).
PAPER_CONNECTORS = {"X": ("sBAXAt", 6), "Y": ("sBYBAt", 6), "Z": ("sZt", 3)}


def unit_cost(walks, false, arcs):
    """Unit cost of a walk system for the honest profile with false set `false`.

    Counts every ordinary arc (each leaves a unit vertex s_j, A, B or C^r), one
    unit for each traversal of a false contact block (the forced arc C^l->C^r,
    which leaves C^l), and 2 for each true contact (forced C^r->C^l plus the
    wheel arc leaving C^l).  Portal arcs (weight lambda) are not counted.
    """
    cost = 2 * sum(1 for c in CONTACTS if c not in false)
    seen = set()
    for w in walks:
        assert w[0] == "s" and w[-1] == "t", w
        assert "s" not in w[1:] and "t" not in w[:-1], w
        for a, b in zip(w, w[1:]):
            assert (a, b) in arcs, (w, a, b)
            cost += 1
        for v in w[1:-1]:
            seen.add(v)
            if v in CONTACTS:
                assert v in false, ("walk enters a true contact", w, v)
                cost += 1
    assert seen == {"A", "B"} | set(false), (walks, seen)
    return cost


def main(path: Path) -> None:
    data = json.loads(path.read_text())
    arcs = {tuple(e) for e in data["arcs"]}
    paper = {(a, b) for a, hs in PAPER_ARCS.items() for b in hs}
    assert len(paper) == 14 and paper == arcs, (sorted(paper ^ arcs))

    ham = {}
    for r in range(4):
        for F in itertools.combinations(CONTACTS, r):
            key = "".join(F)
            found = sorted(
                "s" + "".join(p) + "t"
                for p in itertools.permutations(("A", "B") + F)
                if all((a, b) in arcs for a, b in zip(("s",) + p, p + ("t",)))
            )
            assert bool(found) == (r % 2 == 0), (key, found)
            assert found == sorted(PAPER_HAM.get(key, [])), (key, found)
            ham[key or "none"] = found

    costs = {}
    for F, walks in PAPER_WALKS.items():
        c = unit_cost(walks, F, arcs)
        assert c == PAPER_COST[F], (F, c)
        costs[F or "none"] = (c, PAPER_PORTALS[F])

    for C, (w, stated) in PAPER_CONNECTORS.items():
        c = 0
        assert w[0] == "s" and w[-1] == "t" and C in w
        for a, b in zip(w, w[1:]):
            assert (a, b) in arcs, (w, a, b)
            c += 1
        c += sum(1 for v in w if v in CONTACTS)  # forced C^l -> C^r
        assert c == stated, (C, c)

    unused = sorted(arcs - {(a, b) for ws in PAPER_WALKS.values() for w in ws
                            for a, b in zip(w, w[1:])}
                    - {(a, b) for w, _ in PAPER_CONNECTORS.values() for a, b in zip(w, w[1:])})
    print(json.dumps({"result": "PASS", "hamiltonian_paths": ham,
                      "walk_unit_cost_and_portal_pairs": costs,
                      "connector_costs": {C: v[1] for C, v in PAPER_CONNECTORS.items()},
                      "arcs_unused_by_all_walks": unused}, sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("parity_boundary.json"))
