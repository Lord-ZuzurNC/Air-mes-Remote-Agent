# Design — Air-mes Remote Agent

Source of truth for this project. The general registry (`projets.md`, skill
`lord-contexte`) keeps a summary; this file is authoritative on the detail.

## Decided

- **No direct device-to-PC BLE link.** Topology:
  `device --BLE--> relay --internet--> PC/Hermes`.
- **STT and TTS run on the phone, not on the device** (Lord, 2026-11-24).
  The device is a BLE audio terminal: microphone audio goes out, reply
  audio comes in. Only text crosses the internet. No speech model and no
  speech synthesiser in the firmware. Pipeline: see *Audio pipeline*.
- **Talk button is push-to-talk only.** No toggle mode in v1.
- **Intended use: real remote access**, not just the local network.
- **BLE link to the relay must be as low-power as possible** while
  carrying real-time audio in both directions during an exchange. Full
  BLE design: see the dedicated section below.
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
default to save power; the device requests a short interval (connection
parameter update, 15 ms target) from the Talk press until the reply has
finished playing, then reverts to the long interval. A parameter update
only takes effect several connection events later, at the old interval:
the device buffers microphone audio from the press and catches up once
the short interval is in place (*Audio pipeline*).

**GATT profile:** a custom service, not a standard one:
- **audio up** — Notify, device → phone: microphone audio frames.
- **audio down** — Write Without Response, phone → device: reply audio
  frames.
- **control** — Write + Notify: talk start/stop, stop/abort, codec id,
  and the device's receive credits for audio down (the flow control that
  makes Write Without Response safe).
- **status** — Read + Notify: battery level, mic muted/active.

**MTU and packet length:** ATT MTU of 247 B or more, with LE Data Length
Extension (251 B link-layer payload). One audio frame is 244 B, sized to
travel in exactly one link-layer packet; a higher MTU (up to 517 B) is
accepted but brings nothing for audio. Without Data Length Extension the
link cannot carry the audio (see the numbers below): the device reports an
error instead of streaming.

**PHY:** 2M requested, 1M accepted. The budget below is made on 1M.

**Link budget — numbers, not measured on this hardware:**

| Quantity                                                                    | Value                 | Source                                                                                         |
| --------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------- |
| Audio stream, each direction (never both at once)                           | 65 kbit/s (8.1 kB/s)  | 33.3 frames/s × 244 B, see *Audio pipeline*                                                    |
| ESP32-S3 ↔ ESP32-S3, notify, 1M PHY                                         | ~755 kbit/s           | Espressif, `examples/bluetooth/nimble/throughput_app`: shield box, 7.5 ms interval, MTU 512, DLE 251 |
| same, write                                                                 | ~753 kbit/s           | same                                                                                           |
| same, 2M PHY                                                                | ~1.35 / ~1.34 Mbit/s  | same                                                                                           |
| Floor: one 244 B packet per 15 ms connection event                          | 130 kbit/s            | arithmetic                                                                                     |
| No Data Length Extension: 4–6 packets of 20 B per 15 ms event               | 43–64 kbit/s          | arithmetic                                                                                     |
| Raw PCM 16 kHz / 16 bit, for comparison                                     | 256 kbit/s            | arithmetic                                                                                     |

The stream uses 8.6 % of what Espressif measured between two ESP32-S3 and
50 % of the one-packet-per-event floor. Raw PCM would use 34 % of the
measured figure and does not fit under the floor. **Not measured: the
throughput between this module and an Android phone.** Android grants
11.25–15 ms under `CONNECTION_PRIORITY_HIGH` and decides itself how many
packets fit in an event; no published ESP32-S3 ↔ Android figure was found.

**Latency:** a frame is 30 ms of audio and waits at most one connection
interval (15 ms): the phone is under 50 ms behind the microphone, so when
Talk is released the utterance is already on the phone. Reply playback
starts once 5 frames (150 ms) are buffered on the device.

