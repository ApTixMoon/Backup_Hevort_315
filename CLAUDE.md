# Regler for Claude i dette repoet

Denne branchen (`orca`) speiler brukerens faktiske OrcaSlicer-profiler
(`orca_slicer/`). Et backup-script på PCen synkroniserer jevnlig FRA de
faktiske profilfilene TIL denne branchen — altså går synkroniseringen én
vei, fra OrcaSlicer til GitHub.

## Viktig: ikke push config-endringer direkte

- **IKKE** bruk `git push` / `create_or_update_file` for å endre filer
  under `orca_slicer/`. Slike endringer blir overskrevet neste gang
  backup-scriptet kjører, siden OrcaSlicer fortsatt har den gamle
  versjonen.
- Når du finner en feil eller forbedring i en profil:
  1. Forklar problemet og fiksen.
  2. Vis nøyaktig hvilket felt/verdi som skal endres — fil og
     før/etter-verdi — slik at brukeren kan endre det manuelt i
     OrcaSlicer (eller direkte i JSON-filen lokalt).
  3. IKKE commit/push disse endringene selv.
- `TODO.md` (på `main`-branchen) kan fortsatt oppdateres direkte for å
  spore status på funn/fikser.
