import multiprocessing
import time
from SniffPyBot.features_capture_mp.main import run_capture
from app.config.settings import DIR_CAPTURE
from app.config.logger_config import capture_logger  # Importa el logger configurado

class CaptureService:
    def __init__(self):
        # Diccionario para almacenar las referencias a los procesos.
        self.processes = {}

    def start_capture(self, capture_time, file_path):
        """
        Inicia la captura en un proceso separado, espera `capture_time` segundos,
        y luego detiene el proceso de captura.
        """
        capture_logger.info("⚡ Captura iniciada...")
        # Crea y ejecuta el proceso de captura.
        process = multiprocessing.Process(target=run_capture, args=(file_path,))
        process.start()
        self.processes["capture"] = process

        # Espera el tiempo determinado para la captura.
        time.sleep(capture_time)
        stop_result = self.stop_capture()

        capture_logger.info(f"⏹️ Captura detenida después de {capture_time} segundos. Resultado: {stop_result}")
        return {"status": "Capture cycle complete"}

    def stop_capture(self):
        """
        Detiene el proceso de captura si está activo y espera un tiempo para liberar recursos.
        """
        sleep_time = 15
        process = self.processes.get("capture")
        if process and process.is_alive():
            process.kill()
            process.join()
            capture_logger.info(f"😴 Esperando {sleep_time} segundos para liberar recursos...")
            time.sleep(sleep_time)
            capture_logger.info(f"✅ Espera finalizada ({sleep_time} segundos).")
            return {"status": "Capture stopped "}
        return {"status": "No active capture process"}