**Security:** LE Secure Connections with **numeric comparison pairing**
(the device's screen can show the 6-digit code) rather than Just Works,
which is MITM-vulnerable. **Bonding** after first pairing so later
reconnections reuse stored keys instead of re-authenticating.

## Form factor & standby display — decided

**Superseded (2026-11-21): shape is rectangular, not round.** Reason:
the ESP32-S3's antenna keep-out (15 mm, see MCU section) is directional,
not radial — a round shell has to inflate its whole diameter to satisfy
a clearance that only matters in one direction, a rectangle only needs to
grow on the side that needs it. Carry modes below are unchanged by this.
Geometry reset to zero in `models/case/README.md` — no numbers from the
round study (v0.4–v0.8, Ø58 × 12.7 mm) carry over.

~~**Device: round, bare, no fixed wearing mechanism** (2026-11-09).~~ Lord will
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

**Panel pick as of 2026-11-11: `ET013TT1` (E Ink, via Unisystem) — square, not round.** The round 1.1" panel named above as "already existing
off the shelf" (E Ink Mobius / Unisystem `ET011TT6`) turned out to be
**EOL at the manufacturer**, with no round grayscale equivalent sourceable
outside a B2B custom quote (SEEKINK and IDS Display both require a
project-based quote for round panels, not a stock buy). Checked and ruled
out as a workaround: round LCD modules (GC9A01-driven, widely available)
exist, but give up the whole point of E-Ink here — near-zero standby
power and sunlight readability — so staying on E-Ink and accepting a
square face was the better trade.

**Superseded, re-picked (2026-11-21):** now that the case itself is
rectangular, not round, the square-only constraint that justified
`ET013TT1` no longer holds. `ET013TT1` is dropped.

**Final panel pick: `GDEY0213B74` (Good Display) — bare panel, no touch,
no front-light.** Genuinely rectangular, commodity stock (not a B2B
quote): SSD1680Z controller, 2.13", 250×122 px, SPI, 4 grayscale, 24-pin
FPC. Active area 48.55×23.7 mm, outline 59.2×29.2×1.0 mm, partial
refresh ~0.4 s. **Caution logged (2026-11-21):** the first link Lord sent was
`GDEY0213B74-FT11` — a capacitive-touch + front-light variant repackaged
as a Raspberry Pi HAT (40-pin GPIO header, its own driver board) — wrong
part, not embeddable on a custom PCB via FPC/ZIF. Corrected to the bare
`GDEY0213B74` before sourcing/BOM lock.
- **UX consequence, turned into a feature, not just absorbed as a
  compromise:** a square face reads as a screen, not a watch dial — so
  the face leans into a small animated character (Tamagotchi-style)
  that shows the time at rest and animates while listening/speaking,
  rather than an analog/digital clock trying to look round inside a
  square window. Detail to flesh out in the software/UX topic.

## MCU — decided

**ESP32-S3-WROOM-1-N16R8** (16 MB quad-SPI flash + 8 MB octal-SPI PSRAM;
18 × 25.5 × 3.1 mm, PCB antenna). Per Espressif's module datasheet: 33
usable GPIO on this variant (IO35, IO36, IO37 are taken by the octal
PSRAM; the floorplan uses none of them) and −40 to 65 °C ambient (85 °C
only with PSRAM ECC enabled, which costs 1/16 of the PSRAM).

**It is larger than the firmware needs.** With no speech model on the
device, the load is the BLE stack, two audio buffers, the display driver,
four buttons and the fuel gauge:

| Resource                   | Need                                                                                                                                                         | N16R8 has            | Smallest variant that fits            |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------- | ------------------------------------- |
| Flash                      | two OTA application slots (firmware update is over BLE) + NVS/bonding data + character sprites. Application estimated under 1.5 MB (ESP-IDF, NimBLE, drivers); a full 250×122 frame at 2 bit/px is 7.6 kB | 16 MB                | 4 MB (two 1.9 MB slots); 8 MB with room |
| RAM, audio up              | 3 s of ADPCM held while the connection interval switches: 24 kB                                                                                              | 512 kB SRAM in the chip | internal SRAM                         |
| RAM, audio down            | 2 s of ADPCM: 16 kB; I2S DMA and one decoded frame: under 8 kB                                                                                               | same                 | internal SRAM                         |
| RAM, display               | two 1-bit planes of 250×122 (SSD1680): 2 × 4 kB, plus one working copy                                                                                       | same                 | internal SRAM                         |
| RAM, BLE stack, RTOS, tasks | estimated 100–150 kB (one connection, peripheral role only)                                                                                                  | same                 | internal SRAM                         |
| PSRAM                      | none                                                                                                                                                         | 8 MB                 | no PSRAM                              |

The buffer sizes are arithmetic from the audio format; the application
size and the stack's RAM are estimates, not a build — there is no
firmware yet. Even at twice those estimates the total stays inside
512 kB of SRAM and a 4 MB flash.

**Kept anyway.** `ESP32-S3-WROOM-1-N4` or `-N8` (no PSRAM) would be
enough. Every `ESP32-S3-WROOM-1` variant has the same outline, land
pattern and pinout, so the choice changes neither the board nor the case;
the N16R8 is a superset except for the three GPIO and the temperature
range above. What it costs: about 1.5 € per module over an N4 (Mouser list prices, 2026-11), and 140 µA
more in light sleep for the 8 MB PSRAM (Espressif's ESP32-S3 datasheet,
table 5-10 note). What it gives: a whole reply can be buffered on the
device (60 s of ADPCM is 480 kB), and OTA slots are never tight. The
firmware must not depend on PSRAM, so that a build on an N4/N8 works.

## Audio — decided, one reserve

**Microphone: single digital MEMS mic (I2S), 16 kHz mono.** Not analog
electret (noisier, needs an ADC + gain stage). Not a mic array: one
microphone at push-to-talk distance, and the recogniser on the phone
takes 16 kHz mono.

**Speaker: small dynamic speaker driven by an I2S DAC/amp (Class D), not a
piezo buzzer.** A piezo can beep but can't carry intelligible speech.

**Final picks (2026-11-11):**
- **Microphone:** `ICS-43434` (TDK InvenSense, I2S MEMS) — replaces the
  originally-named INMP441, which DigiKey confirms is obsolete; this is
  their own listed replacement. 3.50×2.65×0.98 mm SMD package. At 16 kHz
  it runs in its low-power mode (6.25–18.75 kHz, 230 µA).
- **Speaker:** `CDS-20144` (Same Sky/CUI). Correction on shape: not round
  — it's an **oval frame, 20×14×3.2 mm**, 1 W, 4 Ω. The front-face layout
  (grille/port only, driver relocated to the back cavity, see the bug
  fix in the enclosure section) needs to account for this footprint, not
  a round one.

## Audio pipeline — decided (2026-11-24)

```
Talk held:   mic → I2S 16 kHz/16 bit → IMA ADPCM → BLE notify → phone: STT → text → Hermes
Reply:       Hermes → text → phone: TTS → 16 kHz → IMA ADPCM → BLE write → decode → I2S → amp → speaker
```

**One format in both directions: 16 kHz, mono, 16 bit, IMA ADPCM at
4 bit/sample = 64 kbit/s.** 16 kHz both ways because the microphone and
the amplifier share one I2S clock pair on the board, and because it is
the recogniser's native rate. The synthesiser produces 24 kHz; the phone
resamples before sending.

**Frame:** 244 B = 4 B header (sequence number, ADPCM predictor and step
index, so every frame decodes on its own and a lost frame costs 30 ms,
not the rest of the utterance) + 240 B = 480 samples = 30 ms. 33.3
frames/s, 8.1 kB/s.

**Why ADPCM:**

| Codec                | Bit rate at 16 kHz mono | Cost on the ESP32-S3 (Espressif `esp_audio_codec` table, ESP32-S3R8)                  | Verdict                                                                                                  |
| -------------------- | ----------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Raw PCM              | 256 kbit/s              | none                                                                                    | 34 % of the best measured link, above the one-packet-per-event floor; four times the radio time          |
| **IMA ADPCM**        | **64 kbit/s**           | encode 2.69 % CPU at 48 kHz stereo (a sixth of that at 16 kHz mono), 0.01 kB            | **picked** — fits under the floor with 2× margin, a few dozen lines of code each side, no library         |
| G.722                | 64 kbit/s               | encode 9.74 % CPU, 20.8 kB                                                              | same bit rate as ADPCM for more CPU and RAM                                                              |
| Opus                 | 16–32 kbit/s            | encode 24.9 % CPU at 48 kHz stereo, complexity 0; 29.4 kB                               | fallback — a third of the radio time, but a library on both sides                                         |
| LC3                  | 32 kbit/s               | encode 46.57 % CPU at 48 kHz stereo                                                     | heavier than Opus for a higher bit rate                                                                  |

IMA ADPCM at 16 kHz / 16 bit over BLE notifications is what voice remote
controls already do (TI application report SWRA506). The control
characteristic carries a codec id so that Opus can replace it without a
new GATT layout. Two things would trigger that: a measured phone link
under about 100 kbit/s, or ADPCM noise measurably degrading recognition.
Neither is measured.

**A few seconds of speech:** 5 s is 40 kB of ADPCM (160 kB raw), sent as
it is spoken; 30 s is 240 kB.

**Flow, device side:**
- *Up.* Capture starts at the Talk press into a 3 s buffer (24 kB),
  drained into notifications as fast as the link takes them. Release
  sends the remainder, then a talk-stop on the control characteristic.
- *Down.* The device grants credits (frames it has room for); the phone
  writes only against credits. Playback starts at 5 buffered frames
  (150 ms). On an underrun the device plays silence and keeps the stream.
  A 2 s buffer (16 kB) is enough; nothing requires PSRAM.
- *Stop* drops both buffers and sends an abort, so the phone stops
  synthesising and sending.
- The amplifier's `SD_MODE` goes to a GPIO: shut down (0.6 µA) whenever
  the device is not speaking. Left high it draws 2.4 mA while the I2S
  clock runs for the microphone, and 340 µA with the clock stopped.

## Enclosure — decided (2026-11-09)

**Fixed mechanical envelope first.** Before any shell is designed, the
bare electronics module's outer dimensions, fastener/clip points, and the
position of buttons/screen/charge port are frozen into a single mechanical
interface. Every shell — official or remixed by anyone — mounts on that
same interface, so a new shell is a modelling exercise, not a redesign of
the electronics.

**Model family, all built on that interface:**
- **Base model (reset 2026-11-21, now rectangular, not round):** a plain
  rectangular "pure" shell, printable in PLA/PETG — the reference anyone
  can remix. 90.8 × 33.8 × 12.5 mm. Orientation words (Lord, 2026-11-21):
  the end with the two plastic hooks is the **top** (antenna end), the
  end with the two screws is the **bottom**; USB-C on the right long
  wall. See `models/case/README.md` for the live geometry state.
- **Derived plastic models (examples, also PLA/PETG):** a loop for a
  carabiner + chain, a two-loop version for cords, etc. Not an exhaustive
  list — people are expected to make their own variants off the base.
- **Derived metal models (examples, premium/optional):** ornate
  art-nouveau/rococo-style cases, up to a full hunter-case with a hinged
  lid and latch and a pocket-watch chain. Single-unit manufacturing route:
  lost-wax jewellery casting or metal 3D printing (DMLS/SLM, brass/bronze/
  stainless) — not the mass case manufacturers Lord first had in mind,
  which need volume to justify tooling. Hinge + latch is a modelling
  detail, not a blocker. Note (2026-11-21): a rectangular case reads less
  like jewellery than the round pendant did — the ornate/hunter-case line
  loses some of its charm; Lord has accepted that trade for the antenna
  clearance gain.

## Companion app architecture & connectivity — decided (2026-11-09)

**The device has no awareness of Hermes at all, nor of speech
recognition or synthesis.** It only exchanges audio frames with the phone
over BLE: microphone audio going out, reply audio coming in. Speech
engines, Hermes connectivity, device configuration and firmware updates
all live in the companion app, not the firmware. Keeps the device
firmware small and stable; evolving the integration or changing a speech
engine means updating the app, not reflashing the pendant.

**Speech engines — on the phone, user-chosen (2026-11-24).** The app
decodes the device's ADPCM to 16 kHz PCM, transcribes it, sends the text
to Hermes, synthesises the reply and streams it back as ADPCM.

| Role | Engine                                                                 | Licence    | What its own documentation states                                                                                                                                                         |
| ---- | ---------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| STT  | **Whistle** (Cactus Compute), through the `cactus` engine's C API      | Apache-2.0 | 16.9 MB single file, CPU only; English, German, French, Spanish, Italian, Dutch, Polish; input 16 kHz mono; one pass up to 30 s, windowed beyond; Android among the prebuilt targets       |
| TTS  | **Babylon.cpp** (Mobile Artificial Intelligence), Kokoro engine        | MIT        | C/C++ library on ONNX Runtime, `libbabylon.so` for Android arm64-v8a; Kokoro output 24 kHz; phonemes from Open Phonemizer; `babylon_kokoro_tts` returns a complete WAV, no streaming call |

Requirements on the app that follow from those two columns:
- **Transcribe on release, not while listening.** Whistle documents no
  streaming mode. Audio is accumulated as it arrives; because it arrives
  in real time, transcription starts the moment Talk is released.
- **Talk hold limit and Whistle's 30 s pass** are the same order: keep the
  hold limit at 30 s unless windowed transcription is shown to hold up.
- **Synthesise sentence by sentence.** Babylon returns whole files; the
  app splits the reply so the first sentence is playing while the next
  ones are synthesised. Each is resampled 24 → 16 kHz, ADPCM-encoded and
  sent against the device's credits.
- **Abort** on the device's Stop: cancel synthesis and stop sending.
- **Engine choice is a setting in the app.** One engine per role is
  active, chosen by the user; **no automatic cloud fallback**. The device
  neither knows nor cares which engine is selected.

Not verified from either project's documentation, to measure on the real
phone: Whistle's and Kokoro's speed on an Android arm64 CPU (Whistle's
published timings are on an Apple M4 Pro; Babylon publishes none).

**French through Babylon: confirmed, one voice.** `voices/kokoro/fr-FR-siwis.bin`
exists in Babylon.cpp's repository (verified 2026-11-24, same commit as
every other shipped voice). It is the only French voice currently shipped
— Kokoro's upstream model supports more, so additional French voices may
follow, but today there is exactly one to pick from.

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

