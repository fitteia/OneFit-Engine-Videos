# Fits, saved fits and batches

[`ofe-fits-batches-parallel.mp4`](https://github.com/fitteia/OneFit-Engine-Videos/releases/latest/download/ofe-fits-batches-parallel.mp4) is a 5 minute 22 second, 1920×1080 video with English narration and an embedded English subtitle track (soft subtitles; turn them on in the player). [`ofe-fits-batches-parallel.srt`](ofe-fits-batches-parallel.srt) holds the same subtitles as a separate file, and [`ofe-fits-batches-parallel-script.txt`](ofe-fits-batches-parallel-script.txt) holds the full script. It follows the [introduction](../introduction/README.md) and the [remote hosts](../remote/README.md) videos, with the same measurement: the full Stelar file, `T005F1_1.sdf`, with 44 field-cycling NMR relaxation curves from 8 MHz down to 3 kHz.

It shows the ways to start a fit, and the fits that run in parallel:

- A model and data files: `onefite fit` with `--individual` and `--save-to`, then the same fit in OFE-GUI's Function + data files tab. T1 grows from 2.00 s at 3 kHz to 3.29 s at 8 MHz.
- A saved fit: what `t005.json` holds (`Function` and `Parameters`, `Dados` with each block's `# DATA` and `# TAG` lines, `T`, `Tags`, `FitType`), the JSON/SAV/Jobs tab and the field editor, Shift+T to rename `T`, and All in Tags.
- Fitting a saved fit again with OFE-Go: `--selected-dataset` (and all in OFE-GUI's Selected data sets), a `.sav` file and `onefite convert`.
- A batch: a jobs file with two models fitted individually and the saved fit fitted globally, `--jobs`, the batch folder and `batch.json`; then OFE-GUI's Jobs table, Fits at once, the Fits bar and the global fit that can't follow the data (χ² 41 against 0.048).
- Parallel fits at two levels: an individual fit's blocks (and a hybrid fit's per-block parts) with `--workers` and `--no-parallel`, and a batch's fits with `--jobs`, each fit getting CPUs ÷ jobs workers.

Every command and its output on the slides, and the GUI screens, come from real runs with OFE-GUI 0.4.0-pre27 and onefite-go 0.4.0~pre9 on a Debian forky server (arm64, 4 CPUs). The closing card marks this as a pre-final version and identifies the Artistic License 2.0 currently included with both OFE-Go and OFE-GUI.

## Building

As for the introduction (see its [Building](../introduction/README.md#building) section), with this folder's `make.sh`:

```sh
npm install
kit/get-voice.sh
fits/build/make.sh
```

`build/slides/slides.html` holds the slides; elements marked `data-hl` can be highlighted by name in `narration.py` (`"batch:jobs"`). `build/shots/` holds the six GUI screens, captured at 3840×2160 by `build/capture/fits-scene.cjs` (see its header) from one real session: the Stelar file uploaded and fitted, the saved JSON in the JSON viewer, the Jobs table, and the batch it ran.

## Voice credit

Narration was generated with Piper's `en_GB-alba-medium` voice. Its model card names the University of Edinburgh dataset at <https://datashare.ed.ac.uk/handle/10283/3270>, licensed under CC BY 4.0, and says the model was fine-tuned from the U.S. English Lessac voice. See the [Alba voice model card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_GB/alba/medium/MODEL_CARD) and the [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).
