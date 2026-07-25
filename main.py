import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("spawn")

    from ui.app import create_app
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
