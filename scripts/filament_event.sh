#!/bin/bash
# Append a timestamped filament event.
#
# Why this exists: M118/RESPOND output never reaches klippy.log - it goes to the
# gcode response stream, which only Moonraker's size-limited gcode_store keeps.
# After the 2026-08-11 runout there was no durable record saying whether a pause
# was a runout or a manual one. This file is that record.

LOG=/home/hevort/printer_data/logs/filament_events.log

printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"
