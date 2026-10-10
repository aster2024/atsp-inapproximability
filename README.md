# A 63/62 inapproximability bound for the asymmetric traveling salesman problem

Jizhou Guo — mitsuha2021b@gmail.com — 10 October 2026

[**Paper (PDF, 22 pages)**](paper.pdf) · [LaTeX source](source/) · [Programs](anc/)

## Results

ATSP is the metric traveling salesman problem with distances that satisfy the triangle inequality but need not be
symmetric.

**Theorem 1.1.** For every ε > 0 it is NP-hard to approximate ATSP within a factor of 63/62 − ε.

**Theorem 1.3.** For every ε > 0 it is NP-hard to approximate ATSP within a factor of 73/72 − ε, by a reduction
whose only external ingredient is the source theorem of Karpinski, Lampis and Schmied, the same source as for their
bound 75/74.

The bound for ATSP stated by Karpinski, Lampis and Schmied (ISAAC 2013; J. Comput. System Sci. 2015) is 75/74. It
is the bound listed for ATSP in the survey of Saller, Koehler and Karrenbauer
([arXiv:2311.00604](https://arxiv.org/abs/2311.00604), Table 1).

## How the bounds arise

Both theorems follow the directed reduction of Karpinski, Lampis and Schmied from a bounded-occurrence system of
linear equations modulo 2 built on bi-wheel amplifiers. In their reduction a matched pair of checker variables costs
3 and a three-variable equation costs 10; with 9 matched pairs per equation and a gap of 1/2 this gives
(37 + 1/2)/37 = 75/74.

| | source | matched pairs per equation | cost of a pair | cost of the equation module | total | bound |
|---|---|---|---|---|---|---|
| Karpinski–Lampis–Schmied | unweighted bi-wheels | 9 | 3 | 10 | 37 | 75/74 |
| Theorem 1.3 | unweighted bi-wheels | 9 | 3 | 9 | 36 | 73/72 |
| Theorem 1.1 | weighted bi-wheels of Chlebík and Chlebíková | 15 | 3/2 | 17/2 | 31 | 63/62 |

- **Theorem 1.3** replaces the equation gadget by a module with 10 vertices and 14 arcs
  ([`anc/parity_boundary.json`](anc/parity_boundary.json)).
- **Theorem 1.1** uses the weighted amplifiers that Chlebík and Chlebíková introduced for the symmetric problem:
  forced edges of matched pairs get weight 1 and wheel arcs weight 1/2. The equation is simulated by a module with
  three auxiliary vertices and 18 arcs
  ([`anc/half_contact_3aux_candidate.json`](anc/half_contact_3aux_candidate.json)), whose minimum unit cost for an
  honest profile is 17/2 if the equation is satisfied and 19/2 otherwise.
- Soundness reduces to finite properties of the module. A Hamiltonian path from the entry port to the exit port
  through the auxiliary vertices and exactly the contacts set to false exists if and only if the equation is
  satisfied. In the weighted case the module cannot be covered by two paths to its exit, one from its entry and one
  from a true contact.
- In the soundness analysis each violated cycle equation is charged to one of its endpoints, so that every variable
  is decoded from its own gadget. This also corrects two steps in the analysis of Karpinski, Lampis and Schmied
  (end of the introduction and Remark 6.4 of the paper). Both concern the presentation of their argument, and the
  lemma that replaces them applies verbatim to the matched pairs of their construction.

## What the theorems depend on

- Theorem 1.1 uses Theorem 5 of Chlebík and Chlebíková (J. Comb. Optim. 43 (2022)): for every sufficiently large k
  there is a bi-wheel with k contacts and 10k checkers on each cycle that is an amplifier for cycle weight 1/2 and
  matching weight 1. The published proof of that theorem is a sketch. The paper uses the theorem as published. The
  bound 117/116 of Chlebík and Chlebíková for the symmetric problem and the bound 111/110 of Nagda, Raghavan and
  Thakurta depend on the same theorem.
- Theorem 1.3 does not use it. It depends only on the unweighted bi-wheel amplifiers of Karpinski, Lampis and
  Schmied, which rest on the analysis of wheel amplifiers by Berman and Karpinski, and on Håstad's theorem.
- The proofs of both theorems are written out by hand for arbitrary multiplicities. The programs in `anc/` check
  the finite module properties and the arithmetic, and repeat the local soundness lemmas for bounded
  multiplicities. Remark 8.1 (no module with at most one auxiliary vertex has the parity property) is a statement
  proved by exhaustive enumeration.

## Related work

- Papadimitriou and Vempala (Combinatorica 2006): 117/116 for ATSP and 220/219 for the symmetric problem.
- Lampis (APPROX 2012): 185/184 for the symmetric problem.
- Karpinski, Lampis and Schmied ([arXiv:1303.6437](https://arxiv.org/abs/1303.6437)): 123/122 for the symmetric
  problem and 75/74 for ATSP.
- Chlebík and Chlebíková (COCOON 2019; J. Comb. Optim. 2022): weighted amplifiers and 117/116 for the symmetric
  problem. Their graphs are undirected.
- Nagda, Raghavan and Thakurta ([arXiv:2509.18057](https://arxiv.org/abs/2509.18057)): 111/110 for the symmetric
  problem, keeping the reduction of Chlebík and Chlebíková and replacing its equation gadget by one found with the
  AlphaEvolve agent. Their gadget is for the undirected reduction.

Bounds for the symmetric problem also hold for ATSP; the ones above are smaller than 75/74.

## Files

Read [paper.pdf](paper.pdf). To compile the source, with Tectonic installed,

    cd source
    tectonic main.tex

or run `pdflatex main.tex` twice (the bibliography is inside `main.tex`).

[`anc/README.md`](anc/README.md) lists the programs, the lemma each one checks, the commands and the expected
output. The quick ones need only the Python 3 standard library and run in under a second each:

    cd anc
    python3 check_weighted_module.py
    python3 check_half_weight_pair.py
    python3 check_weighted_transfer_arithmetic.py
    python3 check_weighted_small_host.py
    python3 check_final.py
    python3 check_tables.py
    python3 checker_pair.py
    python3 check_parity_ham.py parity_boundary.json

Three further checks need a C compiler or Google OR-Tools. `SHA256SUMS` records the distributed files.

## Licence

The paper and text are under CC BY 4.0 (see [`LICENSE-papers.md`](LICENSE-papers.md)); the programs in `anc/` are
under the MIT licence (see [`LICENSE`](LICENSE)).

## Citation

```bibtex
@misc{Guo2026ATSP6362,
  author = {Guo, Jizhou},
  title = {A 63/62 inapproximability bound for the asymmetric traveling salesman problem},
  year = {2026},
  month = oct,
  howpublished = {\url{https://github.com/aster2024/atsp-inapproximability}},
  note = {Preprint, 10 October 2026}
}
```