## Licence — decided (2026-11-09), firmware open (2026-11-24)

Multi-licence, same pattern as Wizards Towers/turbofat:
- **ARA firmware (device): not chosen.** Nothing in the firmware forces a
  licence any more: it contains no speech engine and no model weights,
  only Lord's own code on ESP-IDF (Apache-2.0). The GPL-3.0 constraint
  that came with Oído is gone with Oído.
- **Companion app (Android): MIT.** It links Whistle/`cactus`
  (Apache-2.0) and Babylon.cpp (MIT), both compatible with MIT; their
  notices and those of the model files they load go in a `NOTICE` file,
  same convention as Wizards Towers' `CREDITS.md`.
- **Lord's own 3D models (shells): CC-BY-SA.** Matches the "people remix
  it" intent.

## UX flow / state machine — decided (2026-11-09, timeouts to evolve)

**States:** Off → Standby (clock shown, no BLE) → Connecting (advertising,
on Power/Connect short-press; numeric-comparison pairing the first time,
bonding reused after) → Connected/session idle (clock + small connected
icon, long BLE interval) → Listening (Talk held, mic audio streamed to
the phone, BLE switches to short interval) → Thinking (Talk released;
one unified "processing" state covering the phone's STT, the Hermes
round-trip and the synthesis of the first sentence — no need to expose
the internal steps to the user) → Speaking (reply audio arriving from
the phone and playing) → back to Connected/idle, long BLE interval. Plus
an Error/timeout state (Talk pressed with no connection, link lost during
an exchange, or no reply in time).

