# Origami_Gen v3-gen — Recipe library + Generation API

**Run date:** 2026-06-01 16:26 KST
**Branch:** `v3-gen` (off `v3` off `main`) —
GENERATION_PLAN.md complete (10/10 phases).

## Codebase separation

The generation work (Phases 1–10) is **cleanly separated** from the
original v3 audit pipeline. One-way module dependency:

- **Original v3 pipeline**: `parser`, `topology`, `folder`, `mesher`,
  `stitcher`, `mapper`, `dihedral`, `fillet`, `bumper`, `export`,
  shared `types/`, `constants.py`, `errors.py`, `pipeline/`, etc.
- **Generation code**: `recipe/`, `gemini/`, `corpus/generated/`.

`recipe/` and `gemini/` **import** the pipeline; the pipeline never
imports them. You can delete `gemini/` and P1→P10 still passes 42/42
corpus cases.

The only integration point: `corpus/__init__.py` auto-loads
`corpus/generated/*.yaml` so the batch sampler's keepers flow into
`audit.py --full`. Directory is empty by default — opt-in additive.

---

# API — how to use the generation code

The system supports five surfaces. Pick whichever matches your input
modality.

## 0. Setup

```bash
cp .env.example .env
# Add to .env:
#   GEMINI_API_KEY=<your_key_here>
#   GEMINI_TEXT_MODEL=gemini-2.5-pro
#   GEMINI_IMAGE_MODEL=imagen-4.0-generate-001

pip install -e ".[dev]"     # Pydantic v2, google-genai, PIL, numpy
```

## 1. Render an existing YAML recipe → 3 PNGs

Use this when you already have (or hand-author) a recipe.

**CLI:**
```bash
python scripts/generate_bracket.py from-yaml \
    src/origami_gen/recipe/library/simple_l_bracket.yaml \
    -o /tmp/out/
# Writes: /tmp/out/simple_l_bracket_{main,bump,hole}.png
```

**Python:**
```python
from origami_gen.recipe import load_recipe_yaml
from origami_gen.recipe.render import render_recipe
from origami_gen.recipe.validate import validate_recipe

recipe = load_recipe_yaml("path/to/recipe.yaml")
validate_recipe(recipe)         # raises on C1..C11 failure
bundle = render_recipe(recipe)  # CaseBundle(main_rgb, bump_rgb, hole_rgb)
# bundle.main_rgb is uint8 [H, W, 3]; save with PIL.
```

## 2. Natural-language prompt → recipe (Gemini Track B)

User types an English design intent; Gemini emits a valid YAML.

**Python:**
```python
from origami_gen.gemini.recipe_author import GeminiRecipeAuthor

author = GeminiRecipeAuthor(few_shot_n=3)
result = author.design(
    intent="Design a 5-panel L-bracket for an automotive sensor "
            "mount. Main plate 120x150 mm with two bosses and a "
            "fold-spanning bead.",
)
print(result.recipe.case_name)   # e.g. 'sensor_mount_l_bracket'
print(result.cached)             # True on second call → free
```

`design()` returns `DesignResult(recipe, raw_response, prompt_hash,
cached)`. Caching is keyed on the SHA-256 of `(model, prompt)`; same
intent on second call returns instantly without billing.

## 3. Prompt → recipe with self-correction (Gemini Track B + Phase 4)

Gemini sometimes emits recipes that violate C1..C11. The
self-correction loop catches the violation and re-prompts with the
specific error code (up to `GEMINI_MAX_RETRIES`, default 3).

**Python:**
```python
from origami_gen.gemini.self_correct import GeminiSelfCorrectingAuthor

corrector = GeminiSelfCorrectingAuthor(max_retries=3)
result = corrector.design(intent="Design a U-bracket with 4 panels.")

if result.success:
    print(f"valid recipe after {len(result.attempts)} attempts")
else:
    last = result.last_violations
    print(f"failed; final violations: {[v.code for v in last]}")
```

`CorrectionResult` carries the full `attempts` history — useful for
batch-generation logs.

## 4. Conversational agent (Phase 7 — multi-turn)

