# OneFit-Engine-Videos

Videos about OneFit Engine: OFE-Go (the command line) and OFE-GUI (the browser interface).

The MP4 files are **release assets**, not files in this repository, so that cloning this repository, the OneFit-Engine-go repository or the packages built from it stays small. Each release carries every current video; the links below always point to the newest release.

| Video | Length | Download | Captions and script |
| --- | --- | --- | --- |
| OFE-Go and OFE-GUI introduction (pre-final) | 3:12 | [ofe-go-gui-introduction.mp4](https://github.com/fitteia/OneFit-Engine-Videos/releases/latest/download/ofe-go-gui-introduction.mp4) | [captions](introduction/ofe-go-gui-introduction.srt), [script](introduction/ofe-go-gui-introduction-script.txt), [about](introduction/README.md) |

Every MP4 also has its subtitles as an embedded track; turn them on in the player.

## Building

Each video's folder has a `build/` folder with everything needed to rebuild it: the narration script, the slides, the captured screens and the build scripts. See [introduction/README.md](introduction/README.md).

## Releasing a new cut

Build it, commit the changed captions, script and sources, then attach the MP4 to a new release (from the repository's own clone):

```sh
gh release create intro-YYYY-MM-DD introduction/ofe-go-gui-introduction.mp4 --title "Introduction YYYY-MM-DD"
```

A new release must attach every current video, since `releases/latest` is what the links use.

## License

The build scripts and texts are distributed under the Artistic License 2.0 (see [LICENSE](LICENSE)). The narration voice has its own license; see each video's README for the credit.
