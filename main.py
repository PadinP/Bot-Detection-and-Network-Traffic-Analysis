import uvicorn
import contextlib
from fastapi import FastAPI
from joblib.externals.loky.backend.resource_tracker import _resource_tracker
from app.routers import bot_detection_flow

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Aquí puedes inicializar recursos si es necesario.
    yield
    # Se ejecuta al finalizar el ciclo de vida de la aplicación.
    _resource_tracker._stop()
    print("Aplicación cerrándose, limpiando recursos...")

app = FastAPI(lifespan=lifespan)

app.include_router(bot_detection_flow.router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=8001, reload=True)