**Buttons per context:**
- **Power/Connect:** Standby→Connecting (short); Connected→Off (long);
  in menu = validate.
- **Talk:** push-to-talk, only live in Connected/idle (otherwise shows an
  error icon rather than doing nothing silently).
- **Stop:** interrupts from any active state (Listening/Thinking/Speaking)
  back to Connected/idle — not to Standby, the BLE session stays open.
  It also tells the phone to abort (see *Audio pipeline*). Long press: mute/unmute mic, a persistent state shown by its own icon,
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
the user-reflashable firmware and the remixable shells: the battery and
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
- **Enclosure consequence — decided (2026-11-21): full split.** The
  bezel carries the screen and the PCB, the bottom shell is the lid with
  the battery and speaker in it; two screws out and both are reachable.
- **PCB split:** one soldered-once core board (ESP32-S3 module with its
  integrated BLE, USB-C, speaker, mic) + two connector-based swappable
  parts (screen, battery). Nothing else is meant to be field-replaceable.
- **Wireless charging: optional module, plastic shells only (confirmed).**
  A Qi receiver coil + IC needs a metal-free charging face, for the same
  reason the BLE antenna needs a metal-free window — incompatible with
  the metal shell family without a second cutout, which would compromise
  the ornate metal look. USB-C remains the universal baseline on every
  shell; Qi is an add-on for whoever wants it on a plastic build.

