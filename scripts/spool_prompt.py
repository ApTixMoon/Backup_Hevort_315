#!/usr/bin/env python3
"""Pick the spool for FILAMENT_LOAD and start the load.

Order: an explicit spool id ("temp <id>"), then the spool already active in
Spoolman, then a dialog. Mobileraker cannot show action:prompt dialogs, so on the
phone the choice is made on its Spoolman page and this script picks it up from
there; Mainsail and KlipperScreen get the dialog. The buttons are built from
Spoolman on every call, so adding spools there needs no config editing.

Arguments: "temp <spool_id>" to load that spool, or "auto" (the default).
"""

import json
import os
import sys
import urllib.request

BASE = 'http://127.0.0.1:7125'


def detach():
    # RUN_SHELL_COMMAND holds Klipper's gcode lock until this process exits, and
    # every gcode posted below queues behind that lock. Waiting for them here
    # deadlocked until the request timed out, so hand the work to a child and
    # let Klipper go at once. The child must drop the inherited pipes too, or
    # Klipper keeps waiting for EOF on them.
    if os.fork():
        os._exit(0)
    os.setsid()
    fd = os.open(os.devnull, os.O_RDWR)
    for n in (0, 1, 2):
        os.dup2(fd, n)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r).get('result')


def post(path, payload, timeout=10):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get('result')


def gcode(script):
    # Long timeout: a load runs for minutes. Errors are not ours to handle - a
    # failing gcode reports itself in the console.
    try:
        post('/printer/gcode/script', {'script': script}, timeout=1800)
    except Exception:
        pass


def clean(s):
    # '|' separates the button fields, and quotes would end the RESPOND argument.
    return str(s).replace('|', '/').replace('"', '').replace("'", '')


def say(msg, error=False):
    gcode('RESPOND TYPE=%s MSG="%s"' % ('error' if error else 'echo', clean(msg)))


def cmd(action):
    # Prompt actions travel as ordinary RESPOND messages; the frontend parses them.
    gcode('RESPOND TYPE=command MSG="%s"' % action)


def spools():
    lst = post('/server/spoolman/proxy',
               {'request_method': 'GET', 'path': '/v1/spool'}) or []
    return sorted((s for s in lst if not s.get('archived')),
                  key=lambda s: int(s.get('id', 0)))


def describe(s):
    f = s.get('filament') or {}
    left = s.get('remaining_weight')
    text = '%s - %s - %s C' % (clean(f.get('name', '?')),
                               clean(f.get('material', '?')),
                               f.get('settings_extruder_temp', '?'))
    if left:
        text += ' - %.0f g' % float(left)
    return text


def load(want, how):
    for s in spools():
        if int(s.get('id', -1)) != want:
            continue
        t = (s.get('filament') or {}).get('settings_extruder_temp')
        if not t:
            say('Spole %d har ingen dysetemperatur i Spoolman - sett den der, '
                'eller bruk FILAMENT_LOAD SPOOL=%d TEMP=<grader>' % (want, want),
                error=True)
            return
        say('Laster spole %d (%s): %s' % (want, how, describe(s)))
        gcode('_FILAMENT_LOAD_RUN TEMP=%d SPOOL=%d' % (int(t), want))
        return
    say('Fant ingen spole med id %d i Spoolman (finnes ikke eller er arkivert)' % want, error=True)


def ask():
    lst = spools()
    if not lst:
        say('Ingen spoler registrert i Spoolman', error=True)
        return

    cmd('action:prompt_begin Last inn filament')
    cmd('action:prompt_text Velg spolen du laster inn. Temperaturen hentes fra Spoolman.')
    for s in lst:
        cmd('action:prompt_button %s|FILAMENT_LOAD SPOOL=%s|primary'
            % (describe(s), s.get('id')))
    cmd('action:prompt_footer_button Avbryt|_PROMPT_CLOSE|error')
    cmd('action:prompt_show')

    # For frontends that ignore the dialog: the same choice, readable in the console.
    say('Ingen aktiv spole. Velg i dialogen, paa Spoolman-siden i Mobileraker, '
        'eller med FILAMENT_LOAD SPOOL=nr:')
    for s in lst:
        say('  %s: %s' % (s.get('id'), describe(s)))
    gcode('MR_NOTIFY TITLE="Velg spole" MESSAGE="Ingen aktiv spole. Velg spolen '
          'paa Spoolman-siden og trykk Load igjen."')


detach()
try:
    if len(sys.argv) > 2 and sys.argv[1] == 'temp':
        load(int(sys.argv[2]), 'valgt')
    else:
        active = (get('/server/spoolman/spool_id') or {}).get('spool_id')
        if active:
            load(int(active), 'aktiv i Spoolman')
        else:
            ask()
except Exception as e:
    say('Spolevalg feilet: %s' % e, error=True)
