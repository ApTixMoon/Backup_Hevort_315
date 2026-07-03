# Todo-liste — Hevort 315

> Oppdatert 04.07.2026. Full audit av printer-config (`klipper`-branch), OrcaSlicer (`orca`-branch), Raspberry Pi og WiFi. Alle config-endringer gjøres manuelt via Mainsail/Orca — aldri push til `klipper`/`orca` (én-veis backup). Status verifisert mot backup 68211ed.

## 🔴 Kritisk

- [x] **Mobileraker-krasj (hvert 10. sek)** — løst: ` Default: true` flyttet til kolonne 0 → egen (ufarlig) nøkkel i stedet for fortsettelse av `include_snapshot`. Verifisert med configparser: parses nå rent som `True`, ingen krasj. ✓
- [x] **idle_timeout slo av printeren midt i pause** — løst: `[idle_timeout]` gjort betinget på `printer.pause_resume.is_paused` (kun `M104 S0` ved pause, full power-off ellers). Runout-pause kutter ikke lenger strømmen. ✓
- [ ] **WLED når ikke frem — feil subnett** — `[wled my_leds]` peker fortsatt på `192.168.1.232`, printeren står på 192.168.38.x. `ping 192.168.1.232` fra Pi; flytt ESP32 til 38-nettet (sjekk SSID), gi fast IP, oppdater `address:`, restart moonraker, test `WLED_ON STRIP=my_leds`. (Inline-kommentarene i seksjonen er OK — Moonraker striper dem.)

## 🟠 WiFi-stabilitet Raspberry Pi 5

Diagnose: brcmfmac-driveren henger (kjent RPi5-bug, «HT Avail timeout» — kun reboot hjelper; sonar sine WiFi-restarter biter ikke). Triggere: roaming mellom AP-er/subnett + vedvarende last fra 1080p kamerastrøm og WebSockets. 90 unsafe shutdowns i Moonraker-DB.

- [ ] **roamoff + feature_disable**: `echo "options brcmfmac roamoff=1 feature_disable=0x282000" | sudo tee /etc/modprobe.d/brcmfmac.conf` → reboot → `cat /sys/module/brcmfmac/parameters/roamoff` skal vise `1` (samme fiks som Home Assistant OS shipper som standard)
- [ ] **Oppdater firmware/kernel**: `sudo apt update && sudo apt full-upgrade` (WiFi-firmware er fra aug 2023)
- [ ] **Persistent journal** (for å obdusere neste frys): `sudo mkdir -p /var/log/journal && sudo systemctl restart systemd-journald` → etter neste krasj: `journalctl -k -b -1 | grep -E "brcmfmac|wlan"`
- [ ] **Vurder**: crowsnest ned til 1280x720/15fps hvis WiFi beholdes; Ethernet er den definitive løsningen

## 🟡 Klipper config

- [ ] **Eddy probe rekalibrering** — kjør `PROBE_EDDY_CURRENT_CALIBRATE CHIP=eddy_probe` etterfulgt av `SAVE_CONFIG` for å fikse negativ slope-delta på tap-deteksjon
- [ ] **`tap_threshold`** — sett til `0` midlertidig i printer.cfg (linje ~381, fortsatt `30`) til rekalibrering er utført (`30` gir "insufficient slope delta")
- [x] **Slett `[neopixel my_neopixel]`** — fjernet fra printer.cfg. ✓
- [ ] **Slett TEST-blokken i heatsoak.cfg** (linje 282–286) — ufarlig i dag (`#` i kolonne 0 stripes av Klipper før Jinja), men forvirrende. NB: SLETT linjene, ikke fjern `#` — da knekker configen.
- [x] **`max_accel`** — senket 50000 → 30000 (matcher Orca sin travel-accel; godt innenfor shaper). ✓
- [ ] **`max_extrude_cross_section: 50` → 5–10** (printer.cfg linje 496) — blob-vernet er i praksis avslått (default 4); 50 er mer enn runout-purgen trenger
- [ ] **Verifiser TMC5160 X/Y `run_current: 2.6`A** mot motorenes merkestrøm (bør være ≤ ~85 % av rated)
- [ ] **`[bed_mesh]` `algorithm: lagrange` → `bicubic`** (printer.cfg linje 289; bedre ved 6x6-grid); vurder `fade_start/fade_end`
- [ ] **WLED-lys i makroer** (etter at WLED virker): `SET_WLED STRIP=my_leds RED=1 GREEN=1 BLUE=1` først i `PRINT_START_PHASE_1`, `RED=0 GREEN=1 BLUE=0` sist i `PRINT_END`, evt. `RED=1` i `CANCEL_PRINT`
- [x] **Rydd macros.cfg** — fjernet stablet HEAT_SOAK-variant og `#M109`-hale i PRINT_START_PHASE_1. ✓

