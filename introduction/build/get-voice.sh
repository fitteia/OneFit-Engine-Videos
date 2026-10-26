#!/bin/sh
set -e
cd "$(dirname "$0")"
mkdir -p voices
base=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium
for f in en_GB-alba-medium.onnx en_GB-alba-medium.onnx.json MODEL_CARD; do
  [ -s "voices/$f" ] || curl -fsSL -o "voices/$f" "$base/$f"
done
ls -l voices