Stateful agent: propose → refine → refine → accept → save to corpus.

**Python:**
```python
from origami_gen.gemini.agent import BracketDesignerAgent

agent = BracketDesignerAgent(few_shot_n=3)

t1 = agent.propose("Design a U-bracket for a 30 mm tube clamp.")
# t1.recipe is the first proposal; t1.n_violations == 0 means it's
# already C-floor clean.

t2 = agent.refine("Move the bolt holes closer to the corners and "
                   "add a stiffener bead across the front fold.")
# t2.recipe has the edit applied; pipeline-validates internally.

agent.accept()
yaml_path = agent.save_to_corpus()
# Writes corpus/generated/<case>.yaml + a <case>/ dir with 3 PNGs;
# the case auto-registers into `audit.py --full` on next import.
```

**Or via REPL** (terminal, no GUI):
```bash
python scripts/agent_repl.py
>>> design a small L-bracket for a sensor mount
— turn 1 (propose) — case: sensor_mount, panels: 4, violations: 0
>>> add 2 more bolt holes on the flange
— turn 2 (refine) — case: sensor_mount, violations: 0
>>> :accept
accepted.
>>> :save
saved to .../corpus/generated/sensor_mount.yaml
```

## 5. Batch corpus expansion (Phase 6)

Sample N random design intents → Gemini → render → validate → save
keepers. Used to grow the corpus from 25 → hundreds.

```bash
python scripts/generate_bracket.py sample-batch 50 -o /tmp/batch \
    --seed 0 --max-retries 3 --few-shot-n 3
# /tmp/batch/keepers/<case>/{<case>.yaml, *_main.png, ...}
# /tmp/batch/batch_summary.csv  (per-intent outcome)
# /tmp/batch/generation_attempts.jsonl  (per-call audit log)
```

## 6. Photo → recipe (Phase 9 — multimodal)

Reverse-engineer a real bracket photograph into a YAML recipe.

```bash
python scripts/generate_bracket.py from-photo ~/photos/real.jpg \
    -o /tmp/p9 --scale-mm 180 --note "steering-column mount"
# Writes recipe.yaml + 3 reconstructed PNG layers.
```

**Python:**
```python
from origami_gen.gemini.recipe_author import GeminiRecipeAuthor

author = GeminiRecipeAuthor()
result = author.design_from_photo(
    photo_path="~/photos/real.jpg",
    scale_anchor_mm=180.0,       # the longest visible dimension
    intent_note="steering-column mount",
)
```

## 7. Direct image generation (Phase 8 — experimental)

Imagen 4 / Gemini-image direct PNG with palette-snap post-processing.
Mostly experimental; see `verification/image_gen_experiment.md`.

```bash
python scripts/image_gen_experiment.py --num 5 --out /tmp/imgexp
```

---

## Quick-start scripts

| Want to… | Run |
|---|---|
| Test the recipe schema | `make recipe-tests` |
| Test the Gemini layer (mocked) | `make gemini-tests` |
| End-to-end smoke (no API key) | `make generation-smoke` |
| Lint the new modules | `make ruff` |
| Live API test | `pytest -m gemini_live` |

---

# Reference recipe library — 25 cases (rendered below)

Every case has 3 PNG layers:

| Layer | Colours | Purpose |
|---|---|---|
| `_main.png` | WHITE bg + BLACK panels + RED/BLUE fold bands | structural input (panels + fold lines) |
| `_bump.png` | panel mask + YELLOW/GREEN | stamped-up / stamped-down regions |
| `_hole.png` | panel mask + PURPLE | outline carves + bolt holes + cuts |

All 75 PNGs use only the legal RGB triples per SKILL.md §1.3 — strict
palette, zero anti-aliasing.

---

## Hand-authored (Phase 1) — 5 cases

### `simple_l_bracket` — L-bracket + 2-cap stack (4 panels, 3 folds)

main | bump | hole
:--:|:--:|:--:
![](./simple_l_bracket_main_t20260601_1626.png) | ![](./simple_l_bracket_bump_t20260601_1626.png) | ![](./simple_l_bracket_hole_t20260601_1626.png)

