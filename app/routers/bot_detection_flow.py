import os
import datetime
import threading
from fastapi import APIRouter

from app.config.globals import DIR_CAPTURE
from app.services.capture_service import start_capture
from app.services.detection_service import detection_pipeline

router = APIRouter(prefix="/bots_scan", tags=["Scan"])



@router.post("/bots_scan_parallel")
def run_scan_parallel(capture_time: int = 60, cycles: int = 4):

    os.makedirs(DIR_CAPTURE, exist_ok=True)
    
    cycles_results = []      # Almacena los resultados de cada ciclo.
    detection_threads = []   # Lista para gestionar los threads de detección.
    
    # Primer ciclo: solo captura (no hay análisis previo).
    current_file = os.path.join(DIR_CAPTURE, "flow_analysis_cycle_1.binetflow")
    capture_result = start_capture(capture_time=capture_time, file_path=current_file)
    cycles_results.append({
        "cycle": 1,
        "capture_file": current_file,
        "capture_result": capture_result,
        "detection_trigger": "Primer ciclo: Sin análisis previo."
    })
    
    # Guardamos la ruta del archivo del primer ciclo.
    previous_file = current_file
    
    # Para los ciclos siguientes: ejecutar captura y detección en paralelo.
    for cycle in range(2, cycles + 1):
        # Generar la ruta única para el nuevo archivo (ciclo actual).
        current_file = os.path.join(DIR_CAPTURE, f"flow_analysis_cycle_{cycle}.binetflow")
        
        # Realizar la captura.
        capture_result = start_capture(capture_time=capture_time, file_path=current_file)
        
        # Determinar si el ciclo es par: solo en esos se ejecutará stage3_detection.
        ejecutar_stage3 = (cycle % 2 == 0)
        
        # Lanzar el hilo de detección pasando el flag correspondiente.
        dt = threading.Thread(target=detection_pipeline, args=(previous_file, current_file, ejecutar_stage3))
        dt.start()
        detection_threads.append(dt)
        
        detection_msg = (
            f"Detección lanzada sobre {previous_file}" +
            (f" con stage3 en {current_file} (ciclo par)" if ejecutar_stage3 else f", sin stage3 (ciclo impar)")
        )
        
        cycles_results.append({
            "cycle": cycle,
            "capture_file": current_file,
            "capture_result": capture_result,
            "detection_trigger": detection_msg
        })
        
        # Actualizar previous_file para la siguiente iteración.
        previous_file = current_file

    # Esperar a que todos los hilos de detección finalicen.
    for dt in detection_threads:
        dt.join()
    
    return {"cycles": cycles_results}
