# AGENTS.md — DeepFaceLab

## Git commits
- **NEVER commit without explicit user approval.** Do not run `git add` + `git commit` unless the user has explicitly asked you to commit, reviewed the commit message, and confirmed it.
- Before committing, present the proposed commit message and list of changed files for user review.

## Entrypoints
- **`main.py`** (root) launches the FastAPI Web UI (`uv run python main.py`). It adds `engine/` to `sys.path` before the guard so that spawned child processes can still import engine modules.
- **`engine/main.py`** is the original CLI entrypoint (`uv run python engine/main.py <subcommand>`). Also workable standalone.
- Both entrypoints configure NVIDIA CUDA library paths for the `nvidia-*-cu11` pip packages. `engine/main.py` delegates to `core.cuda_env` — a shared module that uses `importlib.util.find_spec` to locate the pip package lib dirs, auto-detects the system `libcuda.so` driver path, and `os.execve`s the process with `LD_LIBRARY_PATH` set before startup (required because `ld.so` only reads it at process creation). `main.py` uses a different approach (module-level `os.environ` manipulation).
- Registered CLI subcommands: `extract`, `sort`, `util`, `train`, `merge`, `exportdfm`, `videoed`, `facesettool`, `xseg`, `dev_test`.
- On Linux, both entrypoints set multiprocessing to `spawn`. Do not change to `fork`.

## Package management
- Use **uv** for virtual environment and dependencies: `uv sync` (single command, creates venv + installs all deps from lockfile).
- Python 3.8 required (`requires-python = ">=3.8,<3.9"` in `pyproject.toml`).
- Run the web UI: `uv run python main.py`
- Run a CLI subcommand: `uv run python engine/main.py <subcommand>`

## Tech stack and constraints
- **TensorFlow 2.4.0** (GPU via `tensorflow-gpu==2.4.0`), no Keras. Leras is a lightweight keras-like lib built directly on TF graph ops. **Do not add Keras imports.**
- `nn.initialize_main_env()` (sets DeviceConfig + environment) must be called before `nn.initialize()` (imports TF, creates session, registers leras layers/ops/optimizers/archis/models).
- **No eager execution.** TF v2 behavior is disabled; everything runs in graph mode.
- Data format: **NHWC** (default). `floatx="float32"`.
- PyQt5 is used only by the XSeg editor (`engine/XSegEditor/`).
- The `.gitignore` uses a deny-list approach — only explicitly whitelisted file types are tracked.

## Architecture conventions (engine)
- **Core NN library** is `engine/core/leras/` — `nn.py` is a class with all-static members; don't instantiate it.
- **App-level models** live in `engine/models/Model_<Name>/Model.py`. The `--model` arg takes `<Name>` only (e.g., `SAEHD`). `engine/models/__init__.py:import_model()` handles dynamic import.
- **Leras-level models** (NN architecture, discriminators) live in `engine/core/leras/models/`.
- **Architectures** go in `engine/core/leras/archis/` and extend `ArchiBase` (registered dynamically as `nn.ArchiBase`).
- **File I/O** for images: use `core.cv2ex.cv2_imread` / `cv2_imwrite` (handles non-ASCII paths).
- **Atomic writes**: `core.pathex.write_bytes_safe` (writes to `.tmp`, then renames).

## Project layout
| Directory | Purpose |
|-----------|---------|
| `engine/core/leras/` | NN lib: `nn.py`, `device.py`, `layers/`, `archis/`, `models/`, `ops/`, `optimizers/`, `initializers/` |
| `engine/core/imagelib/` | Image processing (blur/sharpen, color transfer, warp, morph, segmentation) |
| `engine/core/interact/` | CLI I/O (`interact.py` — custom colored console I/O) |
| `engine/core/joblib/` | Multi-process work dispatch (`SubprocessorBase`, `SubprocessGenerator`) |
| `engine/core/mplib/` | Multiprocessing shared list |
| `engine/core/qtex/` | Qt/PyQt5 helpers for GUI tooling |
| `engine/core/cv2ex.py` | OpenCV wrappers (non-ASCII path support) |
| `engine/core/pathex.py` | Path utilities: atomic writes, image extensions, recursive scan |
| `engine/core/osex.py` | OS-level helpers (process priority, etc.) |
| `engine/core/cuda_env.py` | NVIDIA CUDA lib discovery + `LD_LIBRARY_PATH` injection via `os.execve` |
| `engine/facelib/` | Face detection (S3FD), landmark extraction (FAN), segmentation (XSegNet) |
| `engine/DFLIMG/` | `.dflimg` file format reader/writer (carries face metadata) |
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
- `nn.ArchitectBase` is registered at module-level (`nn.ArchiBase = ArchiBase` at the bottom of `archis/ArchiBase.py`). Always import via `nn.ArchiBase`, not directly.
- Model files use the pattern `<model_name>_<ModelClass>_data.dat` and `<model_name>_<ModelClass>_archi.dat`.
- The `--force-gpu-idxs` argument takes comma-separated integers (e.g., `0,1`), not a list.
