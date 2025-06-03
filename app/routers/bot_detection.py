# app/routers/detection.py
from fastapi import APIRouter, HTTPException
from app.services.detection_service import detection_run_all,stage3_detection

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


@router.post("/run_stage3", )
def detection_stage3(file_path):
    """
    Ejecuta todas las etapas de detección en orden.
    Este endpoint es el único que se expone para la detección.
    """
    try:
        result = stage3_detection(file_path)
        return result
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
