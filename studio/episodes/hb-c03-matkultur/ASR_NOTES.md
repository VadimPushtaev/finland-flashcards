# Matkultur och matvanor — narration diagnostics

All 42 selected source-order F1 clips pass input/settings, finite waveform,
headroom, duration/sample-rate and hash-bound local ASR checks. Displayed Swedish
and reviewed Russian text remain exact. Separate speech overrides expand only
source 50/femtio and 20/tjugo; both full sentences recover the intended values.
No numerical retake or other resynthesis was indicated by a proven strategy.

ASR checked completed takes during synthesis in one serialized one-thread lane,
using the existing CLI against checksum-verified snapshots. `narration-streaming.json`
records batches; canonical transcript paths were mapped only after checking the
same WAV hashes. `narration-check.json` retains the complete final selected set.

Listen especially to **matsvinn**, **matinköp**, **torgevenemang**,
**lunchrestaurangerna**, **Mellanöstern**, **renskötsel/renkött**, **påskrätterna**,
**fastlagsbullar**, **skördesäsong** and **jordgubbarna**. ASR produced spellings or
word-boundary differences such as mattingköp, torjevenemang, lungrestaurangenas,
mellan östen, renshötsel/ringkött, fastlagspullar, Sjördesäsong and jogubbarna.
It also omitted “är” in the matsvinn sentence and rendered använde/använder in
the spice sentence. These differences are not confirmed audible errors.

Whole-video listening, accent/naturalness, music balance and physical-device checks
remain pending; automated transcription cannot establish them. No auditory or user
acceptance is claimed.