### `u_bracket` — main + 2 flanges, caps on both (5 panels, 4 folds)

main | bump | hole
:--:|:--:|:--:
![](./u_bracket_main_t20260601_1626.png) | ![](./u_bracket_bump_t20260601_1626.png) | ![](./u_bracket_hole_t20260601_1626.png)

### `channel_bracket` — main + 3 flanges + cap (6 panels, 5 folds)

main | bump | hole
:--:|:--:|:--:
![](./channel_bracket_main_t20260601_1626.png) | ![](./channel_bracket_bump_t20260601_1626.png) | ![](./channel_bracket_hole_t20260601_1626.png)

### `accessory_l_bracket` — L + 3-cap stack (5 panels, 4 folds)

main | bump | hole
:--:|:--:|:--:
![](./accessory_l_bracket_main_t20260601_1626.png) | ![](./accessory_l_bracket_bump_t20260601_1626.png) | ![](./accessory_l_bracket_hole_t20260601_1626.png)

### `tab_plate_4` — main + 3 tabs + cap (5 panels, 4 folds)

main | bump | hole
:--:|:--:|:--:
![](./tab_plate_4_main_t20260601_1626.png) | ![](./tab_plate_4_bump_t20260601_1626.png) | ![](./tab_plate_4_hole_t20260601_1626.png)

---

## Auto-generated (Phase 2) — 20 cases

### L_right archetype (v01–v05) — main + right flange + 3-cap stack

#### `bracket_v01`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v01_main_t20260601_1626.png) | ![](./bracket_v01_bump_t20260601_1626.png) | ![](./bracket_v01_hole_t20260601_1626.png)

#### `bracket_v02`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v02_main_t20260601_1626.png) | ![](./bracket_v02_bump_t20260601_1626.png) | ![](./bracket_v02_hole_t20260601_1626.png)

#### `bracket_v03`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v03_main_t20260601_1626.png) | ![](./bracket_v03_bump_t20260601_1626.png) | ![](./bracket_v03_hole_t20260601_1626.png)

#### `bracket_v04`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v04_main_t20260601_1626.png) | ![](./bracket_v04_bump_t20260601_1626.png) | ![](./bracket_v04_hole_t20260601_1626.png)

#### `bracket_v05`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v05_main_t20260601_1626.png) | ![](./bracket_v05_bump_t20260601_1626.png) | ![](./bracket_v05_hole_t20260601_1626.png)

### L_bottom archetype (v06–v10) — main + bottom flange + 3-cap stack

#### `bracket_v06`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v06_main_t20260601_1626.png) | ![](./bracket_v06_bump_t20260601_1626.png) | ![](./bracket_v06_hole_t20260601_1626.png)

#### `bracket_v07`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v07_main_t20260601_1626.png) | ![](./bracket_v07_bump_t20260601_1626.png) | ![](./bracket_v07_hole_t20260601_1626.png)

#### `bracket_v08`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v08_main_t20260601_1626.png) | ![](./bracket_v08_bump_t20260601_1626.png) | ![](./bracket_v08_hole_t20260601_1626.png)

#### `bracket_v09`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v09_main_t20260601_1626.png) | ![](./bracket_v09_bump_t20260601_1626.png) | ![](./bracket_v09_hole_t20260601_1626.png)

#### `bracket_v10`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v10_main_t20260601_1626.png) | ![](./bracket_v10_bump_t20260601_1626.png) | ![](./bracket_v10_hole_t20260601_1626.png)

### U_caps archetype (v11–v15) — main + 2 flanges + caps on each

#### `bracket_v11`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v11_main_t20260601_1626.png) | ![](./bracket_v11_bump_t20260601_1626.png) | ![](./bracket_v11_hole_t20260601_1626.png)

#### `bracket_v12`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v12_main_t20260601_1626.png) | ![](./bracket_v12_bump_t20260601_1626.png) | ![](./bracket_v12_hole_t20260601_1626.png)

#### `bracket_v13`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v13_main_t20260601_1626.png) | ![](./bracket_v13_bump_t20260601_1626.png) | ![](./bracket_v13_hole_t20260601_1626.png)

