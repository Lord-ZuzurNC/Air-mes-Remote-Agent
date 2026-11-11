# Air-mes Remote Agent

A standalone physical device for talking to Hermes without touching a PC or
a phone. Form factor target: close to a Limitless Pendant. Screen + 4
physical buttons.

**Status: design phase.** Nothing is coded yet. This repo is a skeleton
while the hardware, the relay and the licence are still being decided.

## Interface

- **Power/Connect** — short press: connect over BLE. Long press: power
  on/off. In menu: confirm.
- **Talk** — push-to-talk: hold to talk, release to stop. In menu: down.
- **Stop** — short press: stop everything. Long press: mute/unmute the mic.
  In menu: up.
- **Menu** — short press: open settings. Long press: back.

## Architecture (decided)

Voice never travels over BLE.

1. The device runs STT locally (captured speech → text).
2. The text is sent over BLE to a relay.
3. The relay forwards the text over the internet to Hermes/PC.
4. The reply comes back the same way, read aloud by a local TTS on the
   device.

Topology: `device --BLE--> relay --internet--> PC/Hermes`. No direct
device-to-PC BLE link. Intended use: real remote access, not just on the
local network.

## Open questions

See `docs/DESIGN.md` for the detailed decisions and the open questions
(what the relay actually is, the STT firmware's licence, the tunnelling
strategy).

## Licence

Not decided yet.
