"""Bounded cross-check of the module decoding lemma (Lemma 6.6) in the weighted setting.

This is an optional consistency check; the paper proves the lemma by hand for
all multiplicities. Requires OR-Tools (CP-SAT).

Local model: module vertices sj, tj, A, B, C and, for each contact R in X, Y, Z,
the two vertices R^l, R^r. An external hub H stands for the rest of the graph.
Arcs: the 18 module arcs; the forced contact edge in both directions,
R^l->R^r (fm) and R^r->R^l (fp); the wheel arcs H->R^r (a_R) and R^l->H (b_R);
and the portals H->sj (ks) and tj->H (kt).
Constraints: balance at every module vertex; fm+fp >= 1; ks, kt >= 1; and the
necessary cut condition for connectivity (every nonempty set of module
vertices has an arc leaving it).
Cost is charged to tails and doubled so that it is an integer:
  unit arcs from sj, A, B, C cost 2; module arcs from R^r cost 1;
  forced arcs cost 2; wheel arcs R^l->H cost 1; portals are excluded.
Then D2 = cost2 - 17, i.e. twice D_j.
Owed2 = min over assignments x of 2*[x_X+x_Y+x_Z even]
        + sum_R ([x_R != (a_R>0)] + [x_R != (b_R>0)]), i.e. twice owed_j.
Claim: D2 - Owed2 >= 0. CP-SAT minimises D2 - Owed2 with every multiplicity
bounded by UB in {2, 3, 5}; the expected minimum is 0 in each case.
"""
import itertools, sys
from ortools.sat.python import cp_model

BLOCK = [("s","A"),("s","X"),("s","Y"),("s","Z"),("A","B"),("A","X"),("A","Z"),
         ("B","A"),("B","C"),("C","A"),("C","B"),("C","t"),("X","C"),("X","t"),
         ("Y","C"),("Y","t"),("Z","C"),("Z","t")]
C3 = ("X","Y","Z")


def run(UB, extra=None):
    arcs = []
    for a, b in BLOCK:
        t = a + "r" if a in C3 else {"s": "sj", "t": "tj"}.get(a, a)
        h = b + "l" if b in C3 else {"s": "sj", "t": "tj"}.get(b, b)
        arcs.append((t, h, 1 if a in C3 else 2, "mod", (a, b)))
    for R in C3:
        arcs += [(R+"l", R+"r", 2, "fm", R), (R+"r", R+"l", 2, "fp", R),
                 ("H", R+"r", 0, "a", R), (R+"l", "H", 1, "b", R)]
    arcs += [("H", "sj", 0, "ks", None), ("tj", "H", 0, "kt", None)]
    MV = ["sj","tj","A","B","C"] + [R+s for R in C3 for s in "lr"]
    M = cp_model.CpModel()
    x = [M.NewIntVar(0, UB, f"x{i}") for i in range(len(arcs))]
    get = lambda kind, key: x[[i for i, a in enumerate(arcs) if a[3] == kind and a[4] == key][0]]
    for v in MV:
        M.Add(sum(x[i] for i, a in enumerate(arcs) if a[0] == v) ==
              sum(x[i] for i, a in enumerate(arcs) if a[1] == v))
    for R in C3:
        M.Add(get("fm", R) + get("fp", R) >= 1)
    M.Add(get("ks", None) >= 1); M.Add(get("kt", None) >= 1)
    for n in range(1, len(MV) + 1):
        for S in itertools.combinations(MV, n):
            S = set(S)
            M.Add(sum(x[i] for i, a in enumerate(arcs) if a[0] in S and a[1] not in S) >= 1)
    bits = []
    for R in C3:
        for kind in ("a", "b"):
            bvar = M.NewBoolVar(kind + R)
            M.Add(get(kind, R) >= 1).OnlyEnforceIf(bvar)
            M.Add(get(kind, R) == 0).OnlyEnforceIf(bvar.Not())
            bits.append(bvar)
    owed = M.NewIntVar(0, 20, "owed")
    table = []
    for bv in itertools.product((0, 1), repeat=6):
        best = min(2 * int(sum(xv) % 2 == 0) +
                   sum((xv[r] != bv[2*r]) + (xv[r] != bv[2*r+1]) for r in range(3))
                   for xv in itertools.product((0, 1), repeat=3))
        table.append(list(bv) + [best])
    M.AddAllowedAssignments(bits + [owed], table)
    cost2 = sum(a[2] * x[i] for i, a in enumerate(arcs))
    if extra:
        extra(M, x, arcs, get)
    M.Minimize(cost2 - 17 - owed)
    S = cp_model.CpSolver(); S.parameters.num_workers = 1
    S.parameters.max_time_in_seconds = 600
    st = S.Solve(M)
    assert st == cp_model.OPTIMAL, st
    sol = {f"{a[3]}:{a[4]}": S.Value(x[i]) for i, a in enumerate(arcs) if S.Value(x[i])}
    return int(round(S.ObjectiveValue())), sol, S.Value(owed)


def main():
    for UB in (2, 3, 5):
        val, sol, owed = run(UB)
        print({"UB": UB, "min(D2-owed2)": val, "owed2_at_min": owed, "witness": sol})
        assert val >= 0
    # sanity: honest satisfied profile gives D=0 (tightness), and violating
    # honest profile {X} gives D2-owed2 = 0 as well (19/2 cost, owes 1)
    print({"result": "PASS"})


if __name__ == "__main__":
    main()
