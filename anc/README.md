# Ancillary files for "A 63/62 inapproximability bound for the asymmetric traveling salesman problem"

These files check every finite statement used in the paper. They also give
independent bounded-multiplicity checks of the local soundness lemmas, which
the paper proves by hand for all multiplicities. The theorems do not depend on
any of the computations. Every result the programs confirm is also proved in
the text.

The paper has two settings (Table 1 of the paper): the **weighted setting**
(Theorem 1.1, bound 63/62; source of Chlebik and Chlebikova, cycle weight
p_c = 1/2) and the **unweighted setting** (Theorem 1.3, bound 73/72; source
of Karpinski, Lampis and Schmied, p_c = 1).

## Notation

The programs use the block notation of the paper:

- `s` and `t` are the ports `s_j` and `t_j` of one parity module.
- `A`, `B` (unweighted) and `A`, `B`, `C` (weighted) are the auxiliary vertices.
- `X`, `Y`, `Z` are the contact blocks. An arc into a block `c` ends at
  `c^l`; an arc out of `c` starts at `c^r`.

The weighted programs scale all costs by 2, so that every cost is an integer
(for example, the weighted module baseline 17/2 is printed as 17).

## Files

| file | what it checks (paper reference) | dependencies | provenance |
|---|---|---|---|
| `half_contact_3aux_candidate.json` | the 18 module arcs of the weighted module (Table 3), machine-readable | none | output of the SAT search |
| `check_weighted_module.py` | weighted module: Hamiltonian port paths for all 8 profiles, five in total (Lemma 4.2(a)); all 720 candidate covers of the two-start property (Lemma 4.2(b)); exact minimum unit cost 17/2 or 19/2 of every honest profile; every walk of Table 5 and the connector walks (Lemma 5.1) arc by arc | Python 3 standard library | written for the weighted construction; helper inlined for this paper |
| `check_half_weight_pair.py` | Lemma 6.3 for p_c = 1/2 over all 296 balanced, connected local configurations with all multiplicities <= 4 | Python 3 standard library | written for the weighted construction |
| `check_weighted_transfer_arithmetic.py` | exact rational arithmetic of Section 7 (weighted): baseline 31 = 15 * 3/2 + 17/2, limit 63/62, explicit ratio 78750016000/77500137501 > 64/63 | Python 3 standard library | written for the weighted construction |
| `check_weighted_small_host.py` | end-to-end test of the completeness construction of Lemma 5.1 (weighted) on a 35-vertex host: balance, coverage, forced edges and portals used, weak connectivity, exact cost 1731/50 | Python 3 standard library | written for the weighted construction |
| `check_weighted_decoding.py` | Lemma 6.6 (module decoding) in the weighted setting for bounded multiplicities: CP-SAT minimum of 2(D_j - owed_j) over local configurations of the module with its three contacts, all multiplicities <= 2, 3, 5 | Python 3, OR-Tools | written during the independent review of the weighted proof |
| `parity_boundary.json` | the 14 module arcs of the unweighted module (Table 2), machine-readable | none | output of the SAT search |
| `check_final.py` | unweighted module: Hamiltonian port paths for all 8 profiles (Lemma 4.1); exact minimum unit cost 9 or 10 of every honest profile (Table 4); connector walks; exact rational arithmetic of Section 7, including the limit 73/72 and the explicit ratio 91250014500/90000225001 > 75/74 | Python 3 standard library | written during the search |
| `check_parity_ham.py` | a second enumeration of the Hamiltonian port paths of an arc set given as JSON (Lemma 4.1) | Python 3 standard library | written during the search |
| `check_tables.py` | the following, arc by arc: Table 2 equals the JSON arc set; the Hamiltonian port paths are exactly those listed in the proof of Lemma 4.1; every walk of Table 4 and the three connector walks of Lemma 5.1 have the stated cost | Python 3 standard library | written for the paper |
| `checker_pair.py` | Lemma 6.3 for p_c = 1 over all balanced, connected local configurations with wheel multiplicities <= 4 and forced multiplicities <= 3; the minimum cost 5 in Remark 6.4 | Python 3 standard library | independent audit |
| `local_brute.c` | Lemma 6.6 for the unweighted module by exhaustive enumeration: module-arc multiplicities <= M, forced contact multiplicities <= F, wheel multiplicities determined by balance, every local vertex connected to the outside; checks `min_q owed <= D` | C compiler only | independent audit |
| `check2_decoder.py` with `gadget_local.py` | Lemma 6.6 for the unweighted module once more. CP-SAT computes the exact minimum of `D` for each wheel-multiplicity vector and compares it with `min owed`. It also checks the specific decoding rule from the proof of Lemma 6.6 on all 729 feasible combinations of orientation classes and usage bits | Python 3 and Google OR-Tools (`pip install ortools`) | independent audit |
| `check_small_modules.py` | Remark 8.1: no arc set with 0 or 1 auxiliary vertices has the parity property (exhaustive over 2^13 and 2^21 arc sets). Includes a positive and a negative control | Python 3 standard library | written for the paper |
| `SHA256SUMS` | SHA-256 checksums of all other files in this directory (`sha256sum -c SHA256SUMS`) | `sha256sum` | generated |

