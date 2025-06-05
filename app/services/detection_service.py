import os
from strategies.dask_flujo_filter_strategy import DaskFlujoFilterStrategy
from strategies.flujo_filter_context import FlujoFilterContext
from modulo.Facade import *
from modulo.metric_extractor.metrics import Metric
from modulo.files.db_handler import save_data_characterization
from modulo.preprocessdata import preprocesssing as pre
from modulo.mlcomponent.component import Component as comp
from modulo.model_selector.selector import Selector
from modulo.Multiclasificador.multiclasifier import Multiclasifier
from app.config.globals import detection_module,OUTPUT_FOLDER

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


def stage3_detection(file_path2):
    if not detection_module:
        raise Exception("Detection module not initialized")
    else:
        # Asegurarse de que la carpeta OUTPUT_FOLDER existe:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Extraer el nombre base del archivo y quitarle la extensión.
        base_name = os.path.basename(file_path2)
        name_without_ext = os.path.splitext(base_name)[0]
        
        # Construir la ruta completa para el archivo filtrado utilizando OUTPUT_FOLDER.
        filtered_file = os.path.join(OUTPUT_FOLDER, f"{name_without_ext}_filtered.binetflow")
        
        # Instanciar la estrategia y el contexto para filtrar el archivo.
        from strategies.dask_flujo_filter_strategy import DaskFlujoFilterStrategy
        from strategies.flujo_filter_context import FlujoFilterContext
        strategy = DaskFlujoFilterStrategy()
        context = FlujoFilterContext(strategy)
        
        # Ejecutar el filtrado: esto leerá file_path2 y generará filtered_file según la lógica definida.
        context.filtrar_flujos(file_path2, filtered_file)
        
        # Inicializar el proceso de detección usando el archivo filtrado.
        init_detection(filtered_file)
        print("prepro", detection_module.data_preprocess)
        detection_module.component_process()  # Se usa la versión actualizada.
        print("listo")
        return {"stage": 3, "characterization_saved": True}



def detection_pipeline(prev_file: str, current_file: str, ejecutar_stage3: bool = True):
    """
    Ejecuta de forma encadenada el proceso de detección:
      - Se inicia el análisis sobre el archivo del ciclo anterior: init_detection, stage1_detection y stage2_detection.
      - Condicionalmente, se invoca stage3_detection sobre el nuevo archivo (current_file) si ejecutar_stage3 es True.
    """
    # Paso 1: Inicia el proceso de detección sobre el archivo del ciclo anterior.
    init_detection(prev_file)
    stage1_detection()
    stage2_detection()
    
    # Paso 2: Ejecutar stage3_detection solo si se requiere (ciclos pares)
    if ejecutar_stage3:
        stage3_detection(current_file)


