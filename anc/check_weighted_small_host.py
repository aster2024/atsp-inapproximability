"""Pure-stdlib end-to-end completeness smoke check for the weighted directed graph."""

import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


def main():
    root="root"
    lam=Fraction(1,100)
    table=json.loads((Path(__file__).resolve().parent/"half_contact_3aux_candidate.json").read_text())["arcs"]
    walks={"":("sABCt",),"X":("sXt","sABCt"),"Y":("sYt","sABCt"),
           "Z":("sZt","sABCt"),"XY":("sYCBAXt",),
           "XZ":("sZCBAXt",),"YZ":("sYCBAZt",),
           "XYZ":("sZt","sYCBAXt")}
    wheel=[];partner={};contacts=set();equations=[]
    for i in range(3):
        U=[f"w{i}u1",f"w{i}u2",f"w{i}uc"]
        N=[f"w{i}n1",f"w{i}n2",f"w{i}nc"]
        partner[U[0]]=N[0];partner[N[0]]=U[0]
        partner[U[1]]=N[1];partner[N[1]]=U[1]
        contacts.update((U[2],N[2]))
        wheel.append((U,N))
    equations=[tuple(wheel[i][0][2] for i in range(3)),
               tuple(wheel[i][1][2] for i in range(3))]
    verts={root}
    graph={}
    used=Counter()
    forced_pairs=[];portals=[]
    def add_arc(u,v,w):
        assert (u,v) not in graph or graph[(u,v)]==w,(u,v)
        graph[(u,v)]=w;verts.update((u,v))
    def take(u,v):
        assert (u,v) in graph,(u,v)
        used[(u,v)]+=1
    def entry(v): return v+"r" if v in contacts else v
    def exit_(v): return v+"l" if v in contacts else partner[v]
    for U,N in wheel:
        for cyc in (U,N):
            for i,v in enumerate(cyc):
                add_arc(exit_(v),entry(cyc[(i+1)%len(cyc)]),Fraction(1,2))
    for u,n in list(partner.items()):
        if u>n: continue
        add_arc(u,n,Fraction(1));add_arc(n,u,Fraction(1))
        forced_pairs.append(((u,n),(n,u)))
    for c in contacts:
        add_arc(c+"l",c+"r",Fraction(1))
        add_arc(c+"r",c+"l",Fraction(1))
        forced_pairs.append(((c+"l",c+"r"),(c+"r",c+"l")))
    for j,eq in enumerate(equations):
        loc={"s":f"s{j}","t":f"t{j}","A":f"A{j}","B":f"B{j}","C":f"C{j}",
             "X":eq[0],"Y":eq[1],"Z":eq[2]}
        add_arc(root,loc["s"],lam);add_arc(loc["t"],root,lam)
        portals += [(root,loc["s"]),(loc["t"],root)]
        for a,b in table:
            tail=loc[a]+"r" if a in "XYZ" else loc[a]
            head=loc[b]+"l" if b in "XYZ" else loc[b]
            add_arc(tail,head,Fraction(1,2) if a in "XYZ" else Fraction(1))
    # Consistent wheel values: first variable chooses U, other two choose N.
    true_sides=(0,1,1)
    for (U,N),side in zip(wheel,true_sides):
        cyc=(U,N)[side]
        for i,v in enumerate(cyc):
            take(entry(v),exit_(v))
            take(exit_(v),entry(cyc[(i+1)%len(cyc)]))
    def add_block_walk(j,path):
        eq=equations[j]
        loc={"s":f"s{j}","t":f"t{j}","A":f"A{j}","B":f"B{j}","C":f"C{j}",
             "X":eq[0],"Y":eq[1],"Z":eq[2]}
        take(root,loc["s"])
        for a,b in zip(path,path[1:]):
            tail=loc[a]+"r" if a in "XYZ" else loc[a]
            head=loc[b]+"l" if b in "XYZ" else loc[b]
            take(tail,head)
            if b in "XYZ": take(loc[b]+"l",loc[b]+"r")
        take(loc["t"],root)
    # Eq0 U contacts: (1,0,0) => F=YZ. Eq1 N: (0,1,1) => F=X.
    for path in walks["YZ"]: add_block_walk(0,path)
    for path in walks["X"]: add_block_walk(1,path)
    # Three connectors, one per wheel, through a true contact.
    for j,cpos in ((0,"X"),(1,"Y"),(1,"Z")):
        add_block_walk(j,"s"+cpos+"t")
    assert all(used[a]+used[b]>=1 for a,b in forced_pairs)
    assert all(used[p]>=1 for p in portals)
    indeg=Counter();outdeg=Counter()
    for (u,v),n in used.items():
        outdeg[u]+=n;indeg[v]+=n
    assert all(indeg[v]==outdeg[v]>=1 for v in verts),(indeg,outdeg)
    # Weak connectivity of the balanced support implies an Euler tour.
    seen={root};queue=[root]
    while queue:
        v=queue.pop()
        for (a,b),n in used.items():
            if n and a==v and b not in seen:seen.add(b);queue.append(b)
            if n and b==v and a not in seen:seen.add(a);queue.append(a)
    assert seen==verts,(len(seen),len(verts))
    cost=sum(graph[e]*n for e,n in used.items())
    expected=Fraction(69,2)+12*lam
    assert cost==expected,(cost,expected)
    print({"result":"PASS","vertices":len(verts),"available_arcs":len(graph),
           "used_arc_types":sum(bool(n) for n in used.values()),"balanced_connected":True,
           "source_ternary_violations":1,"cost":str(cost),"bound":str(expected)})


if __name__=="__main__":
    main()
