# Todo-liste — Hevort 315

## Klipper config
> Gjeldende config ligger i `klipper`-branchen

- [ ] **Eddy probe rekalibrering** — kjør `PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy_probe` etterfulgt av `SAVE_CONFIG` for å fikse negativ slope-delta på tap-deteksjon
- [ ] **`tap_threshold`** — sett til `0` midlertidig i printer.cfg til rekalibrering er utført (nåværende verdi `30` gir "insufficient slope delta" feil)
- [ ] **CANCEL_PRINT** — legg til `STOP_HEAT_SOAK` som første linje i makroen for å unngå advarsel når print avbrytes under heat_soak
- [ ] **PAUSE makro** — bekreft at mainsail.cfg bruker `rename_existing: BASE_PAUSE` ved å kjøre: `cat ~/printer_data/config/mainsail.cfg | grep rename_existing`
- [ ] **OrcaSlicer start-gcode** — sjekk at `M107` kjøres før `M109` slik at CPAP-viften er av under oppvarming av dyspe

## OrcaSlicer
> OrcaSlicer-filer ligger i `main`-branchen (orca_slicer/)

- [ ] **PETG flow rate** — reduser flow rate med -2% for PETG-profilen
- [ ] **Flytt OrcaSlicer-backup til `orca`-branch** — oppdater `orca_backup.ps1` med ny branch-logikk og kjør én gang for å opprette `orca`-branchen på GitHub

## Oppsett

- [ ] **Slett utdatert `printer_data/` fra `main`** — denne er arkivert, gjeldende config er i `klipper`-branchen

## Valgfritt / forbedringer

- [ ] **Bed mesh dekning** — vurder å øke `mesh_max: 260, 230` → `260, 260` for bedre dekning bakover på sengen
