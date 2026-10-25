#!/usr/bin/env python3
"""Warn if no Spoolman spool is selected, or if the selected one is too light.

Klipper cannot read Moonraker's spool state, so this runs as a shell command and
asks Moonraker directly. That way the check is correct no matter where the spool
was chosen - the Klipper macro, Mainsail's Spoolman panel, or Spoolman itself.

Called from PRINT_START. Warns only; it never stops a print.
"""

import atexit
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = 'http://127.0.0.1:7125'


def detach():
    # RUN_SHELL_COMMAND holds Klipper's gcode lock until this process exits, and
    # every gcode posted below queues behind that lock. Waiting for them here
    # stalled PRINT_START until each request timed out, and messages after the
    # first were lost. Hand the work to a child and let Klipper go at once; the
    # child drops the inherited pipes so Klipper is not left waiting for EOF.
    if os.fork():
        os._exit(0)
    os.setsid()
    fd = os.open(os.devnull, os.O_RDWR)
    for n in (0, 1, 2):
        os.dup2(fd, n)


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)['result']


def post(path, payload, timeout=10):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get('result')


def gcode(script):
    try:
        # Queued behind PRINT_START, which can run through a long heat soak.
        post('/printer/gcode/script', {'script': script}, timeout=3600)
    except Exception:
        pass


def say(msg, error=False):
    # Straight to stdout: with verbose on, gcode_shell_command shows each line
    # in the console at once. A RESPOND would queue behind PRINT_START and show
    # up minutes later, after Z tilt and probing.
    print(('ADVARSEL: ' if error else '') + msg, flush=True)


# Push notifications must go through gcode, so they still wait for PRINT_START.
# They are sent last, from a detached child, so Klipper is not held up.
PENDING = []


def notify(title, message):
    PENDING.append('MR_NOTIFY TITLE="%s" MESSAGE="%s"'
                   % (title.replace('"', "'"), message.replace('"', "'")))


@atexit.register
def _send_pending():
    if not PENDING:
        return
    sys.stdout.flush()
    detach()
    for script in PENDING:
        gcode(script)


# --- which spool is active -------------------------------------------------
try:
    spool_id = get('/server/spoolman/spool_id').get('spool_id')
except Exception as e:
    say('Spoolman: naadde ikke Moonraker (%s)' % e, error=True)
    sys.exit(0)

if not spool_id:
    say('INGEN SPOLE VALGT i Spoolman - forbruket blir ikke registrert', error=True)
    notify('Ingen spole valgt',
           'Utskriften er startet uten aktiv spole. Forbruket registreres ikke i Spoolman.')
    sys.exit(0)

# --- how much is left on it ------------------------------------------------
try:
    spool = post('/server/spoolman/proxy',
                 {'request_method': 'GET', 'path': '/v1/spool/%d' % spool_id})
    remaining = float(spool.get('remaining_weight') or 0)
    name = (spool.get('filament') or {}).get('name', 'ukjent')
except Exception as e:
    say('Spoolman: fikk ikke lest spole %s (%s)' % (spool_id, e), error=True)
    sys.exit(0)

# --- what the job needs ----------------------------------------------------
try:
    stats = get('/printer/objects/query?print_stats')['status']['print_stats']
    filename = stats.get('filename') or ''
    if not filename:
        say('Spoolman: %s, %.0f g igjen' % (name, remaining))
        sys.exit(0)
    meta = get('/server/files/metadata?filename=' + urllib.parse.quote(filename))
except Exception as e:
    say('Spoolman: %s, %.0f g igjen (fant ikke jobbdata: %s)' % (name, remaining, e))
    sys.exit(0)

needed = float(meta.get('filament_weight_total') or 0)
est_time = float(meta.get('estimated_time') or 0)
layers = int(meta.get('layer_count') or 0)
lh = float(meta.get('layer_height') or 0)
fh = float(meta.get('first_layer_height') or lh)

if needed <= 0:
    say('Spoolman: %s, %.0f g igjen (jobben oppgir ingen vekt)' % (name, remaining))
    sys.exit(0)

# --- enough? ---------------------------------------------------------------
if remaining >= needed:
    say('Spoolman: %s - %.0f g igjen, jobben trenger %.0f g. OK.'
        % (name, remaining, needed))
    sys.exit(0)

# --- not enough: estimate where it stops -----------------------------------
# Linear in filament used, which assumes every layer weighs the same. Infill and
# solid layers break that, so treat the numbers as indicative.
frac = remaining / needed
secs_left = est_time * frac
when = datetime.datetime.now() + datetime.timedelta(seconds=secs_left)
layer = max(1, int(round(layers * frac)))
height = fh + (layer - 1) * lh
hrs, rem = divmod(int(secs_left), 3600)
mins = rem // 60

short = ('%s: %.0f g igjen, trenger %.0f g - tom ca %s'
         % (name, remaining, needed, when.strftime('%H:%M')))
detail = ('Spolen rekker ikke jobben. Ca %d t %02d min ut i utskriften, '
          'rundt lag %d av %d (ca %.1f mm hoeyde), kl %s.'
          % (hrs, mins, layer, layers, height, when.strftime('%H:%M')))

say('FOR LITE FILAMENT - ' + short, error=True)
say(detail, error=True)
notify('For lite filament', detail)