## Power budget — estimated, not measured (2026-11-24)

Battery current equals 3.3 V rail current: the regulator is linear. The
amplifier is on the battery directly. Capacity taken at the nominal
350 mAh, no derating.

**Inputs:**

| Item                                              | Value                         | Source                                                                                  |
| ------------------------------------------------- | ----------------------------- | --------------------------------------------------------------------------------------- |
| BLE transmit, 0 dBm                               | 176 mA peak                   | ESP32-S3 datasheet v2.2, table 5-8                                                      |
| BLE receive                                       | 93 mA peak                    | same                                                                                    |
| CPU awake at 80 MHz, peripheral clocks on, idle   | 36.1 mA                       | same, table 5-9                                                                         |
| BLE up, automatic light sleep, main crystal clock | 3.3 mA                        | Espressif, `examples/bluetooth/nimble/power_save`, ESP32-S3; connection parameters not stated |
| same, external 32.768 kHz crystal                 | 0.23 mA                       | same                                                                                    |
| 8 MB PSRAM in light sleep                         | +0.14 mA                      | ESP32-S3 datasheet, table 5-10 note                                                     |
| Microphone at 16 kHz                              | 0.23 mA                       | ICS-43434 datasheet, low-power mode                                                     |
| Amplifier quiescent / shut down                   | 2.4 mA / 0.6 µA               | MAX98357A datasheet, 3.7 V                                                              |
| Fuel gauge + regulator quiescent                  | 0.08 mA                       | datasheet typical values                                                                |
| One 251 B packet on 1M PHY                        | 2.12 ms on air                | Bluetooth packet format                                                                 |
| Radio open per connection event, no data          | 0.5 ms receive (assumed)      | —                                                                                       |
| Speech into the speaker at full volume            | 50–150 mW average (assumed)   | 0.93 W maximum, speech 7–12 dB below a full-scale sine; amplifier at 85 %               |