## 🟡 OrcaSlicer

> Verifisert OK: `printable_area` 300x265/Z450 matcher printer.cfg eksakt («315» er rammenavnet). Start-gcode kaller `PRINT_START_PHASE_1` riktig og setter M109 etterpå; PRINT_END på plass; PHASE_2 brukes ikke.

- [ ] **Maskinprofil-defaults peker på ikke-eksisterende profiler** — `default_filament_profile: "Vzbot Generic ABS"` og `default_print_profile: "0.20mm Standard @Vzbot"` → pek på faktiske Hevort-profiler
- [ ] **PETG-prosess**: `bridge_speed 300` → ~60; overhang-hastigheter er inverterte (`4_4=210` raskere enn `3_4=170`) — bratteste overheng skal være tregest (f.eks. 4_4=30–50)
- [ ] **ASA-profiler spriker** — 3DJake 275°C vs Generic 230°C nozzle (normalt 240–260); velg én baseline
- [ ] **ABS mangler kammerstyring** — `chamber_temperature 0`/`control 0` og `fan_max 80`, mens ASA kjører kammer 70–90/fan 20. ABS bør ha kammer ~50–60 og lavere fan-max
- [ ] **Start-gcode X-offset** — `{first_layer_print_min[0]-3}` kan gi negativ X. Bytt til `{max(first_layer_print_min[0] - 3, 0)}` begge steder
- [ ] **Opprydding**: `@MyMarlin`-kopiene (2 process + 2 filament + eSUN PLA), `0.2mm ABS_CF @HevORT315_0.5` (arver fra MyKlipper som ikke finnes — repoint eller slett), tom `ASA 0.2mm layer @Hevort SPAWD 315`-stub, orphan `3DJake ASA @Bambu Lab X1E .info`

## 🟢 Tjenester / hygiene

- [ ] **Fjern `[sonar]`-blokken fra moonraker.conf** (fortsatt til stede, linje 89) — sonar-daemonen leser `sonar.conf` direkte (den er den aktive configen); Moonraker har ingen sonar-komponent, blokken er redundant
- [ ] **mainsail-config i backup er gitlink** — `rm -rf ~/mainsail-config/.git` på Pi hvis faktiske filer ønskes i backupen
- [ ] **Timelapse** — komponenten er installert men `[timelapse]` er utkommentert i moonraker.conf; aktiver hvis ønsket

## Fullført (tidligere)

- [x] **CANCEL_PRINT** — `STOP_HEAT_SOAK` lagt til i makroen ✓
- [x] **PAUSE makro** — `rename_existing: _PAUSE_BASE` i macros.cfg; is_soaking-gren uten parkering, ellers `_PAUSE_BASE` + `_TOOLHEAD_PARK_PAUSE_CANCEL` ✓
- [x] **HEAT_SOAK auto-resume** — én-fase med `CANCEL="{ON_TIMEOUT}"`: `RESUME` ved `CHAMBER_TEMP=0`, `CANCEL_PRINT` ved kammer-print ✓
- [x] **WLED-makroer** (`WLED_ON`/`WLED_OFF`/`SET_WLED`) lagt inn i macros.cfg ✓
- [x] **`[wled my_leds]`** lagt inn i moonraker.conf ✓ (men se subnett-punkt over)
- [x] **Bed mesh dekning** — `mesh_max: 260, 260` ✓
- [x] **PETG flow rate** — redusert med -2% ✓
- [x] **M107 i start-gcode** — kjøres i `PRINT_START_PHASE_1` ✓
- [x] **`printer_data/` arkivert fra `main`** ✓
- [x] **OrcaSlicer-backup flyttet til `orca`-branch** ✓