"Written during the search" and "independent audit" refer to programs that
were written separately, from the written specification of the gadget, without
sharing code.

## Commands

Run all commands from this directory. Times are single-core wall-clock times
measured with Python 3.10 and gcc 13 on a Linux server.

### W1. Weighted module (Lemma 4.2, Table 5, Lemma 5.1): about 0.1 s

```
python3 check_weighted_module.py
```

Expected output (one line of JSON):

```
{"arcs": 18, "baseline_per_equation": 31, "connector_unit_cost_scaled": {"X": 5, "Y": 5, "Z": 5}, "forbidden_two_start_covers_checked": 720, "hamiltonian_paths": {"X": [], "XY": ["sYCBAXt"], "XYZ": [], "XZ": ["sXCBAZt", "sZCBAXt"], "Y": [], "YZ": ["sYCBAZt"], "Z": [], "none": ["sABCt"]}, "hamiltonian_paths_total": 5, "limit_ratio": "63/62", "module_profiles": {"X": {"portal_pairs": 2, "scaled_unit_cost": 19}, "XY": {"portal_pairs": 1, "scaled_unit_cost": 17}, "XYZ": {"portal_pairs": 2, "scaled_unit_cost": 19}, "XZ": {"portal_pairs": 1, "scaled_unit_cost": 17}, "Y": {"portal_pairs": 2, "scaled_unit_cost": 19}, "YZ": {"portal_pairs": 1, "scaled_unit_cost": 17}, "Z": {"portal_pairs": 2, "scaled_unit_cost": 19}, "none": {"portal_pairs": 1, "scaled_unit_cost": 17}}, "result": "PASS", "table_walks": {"X": {"portal_pairs": 2, "scaled_unit_cost": 19}, "XY": {"portal_pairs": 1, "scaled_unit_cost": 17}, "XYZ": {"portal_pairs": 2, "scaled_unit_cost": 19}, "XZ": {"portal_pairs": 1, "scaled_unit_cost": 17}, "Y": {"portal_pairs": 2, "scaled_unit_cost": 19}, "YZ": {"portal_pairs": 1, "scaled_unit_cost": 17}, "Z": {"portal_pairs": 2, "scaled_unit_cost": 19}, "none": {"portal_pairs": 1, "scaled_unit_cost": 17}}}
```

In `module_profiles`, each false set maps to the exact minimum scaled unit
cost of an honest traversal (17 = 2 * 17/2, 19 = 2 * 19/2) and the number of
portal pairs of an optimal traversal; `table_walks` gives the same data for
the walks listed in Table 5 of the paper. `connector_unit_cost_scaled` is
5 = 2 * 5/2 for every contact.

### W2. Matched pairs, p_c = 1/2 (Lemma 6.3): about 0.1 s

```
python3 check_half_weight_pair.py
```

Expected output:

```
{'result': 'PASS', 'profiles': 296, 'tight': 10, 'scaled_baseline': 3, 'weights_scaled': {'wheel': 1, 'forced_match': 2}}
```

