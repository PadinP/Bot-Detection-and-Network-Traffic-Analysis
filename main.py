import warnings
warnings.filterwarnings("ignore", message="resource_tracker: There appear to be")

import uvicorn
import contextlib
from fastapi import FastAPI
from joblib.externals.loky.backend.resource_tracker import _resource_tracker
from app.routers import bot_detection_flow

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Aquí puedes inicializar recursos si es necesario.
    yield
    _resource_tracker._stop()
    print("Aplicación cerrándose, limpiando recursos...")

app = FastAPI(lifespan=lifespan, docs_url="/")
app.include_router(bot_detection_flow.router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, reload=True)
