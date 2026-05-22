
---

## PHASE B (Workshop plan) — Cycle 263: B1 family extension

Extends h260 (Ala4 only) to Ala3, Ala5, Ala6 at the canonical c155
protocol. 5 train seeds + 8 paired eval seeds per peptide = 40 paired
evaluations each. Total wall: 1697 s on one A100.

  peptide |  rev_KL | state-dep_Q_KL | gated_KL | state-dep vs rev | gated vs rev
   Ala3   | 0.196   |  1.125         |  0.105   | -474.5%          | +46.6%
   Ala4   | 0.277   |  0.764         |  0.154   | -176.0%          | +44.5%   (h260)
   Ala5   | 0.835   |  1.144         |  0.491   |  -37.0%          | +41.2%
   Ala6   | 0.618   |  0.538         |  0.258   |  +12.9%          | +58.2%

State-dep Q (PH'26 reference): collapses on 3/4 peptides, severity
monotone with d (475->176->37->-13 across d=12,16,20,24). Possible
mechanism: smaller d makes it easier for the MLP Q(x) to over-fit and
collapse onto a single mode.

Gated J replicates canonical c155 headlines (46.6/44.5/41.2/58.2%) and
beats state-dep Q by 52-91% relative reduction on every peptide, all
p<1e-3 paired bootstrap.

Workshop paper updated: 4-peptide family table in workshop_paper.md
and workshop_main.tex, family figure (h263) added.

Files: code/h263_state_dep_baseline_family.py,
code/h263_family_figure.py,
code/results/h263_state_dep_baseline_family.json,
paper/figures/B1_external_baseline_family_h263.{png,pdf}.

Phase B-1 family extension DONE.
