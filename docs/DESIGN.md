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
  during use. A round 1.1" option already exists off the shelf (E Ink
  Mobius, 240×240, 4 grey levels, marketed specifically for watch faces).

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

**Reserve (2026-11-09): speaker size left open.** Same volumetric trade-off
as the battery — bigger speaker/better sound vs. less room left inside the
case. Lord will decide it once a 3D model of the enclosure makes the
available space visible, rather than guessing now.

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

- **Battery:** connector-based (JST-SH or JST-PH, standardising on one),
  not soldered wires. This is already how most retail Li-Po cells ship —
  not an extra constraint, just a default to lock in. Requires a
  removable access hatch/screwed panel in the shell (no glue, no
  ultrasonic welding).
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

## Open — nothing gets coded until these are settled

- **Volumetric budget — reference numbers for the 3D model, not a final
  decision (2026-11-09):**
  - ESP32-S3-WROOM-1-N16R8: 18 × 25.5 mm footprint, 3.1 mm thick. Fixed.
  - E-Ink Mobius display: ~32-35 mm outer flex footprint, 27.96 mm active
    round diameter, 0.5 mm panel (+ a cover lens, still TBD). Fixed panel.
  - MEMS mic: ~3.5×2.65×1 mm package — negligible volume regardless of
    exact part.
  - Speaker: 10-18 mm diameter, ~3-3.5 mm thick for wearable-grade micro
    speakers — range, size reserved for after the 3D model.
  - USB-C receptacle: ~8.5 mm wide × ~2.5-3 mm tall × ~6-7 mm deep, sits
    at the rim.
  - 4 tactile buttons + charge IC + fuel-gauge IC: a few mm each,
    negligible thickness.
  - Battery: thickness from <1 mm (small capacity) to ~6-7 mm+ (bigger
    capacity) for Li-Po pouch cells — reserved, decided last.
  - Custom round PCB (not a rectangular dev board): ~1-1.2 mm thick.
  - Shell wall: ~1.5-2 mm per side (plastic) or ~1 mm (metal).
  - **Sanity check:** stacking everything vertically would run
    ~13 mm (PCB + module + battery + walls + display), already inside the
    45-55 mm / 12-18 mm pocket-watch-style envelope. Laid out side-by-side
    on the PCB instead of stacked, the real minimum is closer to the
    tallest single part (module or speaker, ~3-3.5 mm) + PCB + walls —
    meaning there's real slack, not a tight squeeze, for picking a decent
    battery and speaker once arranged in CAD.
- **Battery capacity/size:** decided deliberately last among the electronics
  (2026-11-09) — it depends on the power draw and the leftover internal
  volume once everything else (MCU ✓, BLE ✓, display ✓, mic ✓, speaker type
  ✓ but size ⬜) is fixed.
