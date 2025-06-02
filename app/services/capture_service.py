import multiprocessing
import time
import psutil
from SniffPyBot.features_capture_mp.main import run_capture
from app.config.globals import processes
from SniffPyBot.features_capture_mp.settings import logger as logging

def start_capture(capture_time, file_path):
    """
    Inicia la captura en un proceso separado, espera capture_time segundos,
    y luego detiene el proceso de captura.
    :param capture_time: Tiempo (en segundos) de la captura.
    :param file_path: Ruta del archivo para la captura.
    """
    print("⚡ Captura iniciada...")
    # Se corrige la forma de pasar argumentos al proceso
    process = multiprocessing.Process(target=run_capture, args=(file_path,))
    process.start()
    processes["capture"] = process

    # Espera el tiempo definido
    time.sleep(capture_time)

    # Detiene la captura y espera que el proceso finalice
    stop_result = stop_capture()
    print(f"⏹️ Captura detenida después de {capture_time} segundos. Resultado: {stop_result}")
    return {"status": "Capture cycle complete"}

def stop_capture():
    sleep_time = 15
    process = processes.get("capture")
    if process and process.is_alive():
        process.kill()
        process.join()
        print(f"😴 Esperando {sleep_time} segundos para liberar recursos...")
        time.sleep(sleep_time)
        print(f"✅ Espera finalizada ({sleep_time} segundos).")
        return {"status": "Capture stopped immediately"}
    
    return {"status": "No active capture process"}
