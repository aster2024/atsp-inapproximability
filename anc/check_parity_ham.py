"""Standalone exhaustive checker for the Hamiltonian port paths of a module given as a JSON arc list (Lemma 4.1)."""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path


def check(path: Path) -> None:
    data = json.loads(path.read_text())
    arcs = {tuple(pair) for pair in data["arcs"]}
    aux = tuple(data.get("aux", ("A", "B")))
    contacts = ("X", "Y", "Z")
    report = {}
    split_report = {}
    for count in range(4):
        for false in itertools.combinations(contacts, count):
            valid = []
            for perm in itertools.permutations(aux + false):
                route = ("s",) + perm + ("t",)
                if all((a, b) in arcs for a, b in zip(route, route[1:])):
                    valid.append(perm)
            expected = count % 2 == 0
            assert bool(valid) == expected, (false, expected, valid)
            report["".join(false) or "none"] = len(valid)
            if data.get("forbid_split") and not expected:
                covers = []
                for perm in itertools.permutations(aux + false):
                    for mask in range(1 << (len(perm) - 1)):
                        routes = []
                        start = 0
                        for i in range(len(perm) - 1):
                            if mask & (1 << i):
                                routes.append(("s",) + perm[start : i + 1] + ("t",))
                                start = i + 1
                        routes.append(("s",) + perm[start:] + ("t",))
                        if all((a, b) in arcs for route in routes for a, b in zip(route, route[1:])):
                            covers.append(routes)
                assert not covers, (false, covers[0])
                split_report["".join(false) or "none"] = 0
    print(json.dumps({"result": "PASS", "arc_count": len(arcs), "hamiltonian_paths": report, "forbidden_split_covers": split_report}, sort_keys=True))


if __name__ == "__main__":
    check(Path(sys.argv[1]))
