import os
import threading
from fastapi import APIRouter
from app.config.settings import DIR_CAPTURE
from app.services.capture_service import CaptureService
from app.services.detection_service import DetectionService
from app.config.logger_config import capture_logger, detection_logger

router = APIRouter(tags=["Scan"])

@router.post("/bots_scan")
def run_scan_sequential(capture_time: int = 5, cycles: int = 4):
    # Aseguramos que exista la carpeta de capturas.
    os.makedirs(DIR_CAPTURE, exist_ok=True)

    # Instanciamos los servicios.
    capture_service = CaptureService()
    detection_service = DetectionService()

    # Primer ciclo: Solo se realiza la captura sin detección.
    current_file = os.path.join(DIR_CAPTURE, "flow_analysis_cycle_1.binetflow")
    capture_logger.info("Ciclo 1 - Iniciando captura en %s", current_file)
    capture_service.start_capture(capture_time=capture_time, file_path=current_file)

    # Guardamos la ruta del archivo del primer ciclo, que se usará en la detección del siguiente ciclo.
    previous_file = current_file

    # Para los ciclos siguientes: se ejecuta la captura y, en paralelo, se lanza (pero de forma secuencial) la detección.
    for cycle in range(2, cycles + 1):
        # Generar la ruta única para el archivo del ciclo actual.
        current_file = os.path.join(DIR_CAPTURE, f"flow_analysis_cycle_{cycle}.binetflow")
        capture_logger.info("Ciclo %d - Iniciando captura en %s", cycle, current_file)
        capture_service.start_capture(capture_time=capture_time, file_path=current_file)

        # Determinar si se debe ejecutar alguna fase extra en la detección (por ejemplo, stage3_detection)
        ejecutar_stage3 = (cycle % 2 == 0)
        detection_logger.info(
            "Ciclo %d - Iniciando detección entre %s y %s (ejecutar_stage3=%s)",
            cycle, previous_file, current_file, ejecutar_stage3
        )

        # Crear y lanzar el hilo de detección.
        dt = threading.Thread(
            target=detection_service.start_detection,
            args=(previous_file, current_file, ejecutar_stage3)
        )
        dt.start()
        # Aquí esperamos a que el hilo de detección finalice antes de continuar.
        dt.join()

        # Actualizamos el archivo previo para la siguiente iteración.
        previous_file = current_file

    # Devolvemos una respuesta indicando el fin del proceso.
    return {"status": "Scan completed successfully"}
