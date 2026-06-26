# Raw h5 Integrity Check — main Moldflow attributes on point cloud (13 figures)

Plotted the **raw Moldflow node fields directly on the full point cloud**, with
**no solver and no body-extraction**. Goal: confirm the h5 ground-truth data is
not corrupt before trusting any predicted-vs-GT comparison.

- **NaN / undefined nodes are drawn light-gray**, so missing data and
  missing-injection regions are visible at a glance.
- Colour = field value (jet, 2–98 percentile of defined nodes).
- Title shows `def=<fraction defined>` for each field.

## Files (`raw_h5/`)
One figure per study; overmolding studies also have an `_OM` figure (2nd shot).

```
raw_jx1_sublowref1     raw_jx1_sublowref2
raw_nq5_sub_bezel_rev1 raw_nq5_sub_bezel_50_45
raw_nq5_otr_htc (+_OM) raw_nq5_otr_45_35 (+_OM) raw_nq5_otr_55_45 (+_OM)
raw_lx3_drl            raw_lx3_otr_om1 (+_OM)
```

## Each figure has 6 subplots (the validation-relevant GT fields)
| panel | h5 key | meaning |
|---|---|---|
| MeltFrontTime | `F_MeltFrontTime` | fill arrival time — drives inlet (≈0) & front detection |
| PressureAtEndOfFill | `F_PressureAtEndOfFill` | pressure GT |
| MeltFrontTemperature | `F_MeltFrontTemperature` | front temp GT |
| FrozenLayerAtEndOfFill | `F_FrozenLayerAtEndOfFill` | frozen-layer fraction GT |
| TimeToEjectionTemp | `C_TimeToReachEjectionTemperature` | ejection-time GT |
| MaxShearRate_main | `time/F_MaxShearRate_main[:,0]` | max shear rate GT |

## How to read it
- A field that is **all-gray** (def=0.00) = not present / undefined for that part.
- **Scattered gray patches** inside an otherwise coloured body = the multi-component
  mesh (runner/sprue/other cavities sharing the file) — expected.
- If a field that should be smooth shows random speckle or holes on the **main body**,
  that points to genuine h5 corruption (none expected — this check verifies that).
