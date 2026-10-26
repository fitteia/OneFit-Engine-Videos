# OFE-GUI on remote hosts

[`ofe-gui-remote-hosts.mp4`](https://github.com/fitteia/OneFit-Engine-Videos/releases/latest/download/ofe-gui-remote-hosts.mp4) is a 4 minute 30 second, 1920×1080 video with English narration and an embedded English subtitle track (soft subtitles; turn them on in the player). [`ofe-gui-remote-hosts.srt`](ofe-gui-remote-hosts.srt) holds the same subtitles as a separate file, and [`ofe-gui-remote-hosts-script.txt`](ofe-gui-remote-hosts-script.txt) holds the full script. It follows the [introduction](../introduction/README.md) and fits the same measurement.

It shows the ways OFE-GUI runs fits on another computer:

- Why OFE-GUI listens only on 127.0.0.1, and connects through SSH.
- `onefite-gui -ssh`: the whole GUI on the remote account, forwarded to your browser. The real launcher output, then the GUI on the remote host (Debian forky, arm64): its Terminal, uploading the data from your computer, and the fit (T1 = 1.998 ± 0.030).
- Its options: `-remote-addr`, `-idle-timeout`, your SSH configuration, and the remote GUI stopping with the launcher.
- `onefite-gui -connect-remote`: the GUI and Terminal on your computer, the fit on a remote OFE-GUI started for you; Settings shows the pre-filled Remote onefite-gui field.
- An OFE-GUI already running on the server, reached with an SSH tunnel, in the browser or through the Remote onefite-gui field.
- `onefite-gui -reverse-ssh`, for a fitting machine that can't accept connections.
- An engine web service (the Raku engine's `onefite start-web-engine`) as the onefite executable.
- How to choose, and `-allow-public` only for an isolated, firewalled machine.

Every command and its output on the slides, and both GUI screens, come from real runs with OFE-GUI 0.4.0-pre25 and onefite-go 0.4.0~pre9, from a Linux computer to a Debian forky server. The closing card marks this as a pre-final version and identifies the Artistic License 2.0 currently included with both OFE-Go and OFE-GUI.

## Building

As for the introduction (see its [Building](../introduction/README.md#building) section), with this folder's `make.sh`:

```sh
npm install
kit/get-voice.sh
remote/build/make.sh
```

`build/slides/slides.html` holds the slides; elements marked `data-hl` can be highlighted by name in `narration.py` (`"ssh1:target"`). `build/shots/` holds the two GUI screens, captured at 3840×2160 by `build/capture/ssh-scene.cjs` (see its header) from a real `-ssh` run and a real `-connect-remote` run, the data file uploaded from the local computer each time.

## Voice credit

Narration was generated with Piper's `en_GB-alba-medium` voice. Its model card names the University of Edinburgh dataset at <https://datashare.ed.ac.uk/handle/10283/3270>, licensed under CC BY 4.0, and says the model was fine-tuned from the U.S. English Lessac voice. See the [Alba voice model card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_GB/alba/medium/MODEL_CARD) and the [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/).
