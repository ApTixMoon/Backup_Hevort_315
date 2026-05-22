# Todo-liste — Hevort 315

## Klipper config

- [ ] **`verify_heater extruder`** — øk `max_error: 60` → `120` for Goliath 100W
- [ ] **Eddy probe rekalibrering** — kjør `PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy_probe` etterfulgt av `SAVE_CONFIG` for å fikse negativ slope-delta på tap-deteksjon

## Valgfritt / forbedringer

- [ ] **Bed mesh dekning** — vurder å øke `mesh_max: 260, 230` → `260, 260` for bedre dekning bakover på sengen
