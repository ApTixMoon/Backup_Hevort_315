# Regler for Claude i dette repoet

Denne branchen (`klipper`) speiler printerens faktiske Klipper-config
(`printer_data/`). Et backup-script på printeren/PCen synkroniserer
jevnlig FRA printerens faktiske filer TIL denne branchen — altså går
synkroniseringen én vei, fra printer til GitHub.

## Viktig: ikke push config-endringer direkte

- **IKKE** bruk `git push` / `create_or_update_file` for å endre filer
  under `printer_data/`. Slike endringer blir overskrevet neste gang
  backup-scriptet kjører, siden printeren fortsatt har den gamle
  versjonen.
- Når du finner en feil eller forbedring i config:
  1. Forklar problemet og fiksen.
  2. Vis nøyaktig hvilke linjer som skal endres — fil, seksjon, og
     før/etter-snutt — slik at brukeren kan lime det inn manuelt via
     Mainsail/Fluidd sin filredigerer.
  3. IKKE commit/push disse endringene selv.
- `TODO.md` (på `main`-branchen) kan fortsatt oppdateres direkte for å
  spore status på funn/fikser.
