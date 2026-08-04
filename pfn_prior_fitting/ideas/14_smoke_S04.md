# Step 15 — Smoke test S04 (M2, the decisive test). **M2 works. The
# pre-registered positive branch fired.**

Script: `smoke/s04_m2_retrain.py`. 3 arms × 2 seeds = 6 *unconditional* PFNs,
identical architecture (d=192, 8 layers), 25k steps each, identical optimizer
and seeds; the **only** difference is the θ-law used to generate pretraining
data. Evaluated on 800 held-out corpus datasets and 800 held-out **broad**
datasets. `π*` = NPMLE fit from S03's θ-conditional model on 600 fit-corpus
datasets over the K=64 grid, resampled with a uniform kernel of half the grid
spacing (0.125/0.25/0.25).

## 15.1 The table

| arm | pretraining θ-law | corpus NLL | ±seed | corpus ACC | broad NLL | broad ACC |
|---|---|---|---|---|---|---|
| **A** | `π₀` broad ("TabPFN as shipped") | 0.5304 | 0.0001 | 0.7252 | **0.5322** | **0.7137** |
| **B** | `π*` NPMLE fit (**ours**) | **0.5185** | 0.0001 | **0.7331** | 0.5352 | 0.7119 |
| **C** | true corpus law (oracle) | **0.5180** | 0.0002 | **0.7352** | 0.5364 | 0.7127 |

Paired, per-dataset, seed-averaged:

| comparison | Δ nats/row | win rate | median Δ |
|---|---|---|---|
| B vs A, **corpus** | **+0.0119** | **59.8%** | +0.0069 |
| C vs A, corpus | +0.0124 | 59.8% | +0.0099 |
| C vs B, corpus | +0.0005 | 49.1% | −0.0002 |
| B vs A, **broad** | **−0.0030** | 42.1% | −0.0037 |
| C vs A, broad | −0.0041 | 42.0% | −0.0063 |

## 15.2 Reading

**(i) The decision rule from §14.4 fired on the positive branch: `A > B ≈ C`.**
`B` recovers **96%** (0.0119 / 0.0124) of the oracle's on-corpus improvement,
while never seeing the true θ-law — only 600 datasets and forward passes through
a θ-conditional network. `C vs B` is +0.0005 with a 49.1% win rate, i.e.
statistically indistinguishable from the oracle.

**(ii) T-E does not fire here, unlike M1.** Seed SD of the arm mean is
0.0001–0.0002 nats/row against an effect of 0.0119 — the effect is 60–120× seed
noise. The paired win rate is 59.8% over 800 datasets; a sign test gives
`z ≈ 5.5`. **This is the first result in the whole project that survives a
paired per-dataset test.** Contrast M1 (S02: 47.8%, S03: 52%), which does not.
This is decisive evidence that the contribution belongs in M2 and not in M1, and
retroactively confirms the §14.2(ii) `O(1/n)` argument.

**(iii) The cost is real and must be reported, not buried.** Fitting the prior
is *specialization*. Off-corpus, `B` is **worse** than `A` by 0.0030 nats/row
(42.1% win rate). The honest statement:

> `π*` buys **96%** of the oracle's on-corpus gain (+0.0119) at **73%** of the
> oracle's off-corpus cost (−0.0030 vs −0.0041).

So the trade is roughly 4 : 1 in favour, and `π*` sits on a better point of the
trade-off curve than the oracle θ-law does. That is a defensible and *falsifiable*
claim, and it is the one the paper should make. Any claim of a free lunch is
false and the data says so.

**(iv) Accuracy moves too**, so the gain is not a pure calibration artefact:
corpus 0.7252 → 0.7331 (+0.79 pts); broad 0.7137 → 0.7119 (−0.18 pts).

## 15.3 What is still not established — the honest list

1. **The corpus is synthetic and inside the generator family.** The "real data"
   here is drawn from the *same* `gen_theta` family, only with a different
   θ-law. The whole point of the paper is real tabular data, whose law is
   **outside** any synthetic family. The NPMLE will then be fitting a
   projection, not a recovery. This is the single largest untested gap and it
   is the main experiment.
2. Scale: n=64 rows, d≤8, 2 classes, 4.5M-parameter network, K=64 grid.
   TabPFN-v2 is 10k rows × 500 features. Whether the gain survives that ratio is
   unknown; §14.2(ii) predicts M1 shrinks like 1/n but says nothing about M2.
3. **Ob1 (Real-TabPFN-2.5 fine-tuning) is still untested and is still the
   strongest objection.** Fine-tuning on the same real corpus is the baseline
   that could dominate. It must be run head-to-head, and the comparison must be
   at matched real-data budget.
4. The kernel half-width in the `π*` resampler is an unjustified hyperparameter.
   With half-width → 0 the retrained model sees only 64 distinct θ; with
   half-width → grid spacing it approaches a continuous fit. The sensitivity is
   unmeasured.
5. O1's detection AUC (S02) has not been re-measured in the continuous-θ setting
   nor with the y-shuffled control that separates covariate novelty from
   conditional-model misfit.

## 15.4 Status of the idea

All four cheap kill tests from `math/01_setup.md` §8 are resolved:

| threat | result |
|---|---|
| T-A (score dominated by network error) | **survived** — 0.703 θ-recovery, σ/k spread 0.134 |
| T-B (θ ignored) | **survived** — k-spread 7% of base loss |
| T-D (NPMLE collapse) | **survived** — TV 0.04 recovery, `e^H` ≈ 5 of 64 |
| T-E (inside seed noise) | **fires for M1, does not fire for M2** — M1 demoted |
| Warning 2.3 (order incoherence) | measurable, 3.7× smaller than the signal |

The idea has a validated formal core, a demoted-and-documented false branch, and
one effect that survives a paired test at 60% win rate and 100× seed noise.

**Step 16: write the full paper claim + implementation plan, then HALT the relay
and ask for approval before committing 1 GPU to the real-data main experiment.**