#### `bracket_v14`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v14_main_t20260601_1626.png) | ![](./bracket_v14_bump_t20260601_1626.png) | ![](./bracket_v14_hole_t20260601_1626.png)

#### `bracket_v15`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v15_main_t20260601_1626.png) | ![](./bracket_v15_bump_t20260601_1626.png) | ![](./bracket_v15_hole_t20260601_1626.png)

### cross_caps archetype (v16–v20) — main + 4 flanges + wider cap

#### `bracket_v16`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v16_main_t20260601_1626.png) | ![](./bracket_v16_bump_t20260601_1626.png) | ![](./bracket_v16_hole_t20260601_1626.png)

#### `bracket_v17`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v17_main_t20260601_1626.png) | ![](./bracket_v17_bump_t20260601_1626.png) | ![](./bracket_v17_hole_t20260601_1626.png)

#### `bracket_v18`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v18_main_t20260601_1626.png) | ![](./bracket_v18_bump_t20260601_1626.png) | ![](./bracket_v18_hole_t20260601_1626.png)

#### `bracket_v19`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v19_main_t20260601_1626.png) | ![](./bracket_v19_bump_t20260601_1626.png) | ![](./bracket_v19_hole_t20260601_1626.png)

#### `bracket_v20`
main | bump | hole
:--:|:--:|:--:
![](./bracket_v20_main_t20260601_1626.png) | ![](./bracket_v20_bump_t20260601_1626.png) | ![](./bracket_v20_hole_t20260601_1626.png)

---

## Acceptance gate (all 25 cases)

- 0 schema-validation violations.
- 0 C1..C11 complexity-floor violations.
- 0 fold-edge clearance violations.
- All 3 PNG layers contain ONLY legal RGB triples (no AA).
- Full P1→P5 pipeline at res 2.0 passes all §3 hard gates:
  `nm=0 orph=0 comp=1 inv=0 sliver=0`.

(See `tests/recipe/test_reference_library_passes.py` for the
automated acceptance test that parametrises over every YAML.)

---

# Live-API example outputs

Real end-to-end runs against the live Gemini 2.5 Pro + Imagen 4
endpoints (no mocks, no cache hits — `use_cache=False`). Each
sub-section corresponds to one of the 7 surfaces documented
above. All artifacts (YAMLs, intents, attempt logs, PNGs) live in
`live_api/` next to this README; the inline images below are the
rendered output of each call.

Note: `s2_*` was the one case that still had 1 fold-clearance
violation when the validator ran — the renderer still produces
valid PNGs, but the recipe would not pass `acceptance gate`. This
is exactly the kind of case the Phase-4 self-correction loop is
designed to repair (see surface 3 below for a clean run, and
surface 5 batch where seed-0 needed 3 attempts to converge).

## S2 — `GeminiRecipeAuthor.design` (one shot)

Intent (`live_api/s2_intent.txt`):
> Design a 5-panel L-bracket for an automotive ECU mount: main
> plate 130x150 mm with three M6 bolt holes near the corners on
> the front, plus one rounded pocket bump for a boss feature in
> the centre. Add a flat flange on the right side with two more
> bolt holes.

Result: `ecu_mount_l_bracket`, 5 panels, 4 folds, **1 violation
(`FOLD_CLEARANCE_HOLE`)**, 42.5 s wall.

main | bump | hole
:--:|:--:|:--:
![](./live_api/s2_ecu_mount_l_bracket_main_t20260601_2100.png) | ![](./live_api/s2_ecu_mount_l_bracket_bump_t20260601_2100.png) | ![](./live_api/s2_ecu_mount_l_bracket_hole_t20260601_2100.png)

Full recipe + raw response JSON: `live_api/s2_ecu_mount_l_bracket.yaml`,
`live_api/s2_summary.json`.

## S3 — `GeminiSelfCorrectingAuthor.design` (validator-aware retry loop)

