#!/bin/bash
# Quick96 minimal VRAM training preset for rapid local testing
set -e
cd "$(dirname "$0")/.."
exec uv run python engine/main.py train \
  --model Quick96 \
  --model-dir workspace/model/quick96 \
  --training-data-src-dir workspace/data_src/aligned \
  --training-data-dst-dir workspace/data_dst/aligned \
  --force-gpu-idxs 0 \
  --silent-start
