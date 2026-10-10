"""Bounded check of the module decoding lemma (Lemma 6.6), computed with CP-SAT.

(a) existence form: for every wheel multiplicity vector (a_C,b_C) in {0..K}^6,
    minD(a,b) >= min_q penalty(q; u=1[a>0], v=1[b>0]).
(b) proof-rule form: for every (a,b) in {0..K2}^6 and every orientation class
    (LR / RL / BOTH per contact), minD under that orientation >= penalty(q_rule),
    where q_rule is the decoder in the proof of Lemma 6.6 of the paper (incl. flips).
Also records tight cases and the global minimum slack.
"""
import itertools, json, sys, time
from gadget_local import CONTACTS, solve, verify_solution, penalty

K = int(sys.argv[1]) if len(sys.argv) > 1 else 2
K2 = int(sys.argv[2]) if len(sys.argv) > 2 else 1
out = {"K": K, "K2": K2}


def best_pen(u, v):
    return min(penalty(q, u, v) for q in itertools.product((0, 1), repeat=3))


t0 = time.time()
cnt = 0; tight = 0; minslack = 99; worst = None; infeas = 0
for ab in itertools.product(range(K + 1), repeat=6):
    a = {c: ab[2 * i] for i, c in enumerate(CONTACTS)}
    b = {c: ab[2 * i + 1] for i, c in enumerate(CONTACTS)}
    cost, sol = solve(a, b)
    if cost is None:
        infeas += 1
        continue
    assert verify_solution(a, b, sol) == cost
    D = cost - 9
    u = [int(a[c] > 0) for c in CONTACTS]; v = [int(b[c] > 0) for c in CONTACTS]
    P = best_pen(u, v)
    cnt += 1
    if D - P < minslack:
        minslack = D - P; worst = (ab, D, P)
    tight += (D == P)
    if D < P:
        print("VIOLATION existence form", ab, D, P, sol); sys.stdout.flush()
out["existence"] = {"feasible": cnt, "infeasible": infeas, "tight": tight, "min_slack": minslack,
                    "worst": worst, "sec": round(time.time() - t0, 1)}
print(json.dumps(out["existence"])); sys.stdout.flush()


def rule_q(orient, u, v):
    """Decoder from the proof of Lemma 6.6 (Module decoding) of the paper."""
    q = []
    for i in range(3):
        o = orient[i]
        if o == "RL":
            q.append(1)
        elif o == "LR":
            q.append(0)
        else:  # BOTH: majority of u,v; tie -> 0 (either allowed)
            q.append(u[i] if u[i] == v[i] else 0)
    if sum(q) % 2 == 1:
        return q
    # even parity -> try flips as in the proof
    for i in range(3):
        if orient[i] == "LR" and (u[i] + v[i]) >= 1:
            q2 = list(q); q2[i] ^= 1; return q2
    for i in range(3):
        if orient[i] == "BOTH" and u[i] != v[i]:
            q2 = list(q); q2[i] ^= 1; return q2
    return q  # keep parity violation


t0 = time.time()
cnt = 0; tight = 0; minslack = 99; worst = None
for ab in itertools.product(range(K2 + 1), repeat=6):
    a = {c: ab[2 * i] for i, c in enumerate(CONTACTS)}
    b = {c: ab[2 * i + 1] for i, c in enumerate(CONTACTS)}
    u = [int(a[c] > 0) for c in CONTACTS]; v = [int(b[c] > 0) for c in CONTACTS]
    for ori in itertools.product(("LR", "RL", "BOTH"), repeat=3):
        cost, sol = solve(a, b, orient=dict(zip(CONTACTS, ori)))
        if cost is None:
            continue
        assert verify_solution(a, b, sol) == cost
        D = cost - 9
        q = rule_q(ori, u, v)
        P = penalty(q, u, v)
        cnt += 1
        tight += (D == P)
        if D - P < minslack:
            minslack = D - P; worst = (ab, ori, D, P, q)
        if D < P:
            print("VIOLATION proof-rule form", ab, ori, D, P, q, sol); sys.stdout.flush()
out["rule"] = {"feasible": cnt, "tight": tight, "min_slack": minslack, "worst": worst,
               "sec": round(time.time() - t0, 1)}
print(json.dumps(out["rule"]))
json.dump(out, open(f"check2_K{K}_K2{K2}.json", "w"), indent=1)
