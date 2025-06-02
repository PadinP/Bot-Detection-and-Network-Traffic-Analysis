import os
import datetime
import threading
from fastapi import APIRouter
from app.services.capture_service import start_capture
from app.services.detection_service import detection_run_all

router = APIRouter(prefix="/bots_scan", tags=["Scan"])

@router.post("/bots_scan_parallel")
def run_scan_parallel(capture_time: int = 60, cycles: int = 3):
    """
    Ejecuta la captura y detección en paralelo. Para cada ciclo:
      - Se genera una ruta única para el archivo (.binetflow) usando el número
        de ciclo y la marca de tiempo actual.
      - Se crea un proceso FlowAnalysis pasándole dicho file_path.
      - Se llama a start_capture, que actualiza internamente el file_path y
        ejecuta run_capture usando ese archivo para guardar la captura.
      - Si ya existe un archivo del ciclo anterior, se lanza en un hilo el análisis sobre él.
      - Al finalizar se ejecuta detección final sobre el último archivo.
    """
    base_dir = "modulo/capturas"
    # Asegura que el directorio existe
    os.makedirs(base_dir, exist_ok=True)
    
    cycles_results = []         # Lista para almacenar resultados de cada ciclo
    detection_threads = []      # Para gestionar los threads de detección

    # Genera la ruta para el primer ciclo de forma inline
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    current_file = os.path.join(base_dir, f"flow_analysis_cycle_1_{timestamp}.binetflow")
    capture_result = start_capture(capture_time=capture_time, file_path=current_file)
    cycles_results.append({
        "cycle": 1,
        "capture_file": current_file,
        "capture_result": capture_result,
        "detection_trigger": "Primer ciclo; sin archivo previo para detectar."
    })
    previous_file = current_file

    # Ciclos restantes: lanzar detección sobre el archivo previo y generar una nueva captura
    for cycle in range(2, cycles + 1):
        # Lanzar en thread la detección sobre el archivo del ciclo anterior
        dt = threading.Thread(target=detection_run_all, args=(previous_file,))
        dt.start()
        detection_threads.append(dt)
        detection_trigger = f"Detección iniciada sobre {previous_file}"

        # Generar la ruta para el siguiente ciclo de forma inline
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        current_file = os.path.join(base_dir, f"flow_analysis_cycle_{cycle}_{timestamp}.binetflow")
        capture_result = start_capture(capture_time=capture_time, file_path=current_file)
        cycles_results.append({
            "cycle": cycle,
            "capture_file": current_file,
            "capture_result": capture_result,
            "detection_trigger": detection_trigger
        })

        # Actualizar la ruta del archivo previo para el siguiente ciclo
        previous_file = current_file

    # Detección final sobre el último archivo generado
    dt = threading.Thread(target=detection_run_all, args=(previous_file,))
    dt.start()
    detection_threads.append(dt)
    cycles_results.append({
        "cycle": "final",
        "capture_file": previous_file,
        "detection_trigger": f"Detección final iniciada sobre {previous_file}"
    })

    # Esperar a que todos los threads de detección finalicen antes de retornar la respuesta
    for dt in detection_threads:
        dt.join()

    return {"cycles": cycles_results}
