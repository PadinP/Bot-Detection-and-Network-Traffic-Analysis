from modulo.Facade import *
from modulo.metric_extractor.metrics import Metric
from modulo.files.db_handler import save_data_characterization
from modulo.preprocessdata import preprocesssing as pre
from modulo.mlcomponent.component import Component as comp
from modulo.model_selector.selector import Selector
from modulo.Multiclasificador.multiclasifier import Multiclasifier
from app.config.globals import detection_module

def init_detection(file_path):
    detection_module.set_data(file_path)
    return {"status": "Detection module initialized", "FILE_PATH": file_path}

def stage1_detection():
    if not detection_module:
        raise Exception("Detection module not initialized")
    detection_module.preprocess_data()
    detection_module.run_charac()
    result = detection_module.multiclasifier_process()
    detection_module.multiclasifier_result = result  
    return {"stage": 1, "bots_detected": bool(result)}

def stage2_detection():
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
    if not detection_module:
        raise Exception("Detection module not initialized")
    else:
        file_path2 = "modulo/capturas/flow_analysis_cycle_2_20250602.binetflow"
        init_detection(file_path2)
        print("prepro", detection_module.data_preprocess)
        detection_module.component_process()  # Aquí se usa la versión actualizada.
        print("listo")
        return {"stage": 3, "characterization_saved": True}

def detection_run_all(file_path):
    print("🚀 Iniciando proceso de detección...")
    try:
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
        raise
    return detection_result
