/* Independent exhaustive local soundness check for a directed parity module.
 *
 * Nodes: 0=sj 1=tj, aux blocks 2..(2+NAUX-1) (single vertices),
 * then for each contact c in {X,Y,Z}: Cl and Cr.
 * Module arcs are given in block notation: an arc into contact C lands on Cl,
 * an arc out of contact C leaves from Cr.
 * Per contact: forced multiplicities fm (Cl->Cr), fp (Cr->Cl), not both 0;
 * wheel arcs a (into Cr), b (out of Cl) determined by balance, must be >= 0.
 * Portals: ks = out(sj) >= 1, kt = in(tj) >= 1 (balance).
 * Local connectivity (necessary for a global tour): every local node must be
 * connected (undirected, via used arcs) to OUTSIDE, where OUTSIDE touches sj,
 * tj, Cr if a>0, Cl if b>0.
 * Unit cost U = out(sj)+sum out(aux) + sum_C [b + fm + outmod(Cr) + fp].
 * D = U - base, base = 1 + NAUX + 6.
 * owed = min_q [xor(q) != 1] + sum_C [q_C != (a>0)] + [q_C != (b>0)].
 * Claim to test: owed <= D for every configuration.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef GADGET
#define GADGET 1
#endif

/* block ids: 's'=sj, 't'=tj, aux letters, contacts X Y Z */
#if GADGET == 1
#define NAUX 2
static const char *AUXN = "AB";
static const char *ARCS[][2] = {
  {"s","B"},{"s","Z"},{"A","B"},{"A","X"},{"A","t"},{"B","A"},{"B","Y"},
  {"X","A"},{"X","Y"},{"X","Z"},{"Y","B"},{"Y","X"},{"Z","Y"},{"Z","t"}};
#define NARC 14
#elif GADGET == 3
/* NEGATIVE CONTROL: new gadget plus one extra arc X->t (makes F={X} Hamiltonian: s B A X t) */
#define NAUX 2
static const char *AUXN = "AB";
static const char *ARCS[][2] = {
  {"s","B"},{"s","Z"},{"A","B"},{"A","X"},{"A","t"},{"B","A"},{"B","Y"},
  {"X","A"},{"X","Y"},{"X","Z"},{"Y","B"},{"Y","X"},{"Z","Y"},{"Z","t"},{"X","t"}};
#define NARC 15
#else
/* Reference module with 11 vertices, reconstructed from the walks described in
   KLS, Section 6 (not claimed to be identical to their gadget; not used in the paper):
   sj->e_i, e_i->tj, e1->x, x->e2, e2->y, y->e3, e3->z, z->e1,
   e2->e1, e1->e3, e3->e2 (auxiliary triangle, from Case x+y+z=3,2 walks) */
#define NAUX 3
static const char *AUXN = "123";
static const char *ARCS[][2] = {
  {"s","1"},{"s","2"},{"s","3"},{"1","t"},{"2","t"},{"3","t"},
  {"1","X"},{"X","2"},{"2","Y"},{"Y","3"},{"3","Z"},{"Z","1"},
  {"2","1"},{"1","3"},{"3","2"}};
#define NARC 15
#endif

#define NNODE (2 + NAUX + 6)
#define OUTSIDE NNODE

static int src[NARC], dst[NARC];

static int block_src(const char *b) {
  if (b[0] == 's') return 0;
  if (b[0] == 't') { fprintf(stderr, "t as source\n"); exit(1); }
  const char *p = strchr(AUXN, b[0]);
  if (p) return 2 + (int)(p - AUXN);
  int c = b[0] - 'X';
  return 2 + NAUX + 2 * c + 1; /* Cr */
}
static int block_dst(const char *b) {
  if (b[0] == 't') return 1;
  if (b[0] == 's') { fprintf(stderr, "s as target\n"); exit(1); }
  const char *p = strchr(AUXN, b[0]);
  if (p) return 2 + (int)(p - AUXN);
  int c = b[0] - 'X';
  return 2 + NAUX + 2 * c; /* Cl */
}

static int par[NNODE + 1];
static int fnd(int x) { while (par[x] != x) x = par[x] = par[par[x]]; return x; }
static void uni(int a, int b) { a = fnd(a); b = fnd(b); if (a != b) par[a] = b; }

