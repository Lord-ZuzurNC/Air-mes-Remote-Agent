# Design — Air-mes Remote Agent

Source of truth for this project. The general registry (`projets.md`, skill
`lord-contexte`) keeps a summary; this file is authoritative on the detail.

## Decided

- **No direct device-to-PC BLE link.** Topology:
  `device --BLE--> relay --internet--> PC/Hermes`.
- **Voice never travels over BLE.** STT runs locally on the device (speech →
  text), only text crosses BLE and then the internet. Reply text → local
  TTS on the device.
- **Talk button is push-to-talk only.** No toggle mode in v1.
- **Intended use: real remote access**, not just the local network.
- **BLE link to the relay must be as low-power as possible** while staying
  reliable enough for a real-time text link (Lord, 2026-11-09). Full BLE
  design: see the dedicated section below.
- **Relay = companion app on Lord's Android phone**, not a dedicated fixed
  hub (2026-11-09). A fixed hub can only reach the pendant within BLE range
  (~10-30 m), which would contradict the "real remote access, not just
  local network" requirement above — only something that travels with Lord
  (the phone, with its own mobile/Wi-Fi data) can satisfy it.
- **Android background BLE service:** standard pattern — ask the user to
  exempt the app from battery optimisation (and/or keep a persistent
  notification), same as other BLE/fitness apps do. Accepted risk: without
  that exemption the OS can kill the service.

## Bluetooth — decided

**Advertising:** no continuous advertising. The device only advertises when
the user short-presses Power/Connect, matching the interface spec above.
Biggest standby power lever — no radio running while idle.

**Connection:** once connected, the link stays up for a session (until
Power long-press or an inactivity timeout). Long connection interval by
default to save power; the device requests a shorter interval (connection
parameter update) while Talk is active, for latency, then reverts to the
long interval afterwards.

**GATT profile:** a custom service, not a standard one:
- a **Notify** characteristic, device → phone: STT-recognised text.
- a **Write** characteristic, phone → device: the reply text to speak.
- a **status** characteristic: battery level, mic muted/active.

**MTU:** negotiate a high ATT MTU (up to ~517 B, supported by most recent
Android phones) so a full sentence goes out in one radio transaction
instead of being fragmented — fewer radio events, less power.

