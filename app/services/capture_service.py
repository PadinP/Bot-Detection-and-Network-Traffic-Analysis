import multiprocessing
import time
import psutil
from SniffPyBot.features_capture_mp.main import run_capture
from app.config.globals import processes
from SniffPyBot.features_capture_mp.settings import logger as logging

def start_capture(capture_time,sleep_time):
    """
    Inicia la captura en un proceso separado, espera 'capture_time' segundos,
    y luego detiene el proceso de captura.
    
    :param capture_time: Tiempo (en segundos) durante el cual se realizará la captura.
    """
    print("⚡ Captura iniciada...")
    # Crea el proceso para ejecutar 'run_capture'
    process = multiprocessing.Process(target=run_capture)
    process.start()
    processes["capture"] = process

    # Espera el tiempo definido
    time.sleep(capture_time)

    # Detiene la captura y espera a que el proceso finalice
    stop_result = stop_capture(sleep_time)
    print(f"⏹️ Captura detenida después de {capture_time} segundos. Resultado: {stop_result}")

       
    return {"status": "Capture cycle complete"}

def stop_capture(sleep_time):
    """
    Detiene inmediatamente el proceso de captura y bloquea la ejecución
    hasta que se liberen los recursos del proceso. Si el proceso está en ejecución,
    se forza su finalización y se espera un tiempo adicional para asegurar que
    el sistema libere completamente sus recursos.

    :param sleep_time: Tiempo (en segundos) a esperar tras finalizar el proceso.
    :return: Diccionario con el estado resultante del cierre del proceso de captura.
    """
    process = processes.get("capture")
    if process and process.is_alive():
        # Forzar la terminación del proceso
        process.kill()
        # Bloquear hasta que el proceso se finalice y se liberen sus recursos
        process.join()
        print(f"😴 Esperando {sleep_time} segundos para asegurar la liberación completa de recursos...")
        time.sleep(sleep_time)
        print(f"✅ Espera finalizada ({sleep_time} segundos).")
        return {"status": "Capture stopped immediately"}
    
    return {"status": "No active capture process"}
