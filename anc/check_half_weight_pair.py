"""Exact bounded checker-pair audit for wheel arcs 1/2, forced edge 1."""

from itertools import product


def main():
    seen=0;tight=0
    for alpha,beta,gamma,delta,f,g in product(range(5),repeat=6):
        if f+g<1 or alpha+g!=beta+f or gamma+f!=delta+g:
            continue
        if alpha+beta+gamma+delta==0:
            continue  # otherwise the pair is isolated from the root
        cost=beta+delta+2*(f+g)  # all quantities scaled by 2
        owed=min(2*int(p==q)
                 +int(p!=(alpha>0))+int(p!=(delta>0))
                 +int(q!=(gamma>0))+int(q!=(beta>0))
                 for p,q in product((0,1),repeat=2))
        assert cost>=3 and owed<=cost-3,(alpha,beta,gamma,delta,f,g,cost,owed)
        seen+=1;tight+=owed==cost-3
    print({"result":"PASS","profiles":seen,"tight":tight,
           "scaled_baseline":3,"weights_scaled":{"wheel":1,"forced_match":2}})


if __name__=="__main__":
    main()