### W3. Arithmetic of Section 7, weighted setting: about 0.1 s

```
python3 check_weighted_transfer_arithmetic.py
```

Expected output:

```
{'result': 'PASS', 'matching_per_equation': 15, 'baseline': '31', 'source_gap': '1/2', 'limit_ratio': '63/62', 'explicit_target': '64/63', 'explicit_ratio': '78750016000/77500137501', 'yes_coefficient': '77500137501/2500000000', 'no_coefficient': '2460938/78125', 'parameters': {'epsilon': '1/100000', 'delta': '1/100000', 'lambda': '1/100000', 'forced_path_length': 10000000}}
```

### W4. End-to-end completeness test, weighted setting (Lemma 5.1): about 0.1 s

```
python3 check_weighted_small_host.py
```

The host has three bi-wheels, each cycle with two checkers and one contact
(gap 2 instead of 10, which does not change the local structure), and two
parity equations; one of them is violated by the chosen consistent
assignment. The expected cost is 6 * 3/2 (pairs) + 17/2 + 19/2 (modules)
+ 3 * 5/2 (connectors) + 12 * lambda (6 portal pairs) = 1731/50 for
lambda = 1/100. Expected output:

```
{'result': 'PASS', 'vertices': 35, 'available_arcs': 82, 'used_arc_types': 46, 'balanced_connected': True, 'source_ternary_violations': 1, 'cost': '1731/50', 'bound': '1731/50'}
```

### W5. Module decoding, weighted setting, via CP-SAT (Lemma 6.6), optional: about 3 s

This check requires OR-Tools.

```
python3 check_weighted_decoding.py
```

Expected output: three lines with `'min(D2-owed2)': 0` (for UB = 2, 3, 5), each
followed by a witness configuration, and a final line `{'result': 'PASS'}`.

### U1. Main certificate (Lemma 4.1, Table 4, Section 7): about 0.2 s

```
python3 check_final.py
```

Expected output (one line of JSON):

```
{"baseline": 36, "explicit_parameters": {"delta": "1/100000", "epsilon": "1/100000", "forced_path_length": 10000000, "lambda": "1/100000"}, "explicit_ratio": "91250014500/90000225001", "limit_ratio": "73/72", "profiles": {"X": [0, 10], "XY": [1, 9], "XYZ": [0, 10], "XZ": [1, 9], "Y": [0, 10], "YZ": [1, 9], "Z": [0, 10], "none": [1, 9]}, "result": "PASS", "source_gap": "1/2"}
```

In `profiles`, each false set `F` maps to `[number of Hamiltonian port paths,
minimum unit cost]`.

### U2. Independent Hamiltonian-path enumeration (Lemma 4.1): about 0.2 s

This program needs the JSON file as its argument.

```
python3 check_parity_ham.py parity_boundary.json
```

Expected output:

```
{"arc_count": 14, "forbidden_split_covers": {}, "hamiltonian_paths": {"X": 0, "XY": 1, "XYZ": 0, "XZ": 1, "Y": 0, "YZ": 1, "Z": 0, "none": 1}, "result": "PASS"}
```

### U3. Tables of the paper (Tables 2 and 4, Lemma 4.1, Lemma 5.1): about 0.1 s

```
python3 check_tables.py parity_boundary.json
```

Expected output:

```
{"arcs_unused_by_all_walks": [["X", "Y"]], "connector_costs": {"X": 6, "Y": 6, "Z": 3}, "hamiltonian_paths": {"X": [], "XY": ["sBYXAt"], "XYZ": [], "XZ": ["sBAXZt"], "Y": [], "YZ": ["sZYBAt"], "Z": [], "none": ["sBAt"]}, "result": "PASS", "walk_unit_cost_and_portal_pairs": {"X": [10, 1], "XY": [9, 1], "XYZ": [10, 1], "XZ": [9, 1], "Y": [10, 1], "YZ": [9, 1], "Z": [10, 2], "none": [9, 1]}}
```

