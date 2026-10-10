"""Independent local model of the 10-vertex unweighted parity module.

Written from the arc table (Table 2 of the paper), independently of check_final.py
and check_parity_ham.py.

Local model: module vertices sj,tj,A,B,Xl,Xr,Yl,Yr,Zl,Zr plus one permissive hub H
standing for "everything outside the module" (root s and all wheels).  Arcs:
  * 14 ordinary unit arcs (block semantics: into C lands at Cl, out of C leaves Cr)
  * forced contact edges Cl->Cr, Cr->Cl (unit each), f_- + f_+ >= 1
  * portals H->sj, tj->H (weight lambda, each >= 1); not in unit cost
  * wheel arcs H->Cr with multiplicity a_C (fixed input; cost charged to checker,
    not to this module) and Cl->H with multiplicity b_C (fixed input; unit cost,
    charged to this module since it leaves Cl)
Unit cost = total multiplicity of arcs leaving the nine unit vertices
{sj,A,B,Xl,Xr,Yl,Yr,Zl,Zr}.  D = unit cost - 9.
Constraints: balance at every module vertex; connectivity: every nonempty subset of
module vertices has an outgoing used arc (all 1023 cuts added explicitly).
"""
from __future__ import annotations

import itertools
from ortools.sat.python import cp_model

CONTACTS = ("X", "Y", "Z")
# Transcribed from Table 2 of the paper (tail -> heads)
TABLE = {
    "s": ["B", "Z"],
    "A": ["B", "X", "t"],
    "B": ["A", "Y"],
    "X": ["A", "Y", "Z"],
    "Y": ["B", "X"],
    "Z": ["Y", "t"],
}
BLOCK_ARCS = [(u, v) for u, vs in TABLE.items() for v in vs]
assert len(BLOCK_ARCS) == 14

MODULE = ["sj", "tj", "A", "B", "Xl", "Xr", "Yl", "Yr", "Zl", "Zr"]
UNIT_VERTS = ["sj", "A", "B", "Xl", "Xr", "Yl", "Yr", "Zl", "Zr"]


def phys(u, v):
    tail = u + "r" if u in CONTACTS else {"s": "sj", "t": "tj"}.get(u, u)
    head = v + "l" if v in CONTACTS else {"s": "sj", "t": "tj"}.get(v, v)
    return tail, head


ORD_ARCS = [phys(u, v) for u, v in BLOCK_ARCS]


def all_arcs():
    """list of (tail, head, kind, key)"""
    arcs = []
    for (t, h) in ORD_ARCS:
        arcs.append((t, h, "ord", f"{t}>{h}"))
    for c in CONTACTS:
        arcs.append((c + "l", c + "r", "fminus", c))   # l->r (gadget direction)
        arcs.append((c + "r", c + "l", "fplus", c))    # r->l (wheel direction)
        arcs.append(("H", c + "r", "win", c))
        arcs.append((c + "l", "H", "wout", c))
    arcs.append(("H", "sj", "pin", "p"))
    arcs.append(("tj", "H", "pout", "p"))
    return arcs


ARCS = all_arcs()
SUBSETS = [frozenset(S) for r in range(1, len(MODULE) + 1)
           for S in itertools.combinations(MODULE, r)]


def solve(a, b, orient=None, extra=None, maxmult=8, time_limit=30.0):
    """Min unit cost.  a,b: dict contact->multiplicity.  orient: dict contact->
    'LR' (only l->r), 'RL' (only r->l), 'BOTH' or None.  Returns (cost, sol) or
    (None, None) if infeasible."""
    m = cp_model.CpModel()
    x = []
    for i, (t, h, kind, key) in enumerate(ARCS):
        if kind == "win":
            v = m.NewConstant(a[key])
        elif kind == "wout":
            v = m.NewConstant(b[key])
        else:
            v = m.NewIntVar(0, maxmult, f"x{i}")
        x.append(v)
    idx = {(t, h, kind, key): i for i, (t, h, kind, key) in enumerate(ARCS)}
    # portals >=1
    for i, (t, h, kind, key) in enumerate(ARCS):
        if kind in ("pin", "pout"):
            m.Add(x[i] >= 1)
    for c in CONTACTS:
        fm = x[idx[(c + "l", c + "r", "fminus", c)]]
        fp = x[idx[(c + "r", c + "l", "fplus", c)]]
        m.Add(fm + fp >= 1)
        o = None if orient is None else orient.get(c)
        if o == "LR":
            m.Add(fm >= 1); m.Add(fp == 0)
        elif o == "RL":
            m.Add(fp >= 1); m.Add(fm == 0)
        elif o == "BOTH":
            m.Add(fm >= 1); m.Add(fp >= 1)
    # balance
    for v in MODULE:
        m.Add(sum(x[i] for i, A in enumerate(ARCS) if A[0] == v)
              == sum(x[i] for i, A in enumerate(ARCS) if A[1] == v))
    # connectivity cuts
    for S in SUBSETS:
        out = [x[i] for i, A in enumerate(ARCS) if A[0] in S and A[1] not in S]
        m.Add(sum(out) >= 1)
    if extra is not None:
        extra(m, x, idx)
    unit = sum(x[i] for i, A in enumerate(ARCS) if A[0] in UNIT_VERTS)
    m.Minimize(unit)
    s = cp_model.CpSolver()
    s.parameters.num_workers = 1
    s.parameters.max_time_in_seconds = time_limit
    st = s.Solve(m)
    if st == cp_model.INFEASIBLE:
        return None, None
    assert st == cp_model.OPTIMAL, s.StatusName(st)
    sol = {ARCS[i]: s.Value(x[i]) for i in range(len(ARCS)) if s.Value(x[i])}
    return int(round(s.ObjectiveValue())), sol


def verify_solution(a, b, sol):
    """Independent pure-python feasibility + cost recomputation of a returned solution."""
    mult = {k: v for k, v in sol.items()}
    for c in CONTACTS:
        assert mult.get(("H", c + "r", "win", c), 0) == a[c]
        assert mult.get((c + "l", "H", "wout", c), 0) == b[c]
        assert mult.get((c + "l", c + "r", "fminus", c), 0) + mult.get((c + "r", c + "l", "fplus", c), 0) >= 1
    assert mult.get(("H", "sj", "pin", "p"), 0) >= 1 and mult.get(("tj", "H", "pout", "p"), 0) >= 1
    bal = {v: 0 for v in MODULE + ["H"]}
    for (t, h, k, key), n in mult.items():
        bal[t] -= n; bal[h] += n
    assert all(bal[v] == 0 for v in MODULE), bal
    # connectivity (undirected) to H
    adj = {v: set() for v in MODULE + ["H"]}
    for (t, h, k, key), n in mult.items():
        if n > 0:
            adj[t].add(h); adj[h].add(t)
    seen = {"H"}; st = ["H"]
    while st:
        v = st.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w); st.append(w)
    assert all(v in seen for v in MODULE)
    return sum(n for (t, h, k, key), n in mult.items() if t in UNIT_VERTS)


def penalty(q, u, v):
    """#mismatches of contact values q with boundary presences + parity violation
    (equation X xor Y xor Z = 1)."""
    mis = sum((q[i] != u[i]) + (q[i] != v[i]) for i in range(3))
    return mis + (1 if sum(q) % 2 == 0 else 0)