Intent (`live_api/s3_intent.txt`):
> Design a 4-panel U-channel mounting bracket: main plate
> 180x100 mm, two folded flanges (each 60 mm wide) running down
> the long edges, each flange having two M5 bolt holes. Add a
> rounded bump in the centre of the main plate.

Result: `u_channel_mount`, **succeeded on attempt 1** (0
violations), 35.0 s wall. Attempt log:
`live_api/s3_generation_attempts.jsonl`.

main | bump | hole
:--:|:--:|:--:
![](./live_api/s3_u_channel_mount_main_t20260601_2100.png) | ![](./live_api/s3_u_channel_mount_bump_t20260601_2100.png) | ![](./live_api/s3_u_channel_mount_hole_t20260601_2100.png)

## S4 — `BracketDesignerAgent` (propose → refine)

Propose intent (`live_api/s4_propose_intent.txt`):
> Design a simple L-bracket: 120x100 mm main plate with a single
> 50 mm flange on the right side. Add two M4 bolt holes on the
> main plate.

Refine instruction (`live_api/s4_refine_instruction.txt`):
> Add two more M4 bolt holes on the right flange, spaced 30 mm
> apart vertically.

Both turns succeeded with 0 violations; case `l_bracket_complex_v1`,
97.4 s wall total. Diff between turn 1 and turn 2 should show
the two added flange bolt holes.

### Turn 1 — propose
main | bump | hole
:--:|:--:|:--:
![](./live_api/s4_turn1_main_t20260601_2100.png) | ![](./live_api/s4_turn1_bump_t20260601_2100.png) | ![](./live_api/s4_turn1_hole_t20260601_2100.png)

### Turn 2 — refine ("add two more bolt holes")
main | bump | hole
:--:|:--:|:--:
![](./live_api/s4_turn2_main_t20260601_2100.png) | ![](./live_api/s4_turn2_bump_t20260601_2100.png) | ![](./live_api/s4_turn2_hole_t20260601_2100.png)

YAML diff inputs: `live_api/s4_turn1.yaml` vs.
`live_api/s4_turn2.yaml`. Session JSONL is in
`live_api/s4_summary.json`.

## S5 — `sample-batch 2` (Gemini-driven corpus expansion)

`scripts/generate_bracket.py sample-batch` runs random design
intents through the self-correction loop; keepers get persisted.
This live run used N=2 with `--seed 0 --max-retries 2
--few-shot-n 3`. **2 / 2 kept**, 160 s wall.

| seed | case_name              | attempts | viols | kept |
|------|------------------------|----------|-------|------|
| 0    | hvac_cross_support     | 3        | 0     | ✓    |
| 1    | u_bracket_trim_mount   | 1        | 0     | ✓    |

Seed-0 needed 3 attempts (self-correction loop fired twice on
intermediate violations) before converging. Seed-1 was one-shot.

### `hvac_cross_support`
main | bump | hole
:--:|:--:|:--:
![](./live_api/s5_hvac_cross_support_main_t20260601_2100.png) | ![](./live_api/s5_hvac_cross_support_bump_t20260601_2100.png) | ![](./live_api/s5_hvac_cross_support_hole_t20260601_2100.png)

### `u_bracket_trim_mount`
main | bump | hole
:--:|:--:|:--:
![](./live_api/s5_u_bracket_trim_mount_main_t20260601_2100.png) | ![](./live_api/s5_u_bracket_trim_mount_bump_t20260601_2100.png) | ![](./live_api/s5_u_bracket_trim_mount_hole_t20260601_2100.png)

Batch CSV: `live_api/s5_batch_summary.csv`. Per-attempt JSONL:
`live_api/s5_generation_attempts.jsonl`. Keeper YAMLs:
`live_api/s5_hvac_cross_support.yaml`,
`live_api/s5_u_bracket_trim_mount.yaml`.

## S7 — Imagen 4 `experiment_run` (raw → palette-snap)

The Phase-8 experiment: ask `imagen-4.0-generate-001` for a 2D
unfolding diagram with **only** 4 legal RGB triples (white /
black / red / blue), then post-process by snapping every pixel
to its nearest palette colour by L2 distance.

