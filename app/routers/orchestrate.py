# from fastapi import APIRouter, HTTPException
# import multiprocessing
# import time
# import threading

# # Importa la función que ejecuta la captura.
# # Asegúrate de importar de la ruta correcta (según cómo esté estructurado tu proyecto),
# # por ejemplo, si run_capture se expone en SniffPyBot/features_capture_mp/main.py.
# from SniffPyBot.features_capture_mp.main import run_capture

# # Diccionario global que se usa para gestionar procesos (por ejemplo, para detener la captura).
# from app.config.globals import processes

# # Importa la función de detección.
# # Si detection_run_all está definida en el router de detección, 
# # evalúa si puedes extraer la lógica a un módulo común o llamarla directamente.
# from app.routers.detectar import detection_run_all

# router = APIRouter(prefix="/orchestrate", tags=["Orchestrator"])

# @router.post("/cycle")
# def orchestrate_cycle(capture_time: int = 60, sleep_time: int = 30):
#     """
#     Ejecuta un ciclo continuo donde:
#       - Se inicia la captura durante 'capture_time' segundos.
#       - Se detiene la captura.
#       - Se ejecutan todas las etapas del módulo de detección.
#       - Se espera 'sleep_time' segundos antes de reiniciar el ciclo.
#     """
#     def cycle():
#         while True:
#             print("🔄 Iniciando ciclo de captura y detección.")

#             # Inicia la captura en un proceso separado.
#             print("⚡ Captura iniciada...")
#             process = multiprocessing.Process(target=run_capture)
#             process.start()
#             processes["capture"] = process

#             # Espera el tiempo de captura.
#             time.sleep(capture_time)

#             # Termina la captura si aún sigue en ejecución.
#             if process.is_alive():
#                 process.terminate()
#                 process.join()
#                 print(f"⏹️ Captura detenida después de {capture_time} segundos.")

#             # Ejecuta las etapas del módulo de detección.
#             print("🚀 Iniciando proceso de detección...")
#             try:
#                 # Llamamos a detection_run_all para ejecutar las etapas (init, stage1, stage2, stage3).
#                 detection_result = detection_run_all()
#                 print("✅ Detección completada:", detection_result)
#             except Exception as ex:
#                 print("❌ Error en la detección:", ex)
            
#             # Espera antes de reiniciar el ciclo.
#             print(f"😴 Esperando {sleep_time} segundos antes de reiniciar la captura.")
#             time.sleep(sleep_time)
    
#     # Se lanza la función de ciclo en un hilo daemon para que no bloquee el endpoint.
#     threading.Thread(target=cycle, daemon=True).start()
#     return {
#         "status": "Orchestrator cycle started",
#         "capture_time": capture_time,
#         "sleep_time": sleep_time
#     }

# from fastapi import APIRouter, HTTPException
# import multiprocessing
# import time
# import threading
# import psutil

# # Importa la función que ejecuta la captura.
# from SniffPyBot.features_capture_mp.main import run_capture

# # Diccionario global para gestionar procesos.
# from app.config.globals import processes

# # Importa la función de detección.
# from app.routers.bot_detection import detection_run_all

# router = APIRouter(prefix="/orchestrate", tags=["Orchestrator"])

# @router.post("/cycle")
# def orchestrate_cycle(capture_time: int = 60, sleep_time: int = 30):
#     """
#     Ejecuta un ciclo continuo donde:
#       - Se inicia la captura durante 'capture_time' segundos.
#       - Se detiene la captura.
#       - Se ejecutan todas las etapas del módulo de detección.
#       - Se espera 'sleep_time' segundos antes de reiniciar el ciclo.
#     """
#     def cycle():
#         while True:
#             print("🔄 Iniciando ciclo de captura y detección.")

#             # Inicia la captura en un proceso separado.
#             print("⚡ Captura iniciada...")
#             process = multiprocessing.Process(target=run_capture)
#             process.start()
#             processes["capture"] = process

#             # Espera el tiempo de captura.
#             time.sleep(capture_time)

#             # Termina la captura si aún sigue en ejecución.
#             if process.is_alive():
#                 process.terminate()
#                 process.join()
#                 print(f"⏹️ Captura detenida después de {capture_time} segundos.")

#                 # Verifica a nivel de sistema si el proceso aún existe.
#                 if not psutil.pid_exists(process.pid):
#                     print(f"El proceso {process.pid} ya no se encuentra en ejecución.")
#                 else:
#                     print(f"El proceso {process.pid} sigue activo.")
            
#             # Verifica que el proceso de captura se haya finalizado y busca procesos hijos asociados.
#             if not process.is_alive():
#                 print("El proceso de captura ha terminado.")
#                 # Verifica que no existan procesos hijos huérfanos asociados al PID terminado.
#                 for proc in psutil.process_iter(['pid', 'ppid', 'name']):
#                     if proc.info['ppid'] == process.pid:
#                         print(f"Aún existe un proceso hijo: {proc.info['pid']} - {proc.info['name']}")

#             # Ejecuta las etapas del módulo de detección.
#             print("🚀 Iniciando proceso de detección...")
#             try:
#                 # Llamamos a detection_run_all para ejecutar las etapas (init, stage1, stage2, stage3).
#                 detection_result = detection_run_all()
#                 print("✅ Detección completada:", detection_result)
#             except Exception as ex:
#                 print("❌ Error en la detección:", ex)
            
#             # Espera antes de reiniciar el ciclo.
#             print(f"😴 Esperando {sleep_time} segundos antes de reiniciar la captura.")
#             time.sleep(sleep_time)
    
#     # Se lanza la función de ciclo en un hilo daemon para que no bloquee el endpoint.
#     threading.Thread(target=cycle, daemon=True).start()
#     return {
#         "status": "Orchestrator cycle started",
#         "capture_time": capture_time,
#         "sleep_time": sleep_time
#     }

# orchestrator endpoint: app/routers/orchestrate.py
# app/routers/orchestrate.py
import sys
import time
from fastapi import APIRouter
from app.services.bot_detection_service import detection_run_all  # Función que ejecuta el proceso de detección
from app.services.capture_service import start_capture  # Función que inicia la captura (implementada con run_capture y stop_capture internamente)

router = APIRouter(prefix="/orchestrate", tags=["Orchestrator"])

@router.post("/cycle")
def orchestrate_cycle(capture_time: int = 60, cycles: int = 3, sleep_time: int = 30):
    """
    Ejecuta en bucle la captura de tráfico durante un tiempo determinado
    y luego el proceso de detección. Se repite la secuencia una cantidad de
    ciclos definidos por el parámetro 'cycles'.

    Nota: El bucle a continuación se queda estancado imprimiendo "hola" cada 30 segundos
    a menos que se invoque sys.exit() para detener el proceso.
    """
    cycles_results = []
    
    for i in range(cycles):
        print(f"\n--- Ciclo {i+1} de {cycles} ---")
        
        # Inicia la captura
        capture_result = start_capture(capture_time=capture_time, sleep_time= sleep_time)
                
        # El siguiente bloque de código nunca se alcanzará a menos que se salga del bucle
        try:
            detection_result = detection_run_all()
        except Exception as ex:
            detection_result = {"error": str(ex)}
        
        cycles_results.append({
            "cycle": i + 1,
            "capture_result": capture_result,
            "detection_result": detection_result
        })
        
        time.sleep(1)
    
    return {"cycles": cycles_results}
