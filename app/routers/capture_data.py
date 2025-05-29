
from fastapi import APIRouter
from app.services.capture_service import start_capture, stop_capture

# Definimos el router con un prefijo general y una etiqueta general para el grupo de endpoints.
router = APIRouter(prefix="/capture", tags=["Capture"])

@router.post("/start-capture")
def start_capture_endpoint(capture_time: int = 60, sleep_time: int = 30):
    return start_capture(capture_time, sleep_time)

@router.post("/stop-capture")
def stop_capture_endpoint():
    return stop_capture()
