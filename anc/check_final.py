"""Standalone exact checker for the 73/72 ATSP module certificate.

Only Python's standard library is needed.  This checks all finite gadget
claims and rational arithmetic; the infinite reduction/decoder is proved in
the accompanying written argument, not inferred from computation.
"""

from __future__ import annotations

import heapq
import itertools
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONTACTS = ("X", "Y", "Z")


def shortest_profile(arcs, aux, false):
    required = tuple(aux) + false
    mask_all = (1 << len(required)) - 1
    start = ("s", 0)
    goal = ("t", mask_all)
    distances = {start: 0}
    heap = [(0, start)]
    while heap:
        cost, (node, mask) = heapq.heappop(heap)
        if distances[node, mask] != cost:
            continue
        if (node, mask) == goal:
            return cost + 2 * (3 - len(false))
        for a, b in arcs:
            if a != node or b in CONTACTS and b not in false:
                continue
            new_mask = mask | (1 << required.index(b)) if b in required else mask
            state = (b, new_mask)
            new_cost = cost + 1 + int(b in CONTACTS)
            if new_cost < distances.get(state, 10**9):
                distances[state] = new_cost
                heapq.heappush(heap, (new_cost, state))
        if node == "t" and mask != mask_all:
            state = ("s", mask)
            if cost < distances.get(state, 10**9):
                distances[state] = cost
                heapq.heappush(heap, (cost, state))
    raise AssertionError(("unreachable", false))


def check():
    data = json.loads((HERE / "parity_boundary.json").read_text())
    aux = tuple(data.get("aux", ("A", "B")))
    assert aux == ("A", "B")
    arcs = {tuple(edge) for edge in data["arcs"]}
    assert len(arcs) == len(data["arcs"]) == 14
    blocks = set(aux + CONTACTS)
    assert all(a in blocks | {"s"} and b in blocks | {"t"} and a != b for a, b in arcs)
    assert not any(b == "s" or a == "t" or (a, b) == ("s", "t") for a, b in arcs)
    connector_paths = {
        "X": ("s", "B", "A", "X", "A", "t"),
        "Y": ("s", "B", "Y", "B", "A", "t"),
        "Z": ("s", "Z", "t"),
    }
    for contact, path in connector_paths.items():
        assert contact in path
        assert all((a, b) in arcs for a, b in zip(path, path[1:]))
        assert len(path) - 1 + 1 <= 6  # ordinary arcs + opposite forced contact arc
    results = {}
    for size in range(4):
        for false in itertools.combinations(CONTACTS, size):
            hamiltonian = 0
            for order in itertools.permutations(aux + false):
                route = ("s",) + order + ("t",)
                hamiltonian += all((a, b) in arcs for a, b in zip(route, route[1:]))
            expected = size % 2 == 0
            assert bool(hamiltonian) == expected, (false, hamiltonian)
            cost = shortest_profile(arcs, aux, false)
            assert cost == (9 if expected else 10), (false, cost)
            results["".join(false) or "none"] = (hamiltonian, cost)
    baseline = 9 * 3 + 9
    gap = Fraction(1, 2)
    hardness = (baseline + gap) / baseline
    assert baseline == 36 and hardness == Fraction(73, 72)
    assert hardness > Fraction(75, 74)
    eps = delta = lam = Fraction(1, 100000)
    forced_path_length = 10000000
    yes_coefficient = baseline + 2 * lam + (1 + 2 * lam) * eps + (6 + 2 * lam) * delta
    no_coefficient = baseline + 2 * lam + gap - eps - Fraction(42, forced_path_length)
    explicit_ratio = no_coefficient / yes_coefficient
    assert explicit_ratio > Fraction(75, 74)
    print(json.dumps({"result": "PASS", "profiles": results, "baseline": baseline, "source_gap": str(gap), "limit_ratio": str(hardness), "explicit_parameters": {"epsilon": str(eps), "delta": str(delta), "lambda": str(lam), "forced_path_length": forced_path_length}, "explicit_ratio": str(explicit_ratio)}, sort_keys=True))


if __name__ == "__main__":
    check()
