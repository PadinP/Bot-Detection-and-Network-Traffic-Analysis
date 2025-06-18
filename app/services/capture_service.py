import multiprocessing 
import time
import sys
import os
from SniffPyBot.features_capture_mp.capture import Capture
from SniffPyBot.features_capture_mp.network_utils import verify_interface
from app.config.settings import NETWORK_INTERFACE, PCAP_FILE
from app.config.logger_config import capture_logger

class CaptureService:
    def __init__(self):
        # Diccionario para almacenar las referencias a los procesos activos.
        self.processes = {}

    def start_capture(self, capture_time: int, file_path: str) -> dict:
        """
        Inicia la captura en un proceso separado, permitiendo que se ejecute durante
        'capture_time' segundos y luego detiene la captura.
        """
        capture_logger.info("⚡ Inicio de captura...")
        process = multiprocessing.Process(
            target=CaptureService.run_capture,  # Se invoca el método estático.
            args=(file_path,)
        )
        process.start()
        self.processes["capture"] = process

        # Se permite que la captura se ejecute durante el tiempo especificado.
        time.sleep(capture_time)
        result = self.stop_capture()

        capture_logger.info(
            f"⏹️ Captura detenida después de {capture_time} segundos. Resultado: {result}"
        )
        return {"status": "Ciclo de captura completado"}

    def stop_capture(self) -> dict:
        """
        Detiene el proceso de captura si existe y se encuentra activo.
        Luego, espera un periodo para liberar los recursos asociados.
        """
        sleep_time = 15
        process = self.processes.get("capture")
        if process and process.is_alive():
            process.kill()    # Finaliza el proceso de captura.
            process.join()    # Asegura el cierre correcto del proceso.
            capture_logger.info(f"😴 Esperando {sleep_time} segundos para liberar recursos...")
            time.sleep(sleep_time)
            capture_logger.info(f"✅ Espera finalizada ({sleep_time} segundos).")
            return {"status": "Captura detenida"}
        return {"status": "No hay proceso de captura activo"}

    @staticmethod
    def run_capture(file_path: str):
        """
        Arranca el proceso de captura, verificando la existencia de la interfaz.
        Utiliza la configuración establecida para la interfaz de red y el archivo PCAP.
        """
        pid = os.getpid()
        print("PID: %s" % pid)
        print("La interfaz %s existe, empezando la aplicación" % NETWORK_INTERFACE)
        if verify_interface(NETWORK_INTERFACE):
            capture = Capture(NETWORK_INTERFACE, PCAP_FILE, file_path)
            capture.start()
        else:
            print("La interfaz %s no existe, terminando la aplicación" % NETWORK_INTERFACE)
            sys.exit()