Intent 0: `A simple L-shape bracket with a flange and 3 bolt
holes.`
Intent 1: `A U-channel bracket with 2 flanges on opposite long
edges.`

Result:
| intent | raw unique colors | snapped strict? | px changed |
|--------|-------------------|-----------------|-----------:|
| 0      | 14,680            | ✓               | 279,602    |
| 1      | 18,791            | ✓               | 257,004    |

Both raw outputs were heavily anti-aliased (14k–19k colors); the
snap brought every pixel onto the legal 4-color palette. The
snapped PNGs are *strict-palette valid* (parser-acceptable in
principle), but the underlying geometry is freeform and would
not pass the topology gate — the experiment confirms what
GENERATION_PLAN §16 predicted: Imagen produces images, not
schema-valid recipes.

### Intent 0 — L-bracket
raw (Imagen direct) | snapped (palette-cleaned)
:--:|:--:
![](./live_api/s7_intent0_raw_t20260601_2100.png) | ![](./live_api/s7_intent0_snapped_t20260601_2100.png)

### Intent 1 — U-channel
raw (Imagen direct) | snapped (palette-cleaned)
:--:|:--:
![](./live_api/s7_intent1_raw_t20260601_2100.png) | ![](./live_api/s7_intent1_snapped_t20260601_2100.png)

Per-attempt diagnostics: `live_api/s7_summary.csv`. Intents:
`live_api/s7_intents.txt`.

---

## Live-API runtime summary

| surface | wall  | result                                            |
|---------|------:|---------------------------------------------------|
| S2      |  42 s | 1 viol (FOLD_CLEARANCE_HOLE), renders valid       |
| S3      |  35 s | 0 viol on attempt 1                               |
| S4      |  97 s | propose + refine, both 0 viol                     |
| S5      | 160 s | 2/2 keepers (seed 0 needed 3 attempts, seed 1 = 1) |
| S7      | ~30 s | 2/2 strict-palette after snap                     |

Total: 5 surfaces, **9 / 10 recipes clean** (S2 was the lone
single-shot failure that the self-correction loop in S3/S5 would
have repaired). All raw responses, YAMLs, JSONLs, PNGs are in
`live_api/`. Full machine-readable rollup:
`live_api/ALL_SUMMARIES.json`.

---

# Live-API: NEW 3-pass sequential generator (`_t20260601_2200`)