**Security:** LE Secure Connections with **numeric comparison pairing**
(the device's screen can show the 6-digit code) rather than Just Works,
which is MITM-vulnerable. **Bonding** after first pairing so later
reconnections reuse stored keys instead of re-authenticating.

## Form factor & standby display — decided

**Device: round, bare, no fixed wearing mechanism** (2026-11-09). Lord will
showcase two carry modes — pocket (fob chain) and necklace — but the
device itself imposes neither; how people wear it is up to them.

**Standby shows the time** (optionally the date too) — makes the device
double as a real watch, with a Hermes connection behind it (2026-11-09).

This requirement decides the **display technology**, ahead of the
dedicated screen topic: a standard OLED/LCD can't show a static clock face
near-zero power, so the panel has to be a **reflective, low-power type**.

**Panel tech: grayscale E-Ink — decided (2026-11-09).** Not Memory LCD, not
color E-Ink:
- **Memory LCD vs E-Ink isn't actually a light-source question** — both are
  reflective and need ambient (or an optional add-on frontlight) to be read
  in the dark; neither emits its own light. That's not what decides this.
- **Color E-Ink is ruled out by refresh speed, not availability.**
  E Ink Spectra 6 (full 6-colour pigment, the variant with an existing
  round 1.69" panel) takes **7-19 s for a full refresh** — built for
  signage and price tags, explicitly static use. E Ink Kaleido 3 (colour
  filter over a monochrome Carta layer, used in colour e-readers) refreshes
  its black/white layer at normal e-reader speed but is still markedly
  slower in colour, and isn't known to exist in a small round panel.
  Either way: pressing Talk should flip the screen to a listening state
  near-instantly, and a multi-second colour refresh would feel broken for
  that, not just slow for the clock.
- **Grayscale E-Ink (Carta-class) gives fast partial refresh** (~300-450 ms,
  no full-panel flash needed for small UI changes) and zero draw between
  refreshes — the right fit for both the clock face and the status icon
  during use.

**Final panel pick: `ET013TT1` (E Ink, via Unisystem) — square, not round
(2026-11-11).** The round 1.1" panel named above as "already existing
off the shelf" (E Ink Mobius / Unisystem `ET011TT6`) turned out to be
**EOL at the manufacturer**, with no round grayscale equivalent sourceable
outside a B2B custom quote (SEEKINK and IDS Display both require a
project-based quote for round panels, not a stock buy). Checked and ruled
out as a workaround: round LCD modules (GC9A01-driven, widely available)
exist, but give up the whole point of E-Ink here — near-zero standby
power and sunlight readability — so staying on E-Ink and accepting a
square face was the better trade.
- `ET013TT1`: 1.3", 256×256, 2 grey levels, SPI. Active area 23.30×23.30 mm,
  outline 27.1×28.4×0.4 mm.
- **UX consequence, turned into a feature, not just absorbed as a
  compromise:** a square face reads as a screen, not a watch dial — so
  the face leans into a small animated character (Tamagotchi-style)
  that shows the time at rest and animates while listening/speaking,
  rather than an analog/digital clock trying to look round inside a
  square window. Detail to flesh out in the software/UX topic.

## MCU — decided

**ESP32-S3-WROOM-1-N16R8** (16 MB quad-SPI flash + 8 MB octal-SPI PSRAM,
that exact variant; 36 usable GPIO, -40 to 85 °C).

Chosen over ESP32-S3-WROOM-2-N32R16V (32 MB flash + 16 MB PSRAM, both
octal, 33 GPIO, -40 to 65 °C only): the extra memory isn't needed —
`lokutor-ai/oido`, the STT engine this project targets, is developed and
benchmarked on this exact WROOM-1-N16R8 board, and its latest version runs
its model entirely from flash, leaving the 8 MB PSRAM free. The WROOM-2's
extra headroom would cost 3 GPIO, a narrower thermal range, and a bigger,
pricier module for no concrete current need. Revisit only if the project
later needs several languages loaded at once, a separate wake-word engine
alongside full STT, or heavy local audio caching.

Open-vocabulary embedded STT is feasible on this chip: `lokutor-ai/oido`
(quantised Conformer-CTC Small, 3.7% WER on LibriSpeech test-clean, runs on
the two Xtensa LX7 cores at 240 MHz, no cloud).

Caveats:

- **Not real-time yet, upstream (software, not a hardware decision point):**
  per the project's own status notes, a 4-second utterance takes about
  8.7 s to come back as text on one core; two-core mode mis-transcribes on
  real silicon and is disabled. Streaming mode roughly halves that delay.
  Doesn't change any hardware pick made here — revisit in the UX/flow
  topic (how the device signals "thinking" during that wait).
- **Oído's firmware is GPL-3.0** (models are CC-BY/CC-BY-SA). Bundling it
  into the device firmware would likely make the whole firmware inherit the
  GPL. To settle alongside the project's overall licence choice.

Local TTS: eSpeak-ng or Flite. Robotic-sounding but good enough to read a
reply aloud.

## Audio — decided, one reserve

**Microphone: single digital MEMS mic (I2S or PDM), 16 kHz mono.** Not
analog electret (noisier, needs an ADC + gain stage). Not a mic array/
beamforming: Oído's engine has no spare compute for that on top of STT
inference (see the MCU caveats above — it isn't comfortably real-time on
one core, and two-core is disabled). Audio must be fed through Oído's
streaming API, not its batch `transcribe` call, which hangs on live
microphone input per the project's own README.

**Speaker: small dynamic speaker driven by an I2S DAC/amp (Class D), not a
piezo buzzer.** A piezo can beep but can't carry intelligible TTS speech.

**Final picks (2026-11-11):**
- **Microphone:** `ICS-43434` (TDK InvenSense, I2S MEMS) — replaces the
  originally-named INMP441, which DigiKey confirms is obsolete; this is
  their own listed replacement. 3.50×2.65×0.98 mm SMD package.
- **Speaker:** `CDS-20144` (Same Sky/CUI). Correction on shape: not round
  — it's an **oval frame, 20×14×3.2 mm**, 1 W, 4 Ω. The front-face layout
  (grille/port only, driver relocated to the back cavity, see the bug
  fix in the enclosure section) needs to account for this footprint, not
  a round one.

## Enclosure — decided (2026-11-09)

**Fixed mechanical envelope first.** Before any shell is designed, the
bare electronics module's outer dimensions, fastener/clip points, and the
position of buttons/screen/charge port are frozen into a single mechanical
interface. Every shell — official or remixed by anyone — mounts on that
same interface, so a new shell is a modelling exercise, not a redesign of
the electronics.

**Model family, all built on that interface:**
- **Base model:** a plain round "pure" shell, printable in PLA/PETG —
  the reference anyone can remix.
- **Derived plastic models (examples, also PLA/PETG):** a loop for a
  carabiner + chain, a two-loop version for cords, etc. Not an exhaustive
  list — people are expected to make their own variants off the base.
- **Derived metal models (examples, premium/optional):** ornate
  art-nouveau/rococo-style cases, up to a full hunter-case with a hinged
  lid and latch and a pocket-watch chain. Single-unit manufacturing route:
  lost-wax jewellery casting or metal 3D printing (DMLS/SLM, brass/bronze/
  stainless) — not the mass case manufacturers Lord first had in mind,
  which need volume to justify tooling. Hinge + latch is a modelling
  detail, not a blocker.

## Companion app architecture & connectivity — decided (2026-11-09)

**The device has no awareness of Hermes at all.** It only talks BLE text to
the phone: STT output going out, text-to-speak coming in. All Hermes
connectivity, device configuration, and firmware updates live in the
companion app, not the firmware. Keeps the device firmware small and
stable; evolving the integration means updating the app, not reflashing
the pendant.

**Firmware OTA: over BLE**, via a dedicated GATT service that streams
firmware chunks from the app — no need to bring up Wi-Fi on the chip just
for updates, keeps the device single-radio (BLE only).

**Connectivity to Hermes is a pluggable, user-chosen setting in the app**
— not hard-wired to Lord's own setup, so other people building this device
aren't forced into running a VPS:
1. **Tailscale/Headscale (default/recommended).** Embedded directly via
   `tsnet` (Tailscale's official embeddable library — real prior art
   exists for exactly this on Android, no separate Tailscale app needed).
   Joins a tailnet together with the home PC; zero public exposure,
   WireGuard end-to-end.
2. **Direct connection.** The user types in their own endpoint
   (IP/domain + port) — port-forward, reverse proxy, whatever they've set
   up. The app shows an explicit security warning when this mode is
   turned on. Includes an **SSL/TLS certificate verification option**:
   properly validates the server's cert chain by default, which reassures
   users who've set up a real certificate (e.g. Let's Encrypt); disabling
   it (self-signed/no cert) should carry its own, stronger warning.
3. **Local network.** Same code path as "Direct", just a LAN address —
   no extra engineering, just a documented use case of mode 2 for people
   who only ever use the device at home.

**Independent of the transport: a mandatory app-level auth token.**
Whichever mode is chosen, reachability alone (knowing the IP) must never
be the only barrier — the token is what actually protects the Hermes
endpoint.

## Licence — decided (2026-11-09)

Multi-licence, same pattern as Wizards Towers/turbofat:
- **ARA firmware (device, includes Oído): GPL-3.0.** Forced by Oído's own
  licence plus the anti-tivoization clause (GPLv3 §6) — a single
  monolithic MCU binary means the whole firmware inherits GPL, not just
  Oído's portion, and the device must allow users to install their own
  modified firmware (no locked secure boot). Fits Lord's own ethos anyway.
- **Companion app (Android): MIT.** Not contaminated by the firmware's GPL
  — app and device only talk over BLE, no linking.
- **Oído's model weights: kept under their own CC-BY-4.0/CC-BY-SA-4.0**
  (the `stream` model used for live capture is CC-BY-SA) — cited correctly
  with a `NOTICE` file, same convention as Wizards Towers' `CREDITS.md`.
- **Lord's own 3D models (shells): CC-BY-SA.** Matches the "people remix
  it" intent and the CC-BY-SA already inherited from Oído's model weights.

## UX flow / state machine — decided (2026-11-09, timeouts to evolve)

**States:** Off → Standby (clock shown, no BLE) → Connecting (advertising,
on Power/Connect short-press; numeric-comparison pairing the first time,
bonding reused after) → Connected/session idle (clock + small connected
icon, long BLE interval) → Listening (Talk held, mic + streaming STT, BLE
switches to short interval) → Thinking (Talk released; one unified
"processing" state covering both Oído's STT tail latency and the
Hermes round-trip — no need to expose the internal steps to the user) →
Speaking (reply received, local TTS) → back to Connected/idle. Plus an
Error/timeout state (Talk pressed with no connection, or no reply in time).

**Buttons per context:**
- **Power/Connect:** Standby→Connecting (short); Connected→Off (long);
  in menu = validate.
- **Talk:** push-to-talk, only live in Connected/idle (otherwise shows an
  error icon rather than doing nothing silently).
- **Stop:** interrupts from any active state (Listening/Thinking/Speaking)
  back to Connected/idle — not to Standby, the BLE session stays open.
  Long press: mute/unmute mic, a persistent state shown by its own icon,
  blocks Talk while active.
- **Menu:** short = open settings, long = back. Only live from Standby or
  Connected/idle — disabled during Listening/Thinking/Speaking so it can't
  interrupt an interaction by accident. In menu: Talk/Stop become down/up,
  Power/Connect becomes validate.

**Timeouts (starting values, expected to change with real use):**
connecting timeout ~30 s → back to Standby; session inactivity timeout
(a few minutes) → auto-disconnect to save power; max Talk hold duration
~30-60 s (stuck-button safety net).

## Platform direction — kept in mind, not v1 scope (2026-11-09)

Lord's longer-term idea: ARA/the companion app could become a platform
that plugs into more than Hermes — Claude Code Cloud, Gemini Cloud,
OpenBot, etc. Not committing scope now, but designing the app's backend
connector as a swappable interface from the start avoids a rewrite later.
Two distinct, loosely-coupled layers:
- **Transport** (how to reach a self-hosted backend): the
  Tailscale/Headscale · Direct · LAN choice already decided above — this
  is specifically for self-hosted backends like Hermes.
- **Backend/harness** (who answers the text): Hermes first. A future
  cloud backend (Claude Code Cloud, Gemini Cloud...) would plug in as its
  own connector with its own reachability and auth (typically just direct
  HTTPS to the provider's endpoint + their own API key/OAuth) — it
  wouldn't need the tailnet machinery at all.

## Charging & serviceability — decided (2026-11-09)

**Right-to-repair, extended from firmware to hardware.** Same spirit as
the GPLv3 reflash requirement and the remixable shells: the battery and
the screen must both be user-replaceable without soldering.

- **Battery:** connector-based, **JST-PH (2.0 mm pitch)** — not JST-SH.
  Correction (2026-11-11): JST-SH is the norm on sub-1 mm-thick cells, but
  every real 300-350 mAh Li-Po found in sourcing (EEMB, LaskaKit) ships on
  JST-PH; standardising on what's actually available beats an abstract
  pick. Not soldered wires either way — already how most retail Li-Po
  cells ship. Requires a removable access hatch/screwed panel in the
  shell (no glue, no ultrasonic welding).
- **Screen:** connects via FPC flex cable + ZIF connector (how small
  e-ink/e-reader panels normally attach) instead of a glued/soldered
  chip-on-flex module — also close to free once that connector type is
  chosen. Caveat: an FPC-ZIF connector is more delicate than the
  battery's JST connector — solder-free, but "careful hands with a
  spudger", not "unplug like a charger".
- **Enclosure consequence (for the 3D model, not resolved yet):** the
  screen sits on the front face, the battery is more naturally accessed
  from the back — two access zones, unless the shell is designed to split
  fully in two (front face with the screen attached, main body with PCB +
  battery). To decide visually in CAD, like the speaker/battery size.
- **PCB split:** one soldered-once core board (ESP32-S3 module with its
  integrated BLE, USB-C, speaker, mic) + two connector-based swappable
  parts (screen, battery). Nothing else is meant to be field-replaceable.
- **Wireless charging: optional module, plastic shells only (confirmed).**
  A Qi receiver coil + IC needs a metal-free charging face, for the same
  reason the BLE antenna needs a metal-free window — incompatible with
  the metal shell family without a second cutout, which would compromise
  the ornate metal look. USB-C remains the universal baseline on every
  shell; Qi is an add-on for whoever wants it on a plastic build.

## Components — final BOM, fixed (2026-11-11)

Every part below is a confirmed, sourceable reference, not a placeholder —
the next 3D modeling pass models the enclosure around these real
footprints instead of guessed boxes.

| Part | Ref | Footprint | Notes |
|---|---|---|---|
| MCU module | `ESP32-S3-WROOM-1-N16R8` | 18 × 25.5 × 3.1 mm | PCB antenna variant (not `-1U`). LCSC C2913202 (4.6€), DigiKey (6€). |
| Display | `ET013TT1` (E Ink, via Unisystem) | outline 27.1×28.4×0.4 mm, active 23.30×23.30 mm | Square, 256×256, 2 grey levels, SPI. Quote-based order. |
| Microphone | `ICS-43434` (TDK InvenSense) | 3.50×2.65×0.98 mm | I2S MEMS. DigiKey 3.48€. |
| Speaker | `CDS-20144` (Same Sky/CUI) | oval 20×14×3.2 mm | 1 W, 4 Ω. Driver lives in the back cavity; front face carries only a small acoustic port (bug found/fixed 2026-11-11, previous round-pocket placeholder overflowed the shell wall). DigiKey 4.33€. |
| Battery | `LP702030` / EEMB 350 mAh | 30 × 20 × 7 mm, JST-PH (2.0 mm) | 3.7 V Li-Po. Amazon (10.99€). Est. life: ~6 d connected-idle, ~4-5 d at 1-2 uses/h, ~2 h continuous non-stop use — estimated from the power budget, not measured. |
| Charge IC | `TP4056` | SOIC-8 | LCSC C382139 (0.11€/unit at qty 5). |
| Fuel gauge | `MAX17048G+T10` | — | DigiKey 4.09€. |
| USB-C receptacle | `SHOU HAN TYPE-C 6P CB1.6(073)`, LCSC C2858274 | 8.94×3.16mm body, ~6.8mm deep, 6-pin (VBUS×2, GND×2, CC1, CC2) | Decided (2026-11-11): charge-only, no D+/D- — firmware OTA is BLE, so the port never needs data lines. Rated 5V/3A. |
| Custom PCB | — | ~1-1.2 mm thick, outline TBD | No longer constrained to round/rectangular — shaped around the battery/speaker/PCB layout once modeled (PCBWay and similar prototype houses fab any outline at no real premium). |

**Suppliers, consolidated on purpose:** LCSC (MCU, charge IC) + DigiKey
(mic, speaker, fuel gauge) as the two main hubs; Amazon only for the
battery (neither LCSC nor DigiKey/Mouser had a matching cell shippable to
France at this capacity/connector).