**Per state:**

| State                                   | Radio duty                                   | Current           |
| --------------------------------------- | -------------------------------------------- | ----------------- |
| Connected, idle                         | —                                            | 3.5 mA            |
| Listening (ADPCM up, 33.3 packets/s)    | transmit 7.1 %, receive 3.3 %                | 48 mA             |
| Thinking (15 ms interval, no data)      | receive 3.3 %                                | 9 mA              |
| Speaking (ADPCM down), electronics      | receive 10.4 %, transmit 0.5 %               | 43 mA             |
| Speaking, with amplifier and speaker    | same                                         | 61–93 mA          |

**Battery life:**

| Profile                                                                 | Average current | 350 mAh lasts |
| ----------------------------------------------------------------------- | --------------- | ------------- |
| Connected, idle                                                         | 3.5 mA          | 4.1 days      |
| Connected, 1–2 exchanges per hour                                       | 3.8–4.1 mA      | 3.6–3.8 days  |
| Exchanges back to back                                                  | 53 mA           | 6.6 hours     |

One exchange = 5 s listening, 5 s thinking, 10 s speaking at 100 mW =
0.29 mAh.

**What the move to the phone changes.** Active use: the budget recorded
with the on-device recogniser was "~2 h continuous", which is 175 mA
average; streaming audio instead is 53 mA, radio included. Connected
idle: unchanged by the move — no recogniser ran while idle. The 3.5 mA
here is higher than the 2.4 mA behind the earlier "~6 d" because it
starts from Espressif's measured 3.3 mA for an ESP32-S3 that keeps its
main crystal running as the BLE sleep clock, which is what this board
does: it has no 32.768 kHz crystal. Standby (no BLE) is not in this
table and is not affected.

