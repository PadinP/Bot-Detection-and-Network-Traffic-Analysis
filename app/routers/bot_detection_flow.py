from fastapi import APIRouter
from app.services.detection_service import detection_run_all  # Función que ejecuta el proceso de detección
from app.services.capture_service import start_capture  # Función que inicia la captura (implementada con run_capture y stop_capture internamente)

router = APIRouter(prefix="/bots_scan  ", tags=["Scan"])

@router.post("/bots_scan  ")
def orchestrate_cycle(capture_time: int = 60, cycles: int = 3):
    """
    Ejecuta en bucle la captura de tráfico durante un tiempo determinado
    y luego el proceso de detección. Se repite la secuencia una cantidad de
    ciclos definidos por el parámetro 'cycles'.

    """
    cycles_results = []
    
    for i in range(cycles):
        print(f"\n--- Ciclo {i+1} de {cycles} ---")
        
        # Inicia la captura
        capture_result = start_capture(capture_time = capture_time)
                
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
    
    return {"cycles": cycles_results}
