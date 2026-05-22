# Todo-liste — Hevort 315

## Klipper config

- [ ] **Eddy probe rekalibrering** — kjør `PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy_probe` etterfulgt av `SAVE_CONFIG` for å fikse negativ slope-delta på tap-deteksjon
- [ ] **`tap_threshold`** — sett til `0` midlertidig i printer.cfg til rekalibrering er utført (nåværende verdi `30` gir "insufficient slope delta" feil)
- [ ] **CANCEL_PRINT** — legg til `STOP_HEAT_SOAK` som første linje i makroen for å unngå advarsel når print avbrytes under heat_soak
- [ ] **PAUSE makro** — bekreft at mainsail.cfg bruker `rename_existing: BASE_PAUSE` ved å kjøre: `cat ~/printer_data/config/mainsail.cfg | grep rename_existing`

## Oppsett

- [ ] **klipper-backup branch** — endre `branch_name=main` til `branch_name=backup` i `~/klipper-backup/.env` slik at klipper-backup pusher til en egen branch og ikke overskriver filer i main

## Valgfritt / forbedringer

- [ ] **Bed mesh dekning** — vurder å øke `mesh_max: 260, 230` → `260, 260` for bedre dekning bakover på sengen
