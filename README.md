# Origami_Gen v3-gen — Reference recipe library renders

**Run date:** 2026-06-01 16:26 KST
**Branch:** `v3-gen` (off `v3` off `main`) —
GENERATION_PLAN.md complete (10/10 phases).

## Codebase separation

The generation work (Phases 1–10) is **cleanly separated** from the
original v3 audit pipeline. Module dependency is one-way:

- **Original v3 pipeline**: `parser`, `topology`, `folder`, `mesher`,
  `stitcher`, `mapper`, `dihedral`, `fillet`, `bumper`, `export`,
  shared `types/`, `constants.py`, `errors.py`, `pipeline/`, etc.
- **Generation code**: `recipe/`, `gemini/`, `corpus/generated/`.

`recipe/` and `gemini/` **import** the pipeline; the pipeline never
imports them. You can delete the whole `gemini/` directory and the
P1→P10 audit still passes 42/42 corpus cases.

The only integration point is `corpus/__init__.py` importing
`corpus.generated` so YAMLs dropped into that directory auto-register
into `audit.py --full`. The directory is empty by default; opt-in
additive.

## What's in this snapshot

25 recipe-library renders. Each case has 3 PNGs (`_main.png`,
`_bump.png`, `_hole.png`), all strict 4/3-colour-palette
(no anti-aliasing). Suffix `_t20260601_1626` on every file.

### Hand-authored (Phase 1) — 5 cases

| Case | Panels | Folds | Topology |
|---|---|---|---|
| `simple_l_bracket` | 4 | 3 | L-bracket + 2-cap stack |
| `u_bracket` | 5 | 4 | U + caps on both flanges |
| `channel_bracket` | 6 | 5 | main + 3 flanges + cap |
| `accessory_l_bracket` | 5 | 4 | L + 3-cap stack |
| `tab_plate_4` | 5 | 4 | main + 3 tabs + cap |

### Auto-generated from BracketSpecs (Phase 2) — 20 cases

`bracket_v01` … `bracket_v05` — L_right archetype.
`bracket_v06` … `bracket_v10` — L_bottom archetype.
`bracket_v11` … `bracket_v15` — U_caps archetype.
`bracket_v16` … `bracket_v20` — cross_caps archetype.

All 20 produced by `scripts/reverse_engineer_corpus.py` mapping
each `BracketSpec` (in
`src/origami_gen/corpus/mobis_bracket/bracket_variants.py`) to a
`BracketRecipe` via the new schema.

### Per-PNG legend

| File | Content |
|------|---------|
| `<case>_main_t…png` | white bg + black panels + RED/BLUE fold bands |
| `<case>_bump_t…png` | panel mask + YELLOW/GREEN bump regions |
| `<case>_hole_t…png` | panel mask + PURPLE outline carves + holes |

### Acceptance gate (all 25 cases)

- 0 schema-validation violations.
- 0 C1..C11 complexity-floor violations.
- 0 fold-edge clearance violations.
- All 3 PNG layers contain ONLY the legal RGB triples per SKILL §1.3
  (no anti-aliasing).
- Full P1→P5 pipeline at res 2.0 passes all §3 hard gates:
  `nm=0 orph=0 comp=1 inv=0 sliver=0`.

(See `tests/recipe/test_reference_library_passes.py` for the
automated acceptance test.)

## Prior snapshot archived

The previous v3-audit snapshot (`_t20260531_1916` suffix, 42-case
visualization × 3 res audit) is in `archive_v3_audit_20260531_1916/`
— 602 files preserved verbatim.

## Tooling shipped on `v3-gen`

| Module | Purpose | LOC |
|---|---|---|
| `recipe/schema.py` | Pydantic schema for `BracketRecipe` | 600 |
| `recipe/validate.py` | C1..C11 + clearance + dim validator | 920 |
| `recipe/render.py` | Pure-numpy deterministic renderer | 900 |
| `recipe/library/*.yaml` | 25 reference recipes | — |
| `gemini/client.py` | SDK wrapper + .env loader | 220 |
| `gemini/cache.py` | Prompt-hash response cache | 140 |
| `gemini/prompts.py` | System / user / correction / reviewer prompts | 280 |
| `gemini/recipe_author.py` | Track B (text → recipe) | 270 |
| `gemini/self_correct.py` | Phase-4 retry loop | 240 |
| `gemini/reviewer.py` | Track D (composite → 1–10 + critique) | 180 |
| `gemini/agent.py` | Track E (multi-turn agent, no UI) | 290 |
| `gemini/image_gen.py` | Imagen 4 + palette-snap | 240 |
| `corpus/generated/` | Auto-register dropped YAMLs | 45 |
| `scripts/generate_bracket.py` | CLI: from-yaml / sample-batch / from-photo | 270 |
| `scripts/agent_repl.py` | Conversational REPL | 130 |
| `scripts/reverse_engineer_corpus.py` | BracketSpec → YAML | 530 |
| `scripts/image_gen_experiment.py` | Phase 8 evaluation harness | 80 |
| `tests/recipe/*` | 41 recipe tests | — |
| `tests/gemini/*` | 38 Gemini tests (incl 1 live) | — |
| `Makefile` | `make generation-smoke` end-to-end | — |
| `.claude/GENERATION_PLAN.md` | 1389-line plan | — |
| `.env` / `.env.example` | Gemini API config (key gitignored) | — |

Branch: https://github.com/voltwin-dev/Origami_Gen/tree/v3-gen
PR-ready at: https://github.com/voltwin-dev/Origami_Gen/pull/new/v3-gen
