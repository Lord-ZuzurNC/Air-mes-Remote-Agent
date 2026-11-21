# Air-mes Remote Agent

- [Air-mes Remote Agent](#air-mes-remote-agent)
  - [Interface](#interface)
  - [Architecture (decided)](#architecture-decided)
  - [Hardware — fixed BOM](#hardware--fixed-bom)
  - [Repository layout](#repository-layout)
  - [Open / not yet validated](#open--not-yet-validated)
  - [Licence](#licence)

A standalone physical device for talking to Hermes without touching a PC or a phone.
Form factor target: close to a Limitless Pendant, round, no fixed wearing mechanism — pocket or necklace, whoever wears it decides.
> Screen + 4 physical buttons coming soon.

**Status: design phase, hardware ahead of firmware.**
No code exists yet, neither on the device nor in the companion app.
The mechanical shell and the PCB are past placeholder stage: a fixed component BOM, a parametric SolidCraft shell with two working halves, and a KiCad board floorplan validated by DRC.
`docs/DESIGN.md` is the source of truth for every decision below; this file only summarises it.

## Interface

- **Power/Connect** — short press: connect over BLE. Long press: power on/off. In menu: confirm.
- **Talk** — push-to-talk: hold to talk, release to stop. In menu: down.
- **Stop** — short press: stop everything. Long press: mute/unmute the mic. In menu: up.
- **Menu** — short press: open settings. Long press: back.

## Architecture (decided)

Voice never travels over BLE.

1. The device runs STT locally (captured speech → text), via `lokutor-ai/oido`.
2. The text is sent over BLE to a relay: the companion app on Lord's Android phone, not a fixed hub — it has to travel with him for the "real remote access" requirement below.
3. The relay forwards the text to Hermes/PC, by default over an embedded Tailscale/Headscale tunnel (`tsnet`); direct connection and plain LAN are user-selectable alternatives, not hard-wired to Lord's own setup.
4. The reply comes back the same way, read aloud by a local TTS (eSpeak-ng/Flite) on the device.

Topology: `device --BLE--> companion app --tsnet/direct/LAN--> PC/Hermes`.
No direct device-to-PC BLE link.
Intended use: real remote access, not just the local network.

The device has no awareness of Hermes at all — connectivity, configuration and firmware OTA (over BLE) all live in the companion app, never in the device firmware.

## Hardware — fixed BOM

Final, sourced references, not placeholders.
Full table, footprints and sourcing notes: `docs/DESIGN.md#components`.

| Part       | Ref                                                | Brand                                 |
| ---------- | -------------------------------------------------- | ------------------------------------- |
| MCU        | `ESP32-S3-WROOM-1-N16R8` (16 MB flash, 8 MB PSRAM) | Espressif Systems                     |
| Display    | `ET013TT1` — 1.3", 256×256, 2 grey levels, SPI     | E Ink (via Unisystem)                 |
| Microphone | `ICS-43434` (I2S MEMS)                             | TDK InvenSense                        |
| Speaker    | `CDS-20144` (1 W, 4 Ω)                             | Same Sky (Formerly CUI Devices)       |
| Battery    | `LP702030` / EEMB 350 mAh Li-Po, JST-PH            | EEMB Battery                          |
| Charge IC  | `TP4056`                                           | TPOWER                                |
| Fuel gauge | `MAX17048G+T10`                                    | Analog Devices Inc./Maxim Integratedz |
| USB-C      | `CB1.6(073)` 6-pin, charge-only                    | SHOU HAN                              |

## Repository layout

- `docs/DESIGN.md` — full decision log: Bluetooth, form factor, MCU, audio, enclosure, companion app, licence, UX state machine, charging/serviceability, BOM.
- `models/case/` — parametric SolidCraft shell, see `models/case/README.md`.
- `models/pcb/` — KiCad board floorplan v0.1, placement-only, see `models/pcb/README.md`.

## Open / not yet validated

- **PCB antenna clearance**: best case ~13.8 mm against a 15 mm Espressif target on a 60 mm shell. Geometry alone can't close this; needs a real prototype range test.
- **E-Ink screen mounting**: FPC ribbon routing, bend radius and a non-damaging retention method aren't finalised; the current shell isn't sealed against water/dust.
- **Battery/screen access split**: the shell doesn't yet decide whether it opens in one piece or splits front/back for independent battery and screen replacement.
- **Firmware and companion app**: neither has a single line of code yet. STT (Oído) is not real-time on one core (~8.7 s for a 4 s utterance); the UX "Thinking" state exists on paper, not in practice.
- UX timeouts (connect ~30 s, session inactivity, max Talk hold ~30-60 s) are starting values, expected to move once there's a real device to test against.

## Licence

Multi-licence, same pattern as Wizards Towers/turbofat. Full rationale: `docs/DESIGN.md#licence--decided-2026-11-09`.

- **Device firmware (includes Oído): GPL-3.0** — forced by Oído's own licence and GPLv3's anti-tivoization clause; the device must allow users to flash their own modified firmware.
- **Companion app (Android): MIT** — not contaminated by the firmware's GPL, since device and app only ever talk over BLE.
- **Oído's model weights: CC-BY-4.0 / CC-BY-SA-4.0**, cited in a `NOTICE` file.
- **Lord's own 3D models (shells): CC-BY-SA**, matching the "people remix it" intent.