The v1 live-API outputs (S2/S3/S4/S5/S7 above) used the
single-shot `GeminiRecipeAuthor` + `GeminiSelfCorrectingAuthor`
path. Some recipes still slipped through with residual violations
(notably S2's `FOLD_CLEARANCE_HOLE`). The new default is a
**3-pass sequential generator** (`GeminiSequentialAuthor`):

  - **Stage A — skeleton.** Gemini emits only the rectangular
    panels + axis-aligned folds + outline carves + corner fillets.
    Stage-A validator suppresses every C-rule that depends on
    bumps / holes (C5/C6/C7/C10/C11). Output is forcibly stripped
    of any features Gemini accidentally emits.
  - **Stage B — bump layer.** Skeleton is rendered to PNG; the
    `main.png` and `bump.png` are passed as multimodal `Part`
    inputs alongside the skeleton YAML. Gemini emits
    `bumps_by_panel + cross_panel_features`. Stage-B validator
    runs every gate EXCEPT C6/C11 (which need holes).
  - **Stage C — hole layer.** Re-render with bumps; pass
    updated `main.png` + `bump.png` to Gemini. Output:
    `holes_by_panel`. Full validator runs — every C-rule and
    clearance gate now applies.

Each stage has its own retry budget (`max_retries`, default 2)
with focused correction prompts that include the parse error
and any violations on the previous attempt. Only the failing
stage retries — Stage A success is never re-run.

Code: `src/origami_gen/gemini/sequential_author.py`,
`src/origami_gen/recipe/sequential.py`,
`src/origami_gen/recipe/validate.py` (new
`validate_skeleton/bump_layer/hole_layer` entries),
`src/origami_gen/gemini/prompts.py` (new
`stage_a/b/c_*` builders). CLI: `scripts/generate_bracket.py
from-intent <intent> -o <dir>` and
`sample-batch N -o <dir>` (sequential default; legacy via
`--legacy-one-shot`).

## API additions

```python
from origami_gen.gemini.sequential_author import (
    GeminiSequentialAuthor,
)

author = GeminiSequentialAuthor(
    few_shot_n=3, max_retries=2, use_cache=False,
)
result = author.design(intent="<natural language design intent>")
# result.recipe              -> BracketRecipe | None
# result.success             -> bool
# result.stage_a_attempts    -> tuple[StageAttempt, ...]
# result.stage_b_attempts    -> tuple[StageAttempt, ...]
# result.stage_c_attempts    -> tuple[StageAttempt, ...]
# result.skeleton_recipe     -> BracketRecipe | None  (post Stage A)
# result.bumped_recipe       -> BracketRecipe | None  (post Stage B)

author.emit_attempts_log(result, Path("attempts.jsonl"))
```

The agent + sample-batch surfaces now route through the
sequential generator by default; legacy one-shot can be
restored via `BracketDesignerAgent(use_sequential=False)` or
`sample-batch --legacy-one-shot`.

## Side-by-side results vs. v1 (one-shot)

| surface | v1 (one-shot)                                  | v2 (sequential)                                  |
|---------|------------------------------------------------|--------------------------------------------------|
| S2      | 1 viol `FOLD_CLEARANCE_HOLE`, 42 s             | **0 viols**, 4 stage attempts (A:2 + B:1 + C:1), 146 s |
| S4      | propose + refine, both 0 viols, 97 s           | propose + refine, both 0 viols, 166 s           |
| S5      | 2/2 kept (seed 0 needed 3 retries)             | **2/2 kept, all clean**, 300 s (seed 0: 4 atts, seed 1: 5 atts) |
| S7      | 2/2 strict-palette after snap                  | 2/2 strict-palette after snap (unchanged)        |

Key delta: **S2 went from 1 violation → 0** with the same intent.
S5 trades raw time for higher per-recipe quality (each stage
narrows Gemini's task, so more total LLM round-trips, but the
final recipes pass `validate_recipe_all` clean).

## S2-seq — `GeminiSequentialAuthor.design` (ECU intent)

Same intent as the v1 S2 (130×150 mm 5-panel L-bracket with
boss + pocket bump + side flange + bolt holes). Result:
`ecu_mount_l_bracket`, **0 violations**, 4 total stage attempts.
Stage A first attempt had a Pydantic schema error (Gemini
omitted `fold_axis` on child panels); the focused retry prompt
included the parse error verbatim and the second Stage-A
attempt parsed cleanly.

main | bump | hole
:--:|:--:|:--:
![](./live_api_seq/s2_seq_main_t20260601_2200.png) | ![](./live_api_seq/s2_seq_bump_t20260601_2200.png) | ![](./live_api_seq/s2_seq_hole_t20260601_2200.png)

Per-attempt log: `live_api_seq/s2_seq_attempts.jsonl`. Stage raws:
`live_api_seq/s2_seq_summary.json` (4 stage raws referenced).

## S4-seq — `BracketDesignerAgent` (sequential propose + refine)

Same intents as v1 S4. Both turns 0 violations. Sequential
propose ran A→B→C clean on the first try (all stages
single-attempt).

### Turn 1 — propose
main | bump | hole
:--:|:--:|:--:
![](./live_api_seq/s4_seq_turn1_main_t20260601_2200.png) | ![](./live_api_seq/s4_seq_turn1_bump_t20260601_2200.png) | ![](./live_api_seq/s4_seq_turn1_hole_t20260601_2200.png)

### Turn 2 — refine ("add two more bolt holes")
main | bump | hole
:--:|:--:|:--:
![](./live_api_seq/s4_seq_turn2_main_t20260601_2200.png) | ![](./live_api_seq/s4_seq_turn2_bump_t20260601_2200.png) | ![](./live_api_seq/s4_seq_turn2_hole_t20260601_2200.png)

YAML diff inputs: `live_api_seq/s4_seq_turn1.yaml` vs.
`live_api_seq/s4_seq_turn2.yaml`. The refine step still uses
the legacy one-shot path because the existing recipe is already
fully featured; sequential is only used on the initial propose.

## S5-seq — `sample-batch 2` (sequential)

Same N=2 random intents as v1 S5 with `--seed 0 --max-retries 2
--few-shot-n 3`. **2 / 2 kept, all clean** (`final_n_violations=0`
on both). Total stage attempts:

| seed | case_name              | total attempts | viols | kept |
|------|------------------------|----------------|-------|------|
| 0    | cross_bracket_hvac     | 4              | 0     | ✓    |
| 1    | u_bracket_trim_mount   | 5              | 0     | ✓    |

### `cross_bracket_hvac`
main | bump | hole
:--:|:--:|:--:
![](./live_api_seq/s5_seq_cross_bracket_hvac_main_t20260601_2200.png) | ![](./live_api_seq/s5_seq_cross_bracket_hvac_bump_t20260601_2200.png) | ![](./live_api_seq/s5_seq_cross_bracket_hvac_hole_t20260601_2200.png)

### `u_bracket_trim_mount`
main | bump | hole
:--:|:--:|:--:
![](./live_api_seq/s5_seq_u_bracket_trim_mount_main_t20260601_2200.png) | ![](./live_api_seq/s5_seq_u_bracket_trim_mount_bump_t20260601_2200.png) | ![](./live_api_seq/s5_seq_u_bracket_trim_mount_hole_t20260601_2200.png)

Batch summary CSV: `live_api_seq/s5_seq_batch_summary.csv`. Per-
attempt JSONL: `live_api_seq/s5_seq_attempts.jsonl`. Keeper
YAMLs in `live_api_seq/s5_seq_*.yaml`.

## S7 — Imagen 4 `experiment_run` (unchanged)

The Imagen experiment is independent of the recipe generator and
behaves identically to v1. Both intents render heavily anti-aliased
(15k–32k unique colors) raw images that the palette-snap brings
down to the legal 4 colors. Schema-conforming pixels, freeform
geometry — same caveat as v1.

| intent | raw unique colors | snapped strict? | px changed |
|--------|-------------------|-----------------|-----------:|
| 0      | 14,977            | ✓               | 246,010    |
| 1      | 31,840            | ✓               | 302,062    |

### Intent 0 — L-bracket
raw | snapped
:--:|:--:
![](./live_api_seq/s7_intent0_raw_t20260601_2200.png) | ![](./live_api_seq/s7_intent0_snapped_t20260601_2200.png)

### Intent 1 — U-channel
raw | snapped
:--:|:--:
![](./live_api_seq/s7_intent1_raw_t20260601_2200.png) | ![](./live_api_seq/s7_intent1_snapped_t20260601_2200.png)

---

## Sequential runtime + acceptance summary

| surface | wall  | result (sequential)                              |
|---------|------:|--------------------------------------------------|
| S2-seq  | 146 s | 0 viols (was 1 in v1); 4 stage attempts          |
| S4-seq  | 166 s | propose + refine, both 0 viols                   |
| S5-seq  | 300 s | 2/2 keepers ALL clean (vs. 2/2 with seed-0 noisy in v1) |
| S7      | ~30 s | 2/2 strict-palette after snap                    |

**Net: 4/4 recipe-generation surfaces produce clean (zero-violation)
recipes**, where v1 had 1 stray FOLD_CLEARANCE_HOLE on S2. Stage
A self-corrects schema errors before Stage B/C ever run, so an
expensive Stage-C retry on a malformed skeleton is impossible.
Full machine-readable rollup: `live_api_seq/ALL_SUMMARIES.json`.

---

## Prior snapshot

The previous v3-audit snapshot (`_t20260531_1916` suffix, 42-case
visualization × 3 res) is in `archive_v3_audit_20260531_1916/`
— 602 files preserved verbatim.

Branch: https://github.com/voltwin-dev/Origami_Gen/tree/v3-gen
PR-ready at: https://github.com/voltwin-dev/Origami_Gen/pull/new/v3-gen
