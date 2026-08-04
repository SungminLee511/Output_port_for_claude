# Step 10 — Focused screen of the specific claim. **SURVIVES, and gets stronger.**

## 10.1 (c) SBI model criticism — the feared pre-emption. Real, but different.
It exists and is mature:
- Schmitt et al., *Detecting Model Misspecification in Amortized Bayesian
  Inference with Neural Networks* (2112.08866; extended 2406.03154): augments the
  training objective to impose probabilistic structure on a **summary-statistic**
  space and uses **MMD** to detect misspecification at test time.
- ICLR-2026 blogpost *Model Misspecification in SBI — Recent Advances and Open
  Challenges*: the community itself still lists this as open.
- 2601.22367 (generalized Bayes via NPE) recommends calibration and
  posterior-predictive diagnostics.

Differences that matter, stated precisely:
1. Target: SBI infers **parameters**; PFNs do **prediction**. Their diagnostic
   concerns the posterior over θ; ours concerns the predictive over y.
2. Statistic: theirs is MMD in a learned summary space and **requires modifying
   the training objective**. Ours is the prequential log-predictive sum, which
   requires **no modification of anything** — it is already computed by any PFN.
3. Use: theirs *detects*. Ours detects **and supplies the objective that fixes
   the prior**. Detection alone is a diagnostic paper (excluded by the user);
   the fix is the method.
Crucially, the SBI literature states the premise I need, in its own words:
*"prior misspecification is particularly consequential in amortized neural SBI
because the prior also serves as the training distribution"* — the argument is
accepted there and simply has not been carried into the PFN/tabular world.
This is a legitimate G2 transfer, not a rediscovery.

## 10.2 (b) Predicting when TabPFN fails — **a published negative result we can
build on.**
*Revisiting Metafeatures to Explain Model Differences on Tabular Data*
(2605.28418): dataset-level meta-feature predictors **fail to improve
meaningfully over a trivial baseline** in leave-one-dataset-out evaluation on the
51 TabArena datasets; "global meta-feature approaches are not robust enough".

This is close to ideal: the obvious approach to O1 has been tried and published
as a failure, which (i) proves a constituency cares, (ii) removes the "why not
just use meta-features" reviewer objection by citation, (iii) gives us a
baseline that we must beat and that is honest to beat, because our statistic is
**model-intrinsic** (it is the model's own likelihood under its own prior)
rather than dataset-extrinsic.

## 10.3 (a) and (d) — no hits. Prequential scoring of PFNs, and empirical-Bayes
fitting of a PFN prior, are unoccupied.

## 10.4 The construction that makes the bilevel problem exactly tractable

The remaining obstacle from Step 9 was Ob3 (naive empirical Bayes needs one
pretraining per prior update). It dissolves:

Let the synthetic prior family be `{p(D | θ)}` indexed by prior hyperparameters
`θ` (SCM depth, activation set, noise model, feature-type mixture, …).

1. **Train one θ-conditional PFN**, i.e. condition the network on `θ` as input,
   with `θ ~ π₀` broad. At the optimum its outputs are `p(y | x, D_{<i}, θ)`.
2. For real datasets `D₁..D_M` and a finite set `θ₁..θ_K`, compute
   `L[m,k] = exp( Σ_i log q(y_i | x_i, D_{<i}, θ_k) ) ≈ p(D_m | θ_k)`
   by prequential sums — pure forward passes, no gradients.
3. Fit the mixing distribution by maximum likelihood:
   `π* = argmax_{π ∈ Δ_K} Σ_m log Σ_k π_k L[m,k]`.
   This is the Kiefer–Wolfowitz **NPMLE of a mixing distribution**, and the
   objective is **concave in π** on the simplex — a convex program, solved
   exactly by EM or a simplex-constrained solver. No bilevel loop, no
   hypergradients, no retraining inside the loop.
4. Two deliverables from the same fit:
   - **Inference-time (zero training cost):** exact Bayesian model averaging,
     `p(y | x, D) = Σ_k w_k(D) · p(y | x, D, θ_k)` with
     `w_k(D) ∝ π*_k L_k(D)`. This is an identity, not an approximation, given
     step-1 optimality.
   - **Training-time (one retraining):** resample the synthetic prior from `π*`
     and retrain a standard unconditional PFN — a drop-in better TabPFN.
5. `w_k(D)` is directly interpretable ⇒ O2 (which prior components explain this
   dataset). `max_k L[m,k]` low ⇒ dataset outside the whole family ⇒ O1/O4
   abstention.

Every step above is exact given step-1 optimality; the only approximation in the
whole pipeline is "the trained network ≈ its Bayes-optimal target", which is
also the only approximation in TabPFN itself.

## 10.5 Threats, ranked, with the cheapest test first
1. **T-A (fatal if true): the prequential score is dominated by network error
   and order-incoherence rather than by prior misfit.** Test: on *synthetic*
   datasets with known θ, does `argmax_k L[m,k]` recover the true θ? Cheap,
   decisive, must be the first experiment.
2. **T-B: the θ-conditional PFN ignores θ.** Test: mutual information between θ
   and predictions; compare against per-θ specialist PFNs.
3. **T-C: fine-tuning on real data (Real-TabPFN-2.5) dominates.** Must be run as
   a baseline, not argued away.
4. **T-D: NPMLE collapses to a single atom**, i.e. one prior explains everything
   and the method reduces to "pick the best prior". Would still be publishable
   but much weaker. Test is free (inspect `π*`).
5. **T-E: gains are inside seed noise** on TabArena. Requires ≥3 seeds and
   per-dataset paired tests from the start.

## 10.6 Decision
Proceed to formal setup. Step 11 = `math/01_setup.md`: definitions, the exact
statements (PFN optimum, prequential identity, exchangeability/coherence
conditions, NPMLE concavity), and — critically — the precise conditions under
which step 4's identity holds, since that is where a natural-language argument
would be wrong.