**Open, not part of the move:** a 32.768 kHz crystal on IO15/IO16 (free
in the floorplan's net table) brings Espressif's figure from 3.3 mA to
0.23 mA; connected-idle would become about 0.45 mA, about 32 days. Not on
the BOM. To decide with the schematic.

## Components — final BOM, fixed (2026-11-11)

Every part below is a confirmed, sourceable reference, not a placeholder —
the next 3D modeling pass models the enclosure around these real
footprints instead of guessed boxes.

| Part                    | Ref                                                                                    | Footprint                                                                      | Notes                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MCU module              | `ESP32-S3-WROOM-1-N16R8`                                                               | 18 × 25.5 × 3.1 mm                                                             | PCB antenna variant (not `-1U`). More flash and PSRAM than the firmware needs; any `ESP32-S3-WROOM-1` with 4 MB or more fits the same pads (see *MCU*). LCSC C2913202 / DigiKey 5407-ESP32-S3-WROOM-1-N16R8CT-ND — both at zero stock on 2026-11-21; Mouser 356-ESP32S3WRM1N16R8 in stock that day.                                                                                                                                                                                                                                                                                                   |
| Display                 | `GDEY0213B74` (Good Display)                                                           | outline 59.2×29.2×1.0 mm, active 48.55×23.7 mm                                 | Rectangular, 250×122, SSD1680Z, 4 grayscale, SPI, 24-pin FPC. No touch/front-light. Bought from Good Display's own shop (buy-lcd.com); not at LCSC. From its drawing: active area 2.70 mm from the top (non-FPC) end and 7.95 mm from the FPC end, centred across; tail 12.5 mm wide, 14.3 mm long, 0.3 mm thick.                                                                                                               |
| Microphone              | `ICS-43434` (TDK InvenSense)                                                           | 3.50×2.65×0.98 mm                                                              | I2S MEMS. DigiKey 1428-1066-1-ND. DigiKey now marks it obsolete too (2026-11-21), with 52 007 in stock: buy the prototype's from that stock; a successor is an open point for any later batch.                                                                                                                                                                                                                                  |
| Speaker                 | `CDS-20144` (Same Sky/CUI)                                                             | oval 20×14×3.2 mm                                                              | 1 W, 4 Ω, solder pads. Driver lives in the back cavity; front face carries only a small acoustic port (bug found/fixed 2026-11-11, previous round-pocket placeholder overflowed the shell wall). DigiKey 102-3542-ND.                                                                                                                                                                                                           |
| Battery                 | `LP702030` / EEMB 350 mAh                                                              | 30 × 20 × 7 mm nominal, JST-PH (2.0 mm)                                        | 3.7 V Li-Po. Amazon (10.99€, ASIN B095W1XHVY). The listing reportedly gives 7.3 × 20.5 × 32 mm overall — to measure; the case reserves 2 mm at the lead end. Est. life: ~4 d connected-idle, ~3.7 d at 1-2 uses/h, ~6.5 h of non-stop exchanges — from the *Power budget* section, not measured.                                                                                                                                |
| Charge IC               | `TP4056`                                                                               | SOIC-8                                                                         | LCSC C382139 (0.11€/unit at qty 5).                                                                                                                                                                                                                                                                                                                                                                                             |
| Fuel gauge              | `MAX17048G+T10`                                                                        | TDFN-8, 2 × 2 mm                                                               | LCSC C2682616 / DigiKey MAX17048G+T10CT-ND.                                                                                                                                                                                                                                                                                                                                                                                     |
| USB-C receptacle        | `SHOU HAN TYPE-C 6P(073)`, LCSC C668623                                                | 8.94×3.2 mm shell, 6.8 mm deep (7.15 overall), 6-pin (VBUS×2, GND×2, CC1, CC2) | Charge-only, no D+/D- (decided 2026-11-11) — firmware OTA is BLE, so the port never needs data lines. Rated 5V/3A. **Changed (2026-11-21) from `TYPE-C 6P CB1.6(073)`, C2858274:** that one is the sunk-board version of the same shell, 1.6 mm into a board cut-out; on the 1.0 mm board it comes out 0.6 mm on the display side, where there is 0.4 mm. The plain `(073)` sits on the board. On the device's right long wall. |
| Buttons                 | `Alps SKRTLAE010`                                                                      | 4.5 × 3.4 × 3.3 mm                                                             | Side-push tactile switch, ×4, confirmed (2026-11-21). **Corrected (2026-11-22): 3.3 mm above the board, not 1.65** — Alps' product page and dimension drawing; stem Ø2.0, axis 1.7 mm above the board. Case length and height unchanged; button openings 5.2 × 3.6 mm. LCSC C110293 / DigiKey 4809-SKRTLAE010CT-ND.                                                                                                                                                                                                                                                                                                                              |
| Audio amplifier         | `MAX98357AETE+T` (Analog/Maxim), 16-TQFN                                               | 3 × 3 × 0.75 mm                                                                | I2S Class-D, no MCLK needed. 0.93 W into 4Ω at 3.7 V (battery voltage) — covers the `CDS-20144`'s 1 W/4Ω spec. **Confirmed by Lord (2026-11-21).** LCSC C910544 / DigiKey MAX98357AETE+TCT-ND.                                                                                                                                                                                                                                  |
| 3.3 V regulator         | `AP2112K-3.3TRG1`                                                                      | SOT-23-5                                                                       | LDO, 600 mA, 250 mV dropout at full load — holds regulation through the Li-Po's discharge curve, unlike AMS1117. **Confirmed by Lord (2026-11-21).** LCSC C51118 (Diodes Inc.; C23380830 is another maker's part under the same number) / DigiKey (AP2112K-3.3TRG1DITR-ND).                                                                                                                                                     |
| Display boost circuit   | **Correction (2026-11-21): needed after all** — see below                              | —                                                                              | I was wrong earlier: "on-chip booster" only means the *control loop* is on-chip; the power stage (inductor, MOSFET, diodes) is external, per the GDEY0213B74 datasheet's own §12 Reference Circuit, read in full this time.                                                                                                                                                                                                     |
| — boost inductor        | `L1`: 47µH, 500mA — `CKCS4030-47uH/M` (Cenker)                                         | 4 × 4 × 3 mm                                                                   | Isat 0.95 A, Irms 0.72 A, DCR 0.445 Ω. LCSC C354593.                                                                                                                                                                                                                                                                                                                                                                            |
| — boost MOSFET          | `Q1`: `Si1308EDL` (Vishay, `SI1308EDL-T1-GE3`), SC-70-3                                | N-channel, driven by the panel's GDR pin                                       | LCSC C469327 (Vishay; C7603347 is another maker's part under the same number) / DigiKey.                                                                                                                                                                                                                                                                                                                                        |
| — boost diodes ×3       | `D1/D2/D3`: `MBR0530T1G` (onsemi), SOD-123                                             | Schottky, 30V/500mA                                                            | LCSC C82046 / DigiKey. Use the `T1G` suffix — the bare `MBR0530` is marked obsolete at some distributors, this is the active direct substitute.                                                                                                                                                                                                                                                                                 |
| — boost resistors       | `R1`: 1MΩ (GDR to GND), `R2`: 2.2Ω (RESE to GND)                                       | 0603                                                                           | Generic 1 %. LCSC C22935 (UNI-ROYAL `0603WAF1004T5E`), C112307 (Yageo `RC0603FR-072R2L`).                                                                                                                                                                                                                                                                                                                                       |
| — boost/supply caps ×10 | `C3`, `C4`: 4.7µF/25V; `C2`, `C5`, `C6`, `C7`, `C9`, `C10`, `C11`, `C12`: 1µF/25V each | 0603                                                                           | Ceramic, 25V rating per the reference circuit. **Corrected (2026-11-21): ten, not seven** — `C2` (VSH2), `C4` (input, at L1) and `C11` (VGL) are in the datasheet's drawing too; it has no C1 or C8. Samsung `CL10A475KA8NQNC` (LCSC C69335), `CL10A105KA8NNNC` (LCSC C5673).                                                                                                                                                   |
| Display FPC connector   | Hirose `FH12A-24S-0.5SH(55)` (top contact) or `FH12-24S-0.5SH(55)` (bottom contact)    | 24-pin, 0.5 mm pitch, 2.0 mm high                                              | Same footprint for both. Which one depends on the face of the panel's tail that carries the contacts, which the panel specification does not state: buy both, decide on the real panel. LCSC C506794 / C202112.                                                                                                                                                                                                                 |
| Battery header          | JST `S2B-PH-SM4-TB(LF)(SN)`                                                            | PH 2.0 mm, 2-pin, side entry, SMT                                              | The board side of the JST-PH decision above. LCSC C295747.                                                                                                                                                                                                                                                                                                                                                                      |
| Case screws ×2          | B&F `MPMS 002 0008 PH` — M2 × 0.4 × 8 mm pan head Phillips machine screw               | head Ø3.85 × 1.52 mm                                                           | Decided (2026-11-21). M2 over M1.6, machine screw over thread-forming: neither LCSC nor DigiKey lists a thread-forming screw for plastic in these sizes; the screw cuts its thread in a printed Ø1.7 pilot. 8 mm for 6.7 mm of engagement in the bezel post. DigiKey H739-ND.                                                                                                                                                   |
| Custom PCB              | —                                                                                      | 1.0 mm, 2 layers, 79.95 × 29.3 mm                                              | Rectangular with one slot for the display FPC and two holes for the bezel posts. Floorplan only so far: `models/pcb/README.md`.                                                                                                                                                                                                                                                                                                 |

**Suppliers, consolidated on purpose:** LCSC first (everything it stocks
from the original maker) + DigiKey (mic, speaker, screws) as the two main
hubs; Amazon only for the battery (neither LCSC nor DigiKey/Mouser had a
matching cell shippable to France at this capacity/connector); the display
from Good Display's own shop. The order-ready list, one unit, with every
code: `models/pcb/BOM_to_buy.md`. It also lists about twenty support
passives (USB-C CC resistors, charge-current resistor, decoupling,
pull-ups) that are not in the table above and wait for the schematic.

