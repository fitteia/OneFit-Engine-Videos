# OFE-Go and OFE-GUI introduction

[`ofe-go-gui-introduction.mp4`](https://github.com/fitteia/OneFit-Engine-Videos/releases/latest/download/ofe-go-gui-introduction.mp4) is a 3 minute 11 second, 1920×1080 introduction with English narration and an embedded English subtitle track (soft subtitles; turn them on in the player). [`ofe-go-gui-introduction.srt`](ofe-go-gui-introduction.srt) holds the same subtitles as a separate file, and [`ofe-go-gui-introduction-script.txt`](ofe-go-gui-introduction-script.txt) holds the full script.

The video follows one real measurement, a field-cycling NMR relaxation curve (20 points), from the data to the report:

- OFE-Go: the fit as one command, with its real output. The model `Mz(t,M0:1,Minf:0.05,T1:2[0.01<100])=Minf+(M0-Minf)*exp(-t/T1)` is fitted with `--logx --reduced-chi2 --fit-methods="simp scan min"`, giving T1 = 1.998 ± 0.030.
- The two ways to start a fit (data plus model, or a saved JSON/SAV fit, with jobs files for batches) and the Individual, Global and Hybrid modes.
- OFE-GUI: the same fit, run with OFE-GUI 0.4.0-pre23 and onefite-go 0.4.0~pre8, shown in the dark Compact layout with the Terminal above Plots in the centre column.
- OFE-Figures: the fit plot with an edited title, subtitle and axis labels, drawn by `plot-go`.
- OFE-Report: the report of that run, rounded for publication, with the edited figure.

The closing card marks this as a pre-final version, identifies the Artistic License 2.0 currently included with both OFE-Go and OFE-GUI, and states that a separate commercial license for eligible project code is in preparation.

The Terminal scene shows the ordinary shell. The narration describes an optional, separately installed AI assistant that can be launched there; it is not presented as a built-in OFE-GUI feature.

## Building

Needs Python 3 with `numpy`, `Pillow` and `piper-tts`, ffmpeg with libx264, and Node.js for the slides (`npm install` in `build/`, which installs `playwright-core`; set `CHROME` to a Chromium binary if Playwright has none of its own).

```sh
cd introduction/build
npm install
./get-voice.sh
./make.sh
```

`make.sh` renders the slides, synthesizes the narration sentence by sentence (`narration.py` holds each sentence's caption text, spoken text, camera framing and highlight), renders the frames (`build.py`), normalizes the narration to −16 LUFS with a −1.5 dBTP ceiling, and writes `../ofe-go-gui-introduction.mp4` with its embedded subtitles, plus the `.srt` and the script. Piper's synthesis varies slightly from run to run, so each build's timings, and with them its subtitles, are its own: release the MP4 together with the `.srt` from the same build.

`build/shots/` holds the four GUI screens the video uses, captured at 3840×2160 from a real run. `build/capture/` holds the Playwright scripts that captured them; they drive a running OFE-GUI and contain that session's paths and job IDs, so adjust them before capturing again.

## Voice credit

Narration was generated with Piper's `en_GB-alba-medium` voice. Its model card names the University of Edinburgh dataset at <https://datashare.ed.ac.uk/handle/10283/3270>, licensed under CC BY 4.0, and says the model was fine-tuned from the U.S. English Lessac voice. See the [Alba voice model card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_GB/alba/medium/MODEL_CARD) and the [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).
