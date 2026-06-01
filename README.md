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

## Prior snapshot

The previous v3-audit snapshot (`_t20260531_1916` suffix, 42-case
visualization × 3 res) is in `archive_v3_audit_20260531_1916/`
— 602 files preserved verbatim.

Branch: https://github.com/voltwin-dev/Origami_Gen/tree/v3-gen
PR-ready at: https://github.com/voltwin-dev/Origami_Gen/pull/new/v3-gen