int main(int argc, char **argv) {
  int M = argc > 1 ? atoi(argv[1]) : 2;   /* max module-arc multiplicity */
  int F = argc > 2 ? atoi(argv[2]) : 2;   /* max forced multiplicity */
  for (int i = 0; i < NARC; i++) { src[i] = block_src(ARCS[i][0]); dst[i] = block_dst(ARCS[i][1]); }
  int base = 1 + NAUX + 6;
  long long total = 0, viol = 0, tight = 0, zeroD = 0;
  int minD = 1 << 30;
  int mult[NARC];
  memset(mult, 0, sizeof mult);
  long long hist_owed_minus_D[8] = {0};
  for (;;) {
    int outd[NNODE], ind[NNODE];
    memset(outd, 0, sizeof outd); memset(ind, 0, sizeof ind);
    for (int i = 0; i < NARC; i++) { outd[src[i]] += mult[i]; ind[dst[i]] += mult[i]; }
    int ok = outd[0] >= 1 && ind[1] >= 1;
    for (int k = 0; k < NAUX && ok; k++) if (outd[2 + k] != ind[2 + k]) ok = 0;
    if (ok) {
      /* per-contact options */
      int nopt[3]; int opt[3][64][4]; /* fm fp a b */
      for (int c = 0; c < 3; c++) {
        int cl = 2 + NAUX + 2 * c, cr = cl + 1;
        int min_ = ind[cl], mout = outd[cr];
        nopt[c] = 0;
        for (int fm = 0; fm <= F; fm++) for (int fp = 0; fp <= F; fp++) {
          if (fm + fp == 0) continue;
          int a = mout + fp - fm, b = min_ + fp - fm;
          if (a < 0 || b < 0) continue;
          opt[c][nopt[c]][0] = fm; opt[c][nopt[c]][1] = fp;
          opt[c][nopt[c]][2] = a; opt[c][nopt[c]][3] = b; nopt[c]++;
        }
      }
      for (int i0 = 0; i0 < nopt[0]; i0++)
      for (int i1 = 0; i1 < nopt[1]; i1++)
      for (int i2 = 0; i2 < nopt[2]; i2++) {
        int *o[3] = {opt[0][i0], opt[1][i1], opt[2][i2]};
        for (int v = 0; v <= NNODE; v++) par[v] = v;
        for (int i = 0; i < NARC; i++) if (mult[i]) uni(src[i], dst[i]);
        uni(0, OUTSIDE); uni(1, OUTSIDE);
        int U = outd[0];
        for (int k = 0; k < NAUX; k++) U += outd[2 + k];
        for (int c = 0; c < 3; c++) {
          int cl = 2 + NAUX + 2 * c, cr = cl + 1;
          uni(cl, cr);
          if (o[c][2] > 0) uni(cr, OUTSIDE);
          if (o[c][3] > 0) uni(cl, OUTSIDE);
          U += o[c][3] + o[c][0] + outd[cr] + o[c][1];
        }
        int conn = 1;
        for (int v = 0; v < NNODE; v++) if (fnd(v) != fnd(OUTSIDE)) { conn = 0; break; }
        if (!conn) continue;
        int D = U - base;
        int best = 99;
        for (int q = 0; q < 8; q++) {
          int s = 0, x = 0;
          for (int c = 0; c < 3; c++) {
            int qc = (q >> c) & 1; x ^= qc;
            s += (qc != (o[c][2] > 0)) + (qc != (o[c][3] > 0));
          }
          s += (x != 1);
          if (s < best) best = s;
        }
        total++;
        if (D < minD) minD = D;
        if (D == 0) zeroD++;
        if (best > D) { viol++; if (viol <= 10) {
            printf("VIOLATION owed=%d D=%d mult=", best, D);
            for (int i = 0; i < NARC; i++) printf("%d", mult[i]);
            for (int c = 0; c < 3; c++) printf(" C%d(fm=%d fp=%d a=%d b=%d)", c, o[c][0], o[c][1], o[c][2], o[c][3]);
            printf("\n"); } }
        if (best == D) tight++;
        int d = D - best; if (d >= 0 && d < 8) hist_owed_minus_D[d]++;
      }
    }
    int i = 0;
    while (i < NARC && mult[i] == M) { mult[i] = 0; i++; }
    if (i == NARC) break;
    mult[i]++;
  }
  printf("GADGET=%d M=%d F=%d base=%d configs=%lld minD=%d zeroD=%lld tight=%lld violations=%lld\n",
         GADGET, M, F, base, total, minD, zeroD, tight, viol);
  printf("slack histogram D-owed (0..7):");
  for (int d = 0; d < 8; d++) printf(" %lld", hist_owed_minus_D[d]);
  printf("\n");
  return viol ? 1 : 0;
}
