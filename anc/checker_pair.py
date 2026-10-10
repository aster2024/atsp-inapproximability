"""Brute-force the unchanged KLS matching-pair analysis under the rigorous
'deviation from arc presence' charging: a checker pays for each of its incident
cycle equations where its decoded value differs from the presence indicator
of the arc representing that cycle edge; the pair also pays its matching eq.
p=x^u_i: alpha = in-arc of p, delta = out-arc of q to u-successor
q=x^n_j: gamma = in-arc of q, beta  = out-arc of p to n-successor
forced p->q f1, q->p f2 (weight 2 each). cost = beta+delta+2(f1+f2).
Also records the minimum cost when both checkers are honest with value 1
(KLS p. 20 states >= 6; the true minimum is 5, see Remark 6.4 of the paper).
Exits with an AssertionError if any violation is found."""
import itertools
R = range(0, 5)
worst = None; bad = []; honest11_min = 99
for f1, f2 in itertools.product(range(0, 4), repeat=2):
    if f1 + f2 == 0: continue
    for al, be, ga, de in itertools.product(R, repeat=4):
        if al + f2 != be + f1 or ga + f1 != de + f2: continue
        if be + de == 0 and al + ga == 0: continue   # isolated pair (disconnected)
        cost = be + de + 2 * (f1 + f2)
        pa, pd, pg, pb = al > 0, de > 0, ga > 0, be > 0
        owed = min((p ^ q != 1) + (p != pa) + (p != pd) + (q != pg) + (q != pb)
                   for p in (0, 1) for q in (0, 1))
        if owed > cost - 3: bad.append((f1, f2, al, be, ga, de, cost, owed))
        if pa == pd == 1 and pg == pb == 1:
            honest11_min = min(honest11_min, cost)
        if cost < 3: bad.append(('cost<3', f1, f2, al, be, ga, de))
print("violations:", bad[:5], len(bad))
print("min cost when both honest with value 1:", honest11_min)
assert not bad, bad[:5]
assert honest11_min == 5
print("PASS")
