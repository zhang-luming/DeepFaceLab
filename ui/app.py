from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path


def create_app():
    app = FastAPI(title="DeepFaceLab")

    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    from ui.api import router as api_router
    app.include_router(api_router, prefix="/api")

    @app.get("/")
    async def root():
        return {"message": "DeepFaceLab Web UI"}

    return app
