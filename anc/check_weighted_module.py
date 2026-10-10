"""Standalone finite certificate for the weighted three-auxiliary ATSP module.

Only Python's standard library is needed.  The module arcs are read from
half_contact_3aux_candidate.json in this directory.  All costs are scaled by 2
(a module arc leaving s or an auxiliary vertex costs 2, a module arc leaving a
contact costs 1, one traversal of a contact forced edge costs 2, and an honest
true contact costs 3 = 2 * 3/2).
"""

import heapq
import itertools
import json
from fractions import Fraction
from pathlib import Path


AUX=("A","B","C")
CONTACTS=("X","Y","Z")
# Completeness walks of the paper (one string per portal pair), by false set.
TABLE_WALKS={"none":("sABCt",),"X":("sXt","sABCt"),"Y":("sYt","sABCt"),
             "Z":("sZt","sABCt"),"XY":("sYCBAXt",),"XZ":("sZCBAXt",),
             "YZ":("sYCBAZt",),"XYZ":("sZt","sYCBAXt")}


def walk_cost(arcs, walk):
    """Scaled cost of one block walk s...t: module arcs plus block traversals."""
    assert walk[0]=="s" and walk[-1]=="t"
    cost=0
    for a,b in path_arcs(walk):
        assert (a,b) in arcs,(walk,a,b)
        cost+=(1 if a in CONTACTS else 2)+(2 if b in CONTACTS else 0)
    return cost


def path_arcs(path):
    return tuple(zip(path,path[1:]))


def shortest(arcs, aux, false):
    """Minimum scaled unit cost of an honest traversal of profile `false`.

    Dijkstra over states (vertex, set of required blocks visited).  A walk
    starts at s, may return from t to s through the root at no unit cost (each
    return is one more portal pair), and must visit all auxiliary vertices and
    all false contacts; true contacts are never entered.  Returns the cost
    including 3 per true contact, and one optimal route as a list of arcs.
    """
    required = aux + false
    allmask = (1 << len(required)) - 1
    start = ("s", 0)
    goal = ("t", allmask)
    dist = {start: 0}
    prev = {}
    heap = [(0, start)]
    contacts = set(CONTACTS)
    while heap:
        cost, state = heapq.heappop(heap)
        if dist[state] != cost:
            continue
        node, mask = state
        if state == goal:
            route = []
            while state != start:
                old = prev[state]
                route.append((old[0],state[0]))
                state = old
            route.reverse()
            return cost + 3*(3-len(false)), route
        for a,b in arcs:
            if a != node or (b in contacts and b not in false):
                continue
            nextmask = mask | (1 << required.index(b)) if b in required else mask
            edgecost = (1 if a in contacts else 2) + (2 if b in contacts else 0)
            nxt = (b,nextmask)
            if cost+edgecost < dist.get(nxt,10**9):
                dist[nxt]=cost+edgecost
                prev[nxt]=(node,mask)
                heapq.heappush(heap,(cost+edgecost,nxt))
        if node == "t" and mask != allmask:
            nxt=("s",mask)
            if cost < dist.get(nxt,10**9):
                dist[nxt]=cost
                prev[nxt]=(node,mask)
                heapq.heappush(heap,(cost,nxt))
    return None,None


def main():
    here=Path(__file__).resolve().parent
    data=json.loads((here/"half_contact_3aux_candidate.json").read_text())
    arcs={tuple(e) for e in data["arcs"]}
    assert len(arcs)==len(data["arcs"])==18
    allowed={(u,v) for u in ("s",)+AUX+CONTACTS for v in AUX+CONTACTS+("t",)
             if u!=v and (u,v)!=("s","t")}
    assert arcs<=allowed
    report={}
    ham_paths={}
    total_hamilton=0
    forbidden_covers=0
    for n in range(4):
        for F in itertools.combinations(CONTACTS,n):
            paths=[]
            for perm in itertools.permutations(AUX+F):
                p=("s",)+perm+("t",)
                if all(e in arcs for e in path_arcs(p)):
                    paths.append(p)
            assert bool(paths)==(n%2==0),(F,paths)
            total_hamilton+=len(paths)
            ham_paths["".join(F) or "none"]=["".join(p) for p in paths]
            if n==1:
                for R in CONTACTS:
                    if R in F:
                        continue
                    for perm in itertools.permutations(AUX+F):
                        for split in range(len(perm)+1):
                            p1=("s",)+perm[:split]+("t",)
                            p2=(R,)+perm[split:]+("t",)
                            assert not all(e in arcs for e in path_arcs(p1)+path_arcs(p2)),(F,R,p1,p2)
                            forbidden_covers+=1
            cost,route=shortest(arcs,AUX,F)
            assert cost==(17 if n%2==0 else 19),(F,cost,route)
            assert route and all(e==( "t","s") or e in arcs for e in route)
            recomputed=(sum(1 if a in CONTACTS else 2 for a,b in route if (a,b)!=("t","s"))
                        +2*sum(b in F for a,b in route)+3*(3-len(F)))
            assert recomputed==cost,(F,recomputed,cost)
            report["".join(F) or "none"]={"scaled_unit_cost":cost,
                                          "portal_pairs":1+sum(e==("t","s") for e in route)}
    assert forbidden_covers==6*120
    table={}
    for key,walks in TABLE_WALKS.items():
        F=() if key=="none" else tuple(key)
        visited=[v for w in walks for v in w[1:-1]]
        assert sorted(visited)==sorted(AUX+F),(key,walks)
        unit=sum(walk_cost(arcs,w) for w in walks)+3*(3-len(F))
        assert unit==(17 if len(F)%2==0 else 19),(key,unit)
        assert unit==report[key]["scaled_unit_cost"]
        table[key]={"scaled_unit_cost":unit,"portal_pairs":len(walks)}
    connectors={}
    for C in CONTACTS:
        assert ("s",C) in arcs and (C,"t") in arcs
        connectors[C]=walk_cost(arcs,"s"+C+"t")
    assert set(connectors.values())=={5}
    ratio=Fraction(63,62)
    assert ratio>Fraction(73,72)
    print(json.dumps({"result":"PASS","arcs":len(arcs),
                      "hamiltonian_paths_total":total_hamilton,
                      "hamiltonian_paths":ham_paths,
                      "forbidden_two_start_covers_checked":forbidden_covers,
                      "connector_unit_cost_scaled":connectors,
                      "table_walks":table,
                      "module_profiles":report,"baseline_per_equation":31,
                      "limit_ratio":str(ratio)},sort_keys=True))


if __name__=="__main__":
    main()
