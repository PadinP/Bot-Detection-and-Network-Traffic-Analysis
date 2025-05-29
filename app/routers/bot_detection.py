# app/routers/detection.py
from fastapi import APIRouter, HTTPException
from app.services.bot_detection_service import detection_run_all

router = APIRouter(prefix="/detection", tags=["Detection"])

@router.post("/run_all", )
def detection_run_all_endpoint():
    """
    Ejecuta todas las etapas de detección en orden.
    Este endpoint es el único que se expone para la detección.
    """
    try:
        result = detection_run_all()
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
