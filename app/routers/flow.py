import os
import datetime
import threading
import io
from contextlib import redirect_stdout
from fastapi import APIRouter

from app.config.settings import DIR_CAPTURE
from app.services.capture_service import start_capture
from app.services.detection_service import detection_pipeline

router = APIRouter(prefix="/bots_scan", tags=["Scan"])

@router.post("/bots_scan_parallel")
def run_scan_parallel(capture_time: int = 60, cycles: int = 4):
    # Creamos un buffer para capturar la salida de print()
    buffer = io.StringIO()
    
    # Todo lo que se imprima en este bloque se redirige al buffer
    with redirect_stdout(buffer):
        os.makedirs(DIR_CAPTURE, exist_ok=True)
    
        cycles_results = []      # Almacena los resultados de cada ciclo.
        detection_threads = []   # Lista para gestionar los threads de detección.
    
        # Primer ciclo: solo captura (sin análisis previo).
        current_file = os.path.join(DIR_CAPTURE, "flow_analysis_cycle_1.binetflow")
        print(f"Iniciando captura en: {current_file}")
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
            current_file = os.path.join(DIR_CAPTURE, f"flow_analysis_cycle_{cycle}.binetflow")
            print(f"Iniciando ciclo {cycle} - captura en: {current_file}")
            capture_result = start_capture(capture_time=capture_time, file_path=current_file)
    
            # Determinamos si el ciclo es par para ejecutar stage3_detection.
            ejecutar_stage3 = (cycle % 2 == 0)
            print(f"Ciclo {cycle}: ejecutar_stage3 = {ejecutar_stage3}")
    
            # Lanzamos el hilo de detección.
            dt = threading.Thread(
                    target=detection_pipeline,
                    args=(previous_file, current_file, ejecutar_stage3)
                 )
            dt.start()
            detection_threads.append(dt)
    
            detection_msg = (
                f"Detección lanzada sobre {previous_file}" +
                (f" con stage3 en {current_file} (ciclo par)" if ejecutar_stage3 else f", sin stage3 (ciclo impar)")
            )
            print(detection_msg)
    
            cycles_results.append({
                "cycle": cycle,
                "capture_file": current_file,
                "capture_result": capture_result,
                "detection_trigger": detection_msg
            })
    
            # Actualizamos previous_file para el siguiente ciclo.
            previous_file = current_file
    
        # Esperamos a que todos los hilos de detección finalicen.
        for dt in detection_threads:
            dt.join()
            print("Hilo de detección finalizado.")
    
    # Fin del bloque redirect: recuperamos toda la salida capturada.
    captured_output = buffer.getvalue()
    
    # Guardamos la salida capturada en un archivo TXT, agregando un encabezado con fecha/hora.
    with open("registro_endpoint.txt", "a") as log_file:
        log_file.write("----- Registro endpoint ({}) -----\n".format(datetime.datetime.now()))
        log_file.write(captured_output)
        log_file.write("\n-------------------------------------\n\n")
    
    return {"cycles": cycles_results}
