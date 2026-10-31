#!/usr/bin/env python3
"""Chamber temperature text for the go2rtc camera stream (2026-10-31).

go2rtc's ffmpeg draws the contents of /run/cam-overlay/overlay.txt in the
top-right corner of the "hevort" stream (see go2rtc.yaml) and re-reads the
file twice a second. This script keeps that file current: every 2 s it asks
Moonraker for the chamber air (enclosure_temp) and for the chamber heater
(heater_chamber). The heater's thermistor sits at the heater itself, so it
reads about 10 C above the air while heating.

Top right because Mobileraker's full-screen camera view puts its own
hotend/bed text top left, and its buttons and progress bar along the bottom.

The file must exist whenever the stream runs: drawtext stops ffmpeg, and
with it the stream, if it cannot read the file. Hence the atomic replace
below, and RuntimeDirectoryPreserve in the unit, which keeps the directory
across restarts of this service.

Runs as /etc/systemd/system/cam-overlay.service (enable it, it is pulled in
by go2rtc.service too):

  [Unit]
  Description=Chamber temperature text for the go2rtc camera stream
  After=moonraker.service
  Before=go2rtc.service

  [Service]
  Type=simple
  User=hevort
  RuntimeDirectory=cam-overlay
  RuntimeDirectoryPreserve=yes
  ExecStart=/usr/bin/python3 -I /home/hevort/scripts/cam_overlay.py
  Restart=always
  RestartSec=5

  [Install]
  WantedBy=multi-user.target go2rtc.service
"""
import json
import os
import time
import urllib.request

URL = ('http://127.0.0.1:7125/printer/objects/query'
       '?temperature_sensor%20enclosure_temp=temperature'
       '&heater_generic%20heater_chamber=temperature,target')
OUT = '/run/cam-overlay/overlay.txt'
INTERVAL = 2


def overlay_text():
    try:
        with urllib.request.urlopen(URL, timeout=2) as r:
            status = json.load(r)['result']['status']
        air = status['temperature_sensor enclosure_temp']['temperature']
        heater = status['heater_generic heater_chamber']
    except Exception:
        # Moonraker down or Klipper not ready: dashes, not a stale value.
        return 'Kammer: -- °C\nVarmer: -- °C'
    # Current/target while the heater has a target, like Mobileraker shows
    # hotend and bed; just the current value when it is off.
    if heater['target'] > 0:
        h = '%.0f/%.0f' % (heater['temperature'], heater['target'])
    else:
        h = '%.0f' % heater['temperature']
    return 'Kammer: %.0f °C\nVarmer: %s °C' % (air, h)


def write(text):
    tmp = OUT + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, OUT)


last = None
while True:
    text = overlay_text()
    if text != last:
        write(text)
        last = text
    time.sleep(INTERVAL)