The field `arcs_unused_by_all_walks` supports Remark 8.2: the arc X -> Y is
not needed for completeness.

### U4. Matched pairs, p_c = 1 (Lemma 6.3, Remark 6.4): about 0.1 s

```
python3 checker_pair.py
```

Expected output:

```
violations: [] 0
min cost when both honest with value 1: 5
PASS
```

### U5. Module decoding, exhaustive C enumeration (Lemma 6.6): about 45 s

```
gcc -O2 -o local_brute local_brute.c
./local_brute 2 3
```

The two arguments are M = 2 (maximum module-arc multiplicity) and F = 3
(maximum forced multiplicity). The program exits with status 0. Expected
output:

```
GADGET=1 M=2 F=3 base=9 configs=296978543 minD=0 zeroD=4 tight=119 violations=0
slack histogram D-owed (0..7): 119 467 1885 5569 14873 35580 76883 157577
```

`zeroD=4` means that exactly four configurations have `D = 0`. They are the
four honest traversals of satisfied equations, one for each even false set.

For a quicker run, `./local_brute 1 1` finishes in milliseconds and prints
`configs=14917 ... violations=0`.

Negative control. The module plus the extra arc X -> t has a Hamiltonian port
path for F = {X}, so it must fail:

```
gcc -O2 -DGADGET=3 -o local_brute_neg local_brute.c
./local_brute_neg 1 1
```

This prints two `VIOLATION ...` lines (one for F = {X} and one for
F = {X, Y, Z}), then a summary line ending in `violations=2` and the slack
histogram, and exits with status 1.

A reference variant, compiled with `-DGADGET=0`, runs the same check on the
11-vertex KLS module with baseline 10. Its arcs are reconstructed from the
walks described in the text of KLS, Section 6. With `2 3` it reports
`configs=110259438 ... violations=0`. This variant is not used in the paper.

### U6. Module decoding via CP-SAT (Lemma 6.6), optional: about 3.5 min

This check requires OR-Tools.

```
python3 check2_decoder.py 1 1
```

Expected output: two JSON lines and no line starting with `VIOLATION`.

```
{"feasible": 64, "infeasible": 0, "tight": 35, "min_slack": 0, "worst": [[0, 0, 0, 0, 0, 0], 1, 1], "sec": ...}
{"feasible": 729, "tight": 91, "min_slack": 0, "worst": [[0, 0, 0, 0, 0, 0], ["LR", "LR", "LR"], 1, 1, [0, 0, 0]], "sec": ...}
```

The program also writes `check2_K1_K21.json` to the current directory.

The first argument K sets the range {0..K} of the wheel multiplicities in the
existence check. The second argument K2 sets the range {0..K2} used in the
check of the decoding rule. During the preparation of the paper the run
`python3 check2_decoder.py 3 2` was also completed. It took about 2.8 hours
and reported 4082 feasible wheel vectors and 10648 feasible rule cases, with
no violation.

### U7. Fewer auxiliary vertices (Remark 8.1): about 3 s

```
python3 check_small_modules.py
```

Expected output:

```
{"result": "PASS", "searches": [{"aux": [], "candidate_arcs": 13, "arc_sets": 8192, "with_parity_property": 0, "examples": []}, {"aux": ["A"], "candidate_arcs": 21, "arc_sets": 2097152, "with_parity_property": 0, "examples": []}], "positive_control_two_aux_restricted": {"candidate_arcs": 20, "with_parity_property": 12}}
```

## Scope of the computations

- Scripts W1, W3, W4 and U1-U3 check finite objects completely: the two
  modules, their 8 profiles, the walks, and the rational arithmetic.
- Scripts W2, W5 and U4-U6 check the local lemmas only for bounded
  multiplicities. The paper proves Lemmas 6.3, 6.5 and 6.6 by hand for all
  multiplicities. These scripts are consistency checks of those proofs.
- The source problems (Theorems 2.3 and 2.4 of the paper, due to Karpinski,
  Lampis and Schmied and to Chlebik and Chlebikova) and the forced-path
  normalization (Lemma 6.1) are proved or cited in the text. They are not
  checked by computer.
