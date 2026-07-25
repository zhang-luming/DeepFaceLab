# AGENTS.md — DeepFaceLab

## Git commits
- **NEVER commit without explicit user approval.** Do not run `git add` + `git commit` unless the user has explicitly asked you to commit, reviewed the commit message, and confirmed it.
- Before committing, present the proposed commit message and list of changed files for user review.

## Entrypoints
- **`main.py`** (root) launches the FastAPI Web UI (`uv run python main.py`). It adds `engine/` to `sys.path` before the guard so that spawned child processes can still import engine modules.
- **`engine/main.py`** is the original CLI entrypoint (`python engine/main.py <subcommand>`). Also workable standalone.
- Registered CLI subcommands: `extract`, `sort`, `util`, `train`, `merge`, `exportdfm`, `videoed`, `facesettool`, `xseg`, `dev_test`.
- On Linux, `root main.py` sets multiprocessing to `spawn` start method. Do not change to `fork`.

## Project structure
- **`engine/`** — original DeepFaceLab source (core NN lib, face detection, models, CLI scripts, XSeg editor, etc.)
- **`ui/`** — FastAPI Web UI layer (`app.py`, `api/`, `static/`)
- **`.venv/`** — uv-managed virtual environment (gitignored)
- **`pyproject.toml`** — uv project config with all dependencies

## Package management
- Use **uv** for virtual environment and dependencies: `uv sync` (single command, creates venv + installs all deps from lockfile).
- Python 3.8 required (TF 2.4 constraint — `requires-python = ">=3.8,<3.9"` in `pyproject.toml`).

## Tech stack and constraints
- **TensorFlow 2.4.0** (GPU), no Keras. `nn.initialize()` lazily imports TF after setting CUDA env vars — must be called before any TF import.
- **No eager execution.** Leras runs TF in graph mode.
- Data format: **NHWC** (default). `floatx="float32"`.
- PyQt5 is used for the XSeg editor (Windows/Qt GUI workflow).
- The `.gitignore` uses a deny-list approach — only explicitly whitelisted file types are tracked.

## Architecture conventions (engine)
- **Core NN library** is `engine/core/leras/` — a lightweight keras-like layer built directly on TF graph ops. **Do not add Keras imports.**
- **Models** live in `engine/models/Model_<Name>/Model.py`. The `--model` arg takes `<Name>` only (e.g., `SAEHD`). `engine/models/__init__.py:import_model()` handles dynamic import.
- **Leras-level models** (architectures, discriminators) live in `engine/core/leras/models/`.
- **Architectures** go in `engine/core/leras/archis/` and extend `ArchiBase` (registered as `nn.ArchiBase`).
- **File I/O** for images: use `core.cv2ex.cv2_imread` / `cv2_imwrite` (handles non-ASCII paths).
- **Atomic writes**: `core.pathex.write_bytes_safe` (writes to `.tmp`, then renames).
- **Custom image format** `.dflimg` carries face metadata via `DFLIMG/`.

## Project layout
| Directory | Purpose |
|-----------|---------|
| `engine/core/leras/` | NN lib: `nn.py`, `device.py`, `layers/`, `archis/`, `models/`, `ops/`, `optimizers/`, `initializers/` |
| `engine/core/imagelib/` | Image processing (blur/sharpen, color transfer, warp, morph, segmentation polys, sd) |
| `engine/core/interact/` | CLI I/O (`interact.py` — custom colored console I/O) |
| `engine/core/joblib/` | Multi-process work dispatch (`SubprocessorBase`, `SubprocessGenerator`) |
| `engine/core/qtex/` | Qt/PyQt5 helpers for GUI tooling |
| `engine/core/mplib/` | Multiprocessing shared list |
| `engine/facelib/` | Face detection (S3FD), landmark extraction (FAN), segmentation (XSegNet) |
| `engine/DFLIMG/` | `.dflimg` file format reader/writer |
| `engine/samplelib/` | Dataset loading, sample generators, packed faceset pack/unpack |
| `engine/models/` | Face-swap model classes (`ModelBase` in root, per-model in `Model_*` dirs) |
| `engine/mainscripts/` | CLI subcommand implementations |
| `engine/merger/` | Merging/compositing logic (+ Qt MergerScreen GUI) |
| `engine/XSegEditor/` | PyQt5 polygon mask editor |
| `engine/localization/` | EN/RU/ZH string tables |
| `ui/` | FastAPI Web UI (`app.py`, `api/`, `static/`) |

## No test infrastructure
There are no tests, no linter config, no typechecker, no CI. The `.vscode/` launch configs reference Windows env vars (`DFL_ROOT`, `PYTHONEXECUTABLE`, `WORKSPACE`) and are unreliable on non-Windows.

## Common pitfalls
- Multiprocessing child processes re-import root `main.py`; `sys.path.insert` for `engine/` is outside the guard so children still resolve engine imports. The `if __name__ == "__main__":` guard is critical.
- `core.leras.nn` is a class with all-static members; don't instantiate it.
- Model files use the pattern `<model_name>_<ModelClass>_data.dat` and `<model_name>_<ModelClass>_archi.dat`.
- The `--force-gpu-idxs` argument takes comma-separated integers (e.g., `0,1`), not a list.
