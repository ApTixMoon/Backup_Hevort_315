# Regler for Claude i dette repoet

Dette repoet inneholder backup av Klipper-config (`klipper`-branch) og
OrcaSlicer-profiler (`orca`-branch) for printeren Hevort SPAWD 315.
Et backup-script på printeren/PCen synkroniserer jevnlig FRA printerens
faktiske filer TIL disse branchene — altså går synkroniseringen én vei,
fra printer til GitHub.

## Viktig: ikke push config-endringer direkte

- **IKKE** bruk `git push` / `create_or_update_file` for å endre filer i
  `printer_data/` (klipper-branch) eller `orca_slicer/` (orca-branch).
  Slike endringer blir overskrevet neste gang backup-scriptet kjører,
  siden printeren fortsatt har den gamle versjonen.
- Når du finner en feil eller forbedring i config/profiler:
  1. Forklar problemet og fiksen.
  2. Vis nøyaktig hvilke linjer som skal endres — fil, seksjon, og
     før/etter-snutt — slik at brukeren kan lime det inn manuelt via
     Mainsail/Fluidd sin filredigerer (Klipper-config) eller OrcaSlicer
     (profiler).
  3. IKKE commit/push disse endringene selv.
- `TODO.md` (på `main`) er IKKE en printer-config-fil og kan fortsatt
  oppdateres direkte for å spore status på funn/fikser.
- Andre filer i repoet (dokumentasjon, scripts som ikke speiler
  printer-config) kan også endres direkte ved behov.
