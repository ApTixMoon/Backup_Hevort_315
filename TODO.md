# Todo-liste — Hevort 315

> Oppdatert 04.07.2026. Full audit av printer-config (`klipper`-branch), OrcaSlicer (`orca`-branch), Raspberry Pi og WiFi. Config-endringer gjøres manuelt via Mainsail/Orca — aldri push til `klipper`/`orca` (én-veis backup). Status verifisert mot backup 65edb7f.

## 🟡 Klipper config — gjenstår

- [ ] **Eddy probe rekalibrering** — kjør `PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy_probe` + `SAVE_CONFIG` for å fikse negativ slope-delta på tap-deteksjon
- [ ] **`tap_threshold: 30 → 0`** — midlertidig i printer.cfg (linje ~381) til rekalibreringen over er gjort (`30` gir "insufficient slope delta"). Henger sammen med punktet over.
- [ ] **WLED-lys i makroer** — legg inn `SET_WLED`-kall: hvitt i `PRINT_START_PHASE_1`, grønt i `PRINT_END`, evt. rødt i `CANCEL_PRINT`. Test `WLED_ON STRIP=my_leds` først (WLED er nå på riktig subnett).
- [ ] **Slett TEST-blokken i heatsoak.cfg** (linje 282–286) — ufarlig (`#` i kolonne 0 stripes av Klipper), ren opprydding. SLETT linjene, ikke fjern `#`.
- [ ] **Verifiser TMC5160 X/Y `run_current: 2.6`A** mot motorenes merkestrøm (≤ ~85 % av rated) — informativt

## 🟠 WiFi-stabilitet Raspberry Pi 5

Diagnose: brcmfmac-driveren henger (kjent RPi5-bug, «HT Avail timeout» — kun reboot hjelper; sonar sine WiFi-restarter biter ikke). Triggere: roaming + 1080p kamerastrøm.

- [x] **roamoff + feature_disable** — `/etc/modprobe.d/brcmfmac.conf` med `roamoff=1 feature_disable=0x282000` ✓ (verifiser med `cat /sys/module/brcmfmac/parameters/roamoff` = 1)
- [x] **Firmware/kernel oppdatert** — `apt` (kun WiFi/kernel, ikke printer-programvaren) ✓
- [ ] **Persistent journal** — bevisst hoppet over. Legg til hvis du vil fange loggen ved neste frys: `sudo mkdir -p /var/log/journal && sudo systemctl restart systemd-journald`
- [ ] **Testperiode** — la den printe noen dager og se om frysene er borte. Fallback hvis ikke: crowsnest 720p/15fps, eller Ethernet-kabel (definitiv løsning).

## 🟡 OrcaSlicer — helt urørt ennå

> Verifisert OK: `printable_area` 300x265/Z450 matcher printer.cfg eksakt («315» er rammenavnet). Start-gcode kaller `PRINT_START_PHASE_1` riktig og setter M109 etterpå; PRINT_END på plass; PHASE_2 brukes ikke.

- [ ] **Maskinprofil-defaults** peker på ikke-eksisterende profiler — `default_filament_profile: "Vzbot Generic ABS"` og `default_print_profile: "0.20mm Standard @Vzbot"` → pek på faktiske Hevort-profiler
- [ ] **PETG-prosess**: `bridge_speed 300` → ~60; overhang-hastigheter inverterte (`4_4=210` raskere enn `3_4=170`) — bratteste overheng skal være tregest (f.eks. 4_4=30–50)
- [ ] **ASA-profiler spriker** — 3DJake 275°C vs Generic 230°C nozzle (normalt 240–260); velg én baseline
- [ ] **ABS mangler kammerstyring** — `chamber_temperature 0`/`control 0` og `fan_max 80`, mens ASA kjører kammer 70–90/fan 20. ABS bør ha kammer ~50–60 og lavere fan-max
- [ ] **Start-gcode X-offset** — `{first_layer_print_min[0]-3}` kan gi negativ X. Bytt til `{max(first_layer_print_min[0] - 3, 0)}` begge steder
- [ ] **Opprydding**: `@MyMarlin`-kopiene (2 process + 2 filament + eSUN PLA), `0.2mm ABS_CF @HevORT315_0.5` (arver fra MyKlipper — repoint eller slett), tom `ASA 0.2mm layer @Hevort SPAWD 315`-stub, orphan `3DJake ASA @Bambu Lab X1E .info`

## 🟢 Valgfritt / hygiene

- [ ] **mainsail-config i backup er gitlink** — `rm -rf ~/mainsail-config/.git` på Pi hvis faktiske filer ønskes i backupen
- [ ] **Timelapse** — komponenten er installert men `[timelapse]` er utkommentert i moonraker.conf; aktiver hvis ønsket

## Fullført

- [x] **PLA heat_soak-kollisjon** — `SOAK_TIMEOUT` for CHAMBER_TEMP=0 satt til 10 (var 5 = MIN_SOAK_TIME → kunne aldri nå "done"-grenen, endte alltid som "timed out"). Nå fullfører PLA-soaken rent ved 5 min via "done"-veien. ✓
- [x] **Mobileraker-krasj (hvert 10. sek)** — ` Default: true` flyttet til kolonne 0 → egen ufarlig nøkkel i stedet for fortsettelse av `include_snapshot`. Verifisert med configparser: ingen krasj. ✓
- [x] **idle_timeout slo av printeren midt i pause** — gjort betinget på `printer.pause_resume.is_paused` (kun `M104 S0` ved pause). Runout-pause kutter ikke lenger strømmen. ✓
- [x] **WLED subnett** — `192.168.1.232` → `192.168.38.232` (samme nett som printeren) ✓
- [x] **`[neopixel my_neopixel]` slettet** — død config (gpio17 kan ikke drive WS2812); WLED overtar ✓
- [x] **max_accel** — 50000 → 30000 (innenfor shaper, matcher Orca travel-accel) ✓
- [x] **max_extrude_cross_section** — 50 → 10 (blob-vern gjenopprettet) ✓
- [x] **bed_mesh algorithm** — `lagrange` → `bicubic` ✓
- [x] **`[sonar]`-blokk fjernet fra moonraker.conf** — sonar-daemonen leser `sonar.conf` direkte; blokken var redundant ✓
- [x] **Rydd macros.cfg** — fjernet stablet HEAT_SOAK-variant og `#M109`-hale i PRINT_START_PHASE_1 ✓
- [x] **CANCEL_PRINT** — `STOP_HEAT_SOAK` lagt til i makroen ✓
- [x] **PAUSE makro** — `rename_existing: _PAUSE_BASE`; is_soaking-gren uten parkering, ellers `_PAUSE_BASE` + `_TOOLHEAD_PARK_PAUSE_CANCEL` ✓
- [x] **HEAT_SOAK auto-resume** — én-fase med `CANCEL="{ON_TIMEOUT}"`: `RESUME` ved CHAMBER_TEMP=0, `CANCEL_PRINT` ved kammer-print ✓
- [x] **WLED-makroer** (`WLED_ON`/`WLED_OFF`/`SET_WLED`) lagt inn i macros.cfg ✓
- [x] **`[wled my_leds]`** lagt inn i moonraker.conf ✓
- [x] **Bed mesh dekning** — `mesh_max: 260, 260` ✓
- [x] **PETG flow rate** — redusert med -2% ✓
- [x] **M107 i start-gcode** — kjøres i `PRINT_START_PHASE_1` ✓
- [x] **`printer_data/` arkivert fra `main`** ✓
- [x] **OrcaSlicer-backup flyttet til `orca`-branch** ✓
