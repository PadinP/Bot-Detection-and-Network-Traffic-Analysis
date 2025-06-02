# detection_service.py
import numpy as np
from modulo.Facade import *
from modulo.metric_extractor.metrics import Metric
from modulo.files.db_handler import save_data_characterization
from modulo.preprocessdata import preprocesssing as pre
from modulo.mlcomponent.component import Component as comp
from modulo.model_selector.selector import Selector
from modulo.Multiclasificador.multiclasifier import Multiclasifier
from app.config.globals import detection_module

def init_detection(file_path):
    """Inicializa el módulo de detección con el archivo de datos."""
    detection_module.set_data(file_path)
    return {"status": "Detection module initialized", "FILE_PATH": file_path}

def stage1_detection():
    """
    Stage 1: Preprocesa los datos, extrae métricas y evalúa multiclasificador.
    """
    if not detection_module:
        raise Exception("Detection module not initialized")
    detection_module.preprocess_data()
    detection_module.run_charac()
    result = detection_module.multiclasifier_process()
    # Guarda el resultado para futuras etapas.
    detection_module.multiclasifier_result = result  
    return {"stage": 1, "bots_detected": bool(result)}

def stage2_detection():
    """
    Stage 2: Selección de modelo y clasificación si se detectan bots.
    Si `multiclasifier_process` devolvió 0 (no bots), se guarda la caracterización sin clasificación.
    """
    if not detection_module:
        raise Exception("Detection module not initialized")
    
    if hasattr(detection_module, 'multiclasifier_result') and detection_module.multiclasifier_result == 0:
        save_data_characterization(detection_module.data_charac)
        return {
            "stage": 2,
            "message": "No bots detected. Classification skipped and characterization saved.",
            "bots_count": 0
        }
    else:
        detection_module.select_model()
        predictions = detection_module.classification_process()
        detection_module.predictions = predictions  
        amount_bots = int(np.sum(predictions == 1))
        return {"stage": 2, "bots_count": amount_bots}

def stage3_detection():
    """
    Stage 3: Análisis de componentes y guarda la caracterización.
    En caso de haber clasificación, usa el resultado de la etapa 2.
    """
    if not detection_module:
        raise Exception("Detection module not initialized")
    
    if hasattr(detection_module, 'multiclasifier_result') and detection_module.multiclasifier_result == 0:
         return {
             "stage": 3,
             "message": "No bots detected. Characterization was already saved in stage2."
         }
    else:
         if not hasattr(detection_module, 'predictions'):
             raise Exception("Predictions not available. Run stage2 first.")
         predictions = detection_module.predictions
         detection_module.component_process(predictedLabels=predictions)
         return {"stage": 3, "characterization_saved": True}

def detection_run_all(file_path):
    """
    Ejecuta todas las etapas de detección en orden.
    """
    print("🚀 Iniciando proceso de detección...")
    try:
        # Ejecuta las diferentes etapas de la detección
        result_init = init_detection(file_path)
        result_stage1 = stage1_detection()
        result_stage2 = stage2_detection()
        result_stage3 = stage3_detection()
        detection_result = {
            "run_all": True,
            "stages": [result_init, result_stage1, result_stage2, result_stage3]
        }
        print("✅ Detección completada:", detection_result)
    except Exception as ex:
        print("❌ Error en la detección:", ex)
        raise  # Re-lanza la excepción para que el error pueda ser manejado a niveles superiores, si es necesario.
    
    return detection_result
