import os
import threading
from fastapi import APIRouter
from app.config.settings import DIR_CAPTURE
from app.services.capture_service import CaptureService
from app.services.detection_service import DetectionService
from app.config.logger_config import capture_logger, detection_logger

router = APIRouter(tags=["Scan"])

@router.post("/bots_scan")
def run_scan(capture_time: int = 80, cycles: int = 4):
    # Validación temprana: se requieren al menos 2 ciclos para detectar
    if cycles < 2:
        print("Ciclos insuficientes. Se requieren al menos 2 para ejecutar detección.")
        return {"error": "Se requieren al menos 2 ciclos para ejecutar detección de bots."}


    # Aseguramos que exista la carpeta de capturas.
    os.makedirs(DIR_CAPTURE, exist_ok=True)
 
    # Instanciamos los servicios.
    capture_service = CaptureService()
    detection_service = DetectionService()

    # Lista para gestionar los hilos de detección.
    detection_threads = []

    # Primer ciclo: Solo se realiza la captura sin detección.
    current_file = os.path.join(DIR_CAPTURE, "flow_analysis_cycle_1.binetflow")
    capture_logger.info("Ciclo 1 - Iniciando captura en %s", current_file)
    capture_service.start_capture(capture_time=capture_time, file_path=current_file)

    # Guardamos la ruta del archivo del primer ciclo, que se usará en la detección del siguiente ciclo.
    previous_file = current_file

    # Para los ciclos siguientes: captura + detección entre ciclos.
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
        detection_threads.append(dt)

        # Actualizamos el archivo previo para la siguiente iteración.
        previous_file = current_file

    # Esperamos a que todos los hilos de detección finalicen.
    for dt in detection_threads:
        dt.join()

    # Devolvemos una respuesta indicando el fin del proceso.
    return {"status": "Scan completed successfully"}

    # # Si solo se ejecuta un ciclo, aún así se lanza la detección (usando el mismo archivo)
    # if cycles == 1:
    #     detection_logger.info(
    #         "Ciclo 1 - Ejecutando detección sobre un solo archivo: %s",
    #         current_file
    #     )
    #     detection_service.start_detection(current_file, current_file, ejecutar_stage3=False)