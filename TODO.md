# Todo-liste — Hevort 315

## Klipper config
> Gjeldende config ligger i `klipper`-branchen

- [ ] **Eddy probe rekalibrering** — kjør `PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy_probe` etterfulgt av `SAVE_CONFIG` for å fikse negativ slope-delta på tap-deteksjon
- [ ] **`tap_threshold`** — sett til `0` midlertidig i printer.cfg til rekalibrering er utført (nåværende verdi `30` gir "insufficient slope delta" feil)
- [x] **CANCEL_PRINT** — `STOP_HEAT_SOAK` lagt til som første linje i makroen ✓
- [x] **PAUSE makro** — bekreftet at mainsail.cfg bruker `BASE_PAUSE` via `rename_existing` ✓
- [x] **HEAT_SOAK ble hoppet over / "aborted" feil** — `PRINT_START_PHASE_1` delt i to: `PHASE_1` avsluttes rett etter `HEAT_SOAK`-kallet (med `MIN_SOAK_TIME=5` for garantert min. 5 min soak), og leveling/mesh (`BED_MESH_CALIBRATE`, `SET_Z_FROM_PROBE`, `SKEW_PROFILE`) er flyttet til ny `PRINT_START_PHASE_2` som trigges via `COMPLETE`-callback når soaken faktisk er ferdig. Fikset også `SOAK_TIMEOUT==MIN_SOAK_TIME==5` kollisjon (begge var 5 ved `CHAMBER_TEMP=0`, som trigget `CANCEL_PRINT` etter nøyaktig 5 min) — `SOAK_TIMEOUT` for `CHAMBER_TEMP=0` er nå 15 min. Ryddet opp i "TEST"-kommentarer i heatsoak.cfg ✓
  - NB: PHASE_2 kjører nå full `BED_MESH_CALIBRATE` (RAPID_SCAN) på hver print i stedet for å laste lagret "default" mesh — print-start tar litt lenger tid, men gir mer nøyaktig mesh på en oppvarmet seng

## OrcaSlicer
> OrcaSlicer-filer ligger i `orca`-branchen

- [ ] **Start-gcode X-offset** — `{first_layer_print_min[0]-3}` kan gi negativ X-posisjon. Bytt til `{max(first_layer_print_min[0] - 3, 0)}` begge steder i start-gcode
- [x] **PETG flow rate** — redusert med -2% ✓
- [x] **M107 i start-gcode** — bekreftet at `M107` allerede kjøres inne i `PRINT_START_PHASE_1`-makroen ✓

## Oppsett

- [x] **`printer_data/` arkivert fra `main`** — slettet, gjeldende config er i `klipper`-branchen ✓
- [x] **OrcaSlicer-backup flyttet til `orca`-branch** — orca_backup.ps1 oppdatert og kjørt ✓

## Valgfritt / forbedringer

- [ ] **Bed mesh dekning** — vurder å øke `mesh_max: 260, 230` → `260, 260` for bedre dekning bakover på sengen
