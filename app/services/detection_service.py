import os
import numpy as np
from Facade import *
from files.db_handler import save_data_characterization
from app.config.settings import OUTPUT_FOLDER
from app.config.logger_config import detection_logger 
from deteccion import DetectionModule 

class DetectionService:
    def __init__(self):
        """
        Inicializa el servicio de detección creando una instancia de DetectionModule.
        """
        self.detection_module = DetectionModule()
        
    def init_detection(self, file_path):
        """
        Inicializa el módulo de detección con el archivo provisto.
        """
        detection_logger.info(f"---- inicializando con: {file_path}")
        self.detection_module.set_data(file_path)
        return {"status": "Detection module initialized", "FILE_PATH": file_path}
    
    def stage1_detection(self):
        """
        Ejecuta el primer paso de la detección, que incluye preprocesamiento,
        extracción de características y la ejecución de la multiclasificación.
        """
        if not self.detection_module:
            raise Exception("Detection module not initialized")
        detection_logger.info("---- stage1_detection start ----")
        self.detection_module.preprocess_data()
        self.detection_module.run_charac()
        result = self.detection_module.multiclasifier_process()
        self.detection_module.multiclasifier_result = result  
        detection_logger.info("---- stage1_detection end ----")
        return {"stage": 1, "bots_detected": bool(result)}
    
    def stage2_detection(self):
        """
        Ejecuta el segundo paso de detección: si no hay bots detectados se guarda la
        caracterización; de lo contrario, se realiza la clasificación.
        """
        detection_logger.info("---- stage2_detection start ----")
        if not self.detection_module:
            raise Exception("Detection module not initialized")
        
        if hasattr(self.detection_module, 'multiclasifier_result') and self.detection_module.multiclasifier_result == 0:
            save_data_characterization(self.detection_module.data_charac)
            detection_logger.info("---- stage2_detection end ----")
            return {
                "stage": 2,
                "message": "No bots detected. Classification skipped and characterization saved.",
                "bots_count": 0
            }
        else:
            self.detection_module.select_model()
            predictions = self.detection_module.classification_process()
            amountHumans = np.sum(predictions == 0)
            detection_logger.info(f'Cantidad de Humanos: {amountHumans}')
            amount_bots = int(np.sum(predictions == 1))
            detection_logger.info(f"Cantidad de bots: {amount_bots}")
            detection_logger.info("---- stage2_detection end ----")
            return {"stage": 2, "bots_count": amount_bots}
    
    def stage3_detection(self, file_path2):
        """
        Ejecuta el tercer paso de detección:
          - Filtra el archivo utilizando la estrategia definida.
          - Re-inicializa el módulo con el archivo filtrado.
          - Procesa la detección final.
        """
        detection_logger.info("---- stage3_detection start ----")
        if not self.detection_module:
            raise Exception("Detection module not initialized")
        
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        base_name = os.path.basename(file_path2)
        name_without_ext = os.path.splitext(base_name)[0]
        filtered_file = os.path.join(OUTPUT_FOLDER, f"{name_without_ext}_filtered.binetflow")
        
        from strategies.dask_flujo_filter_strategy import DaskFlujoFilterStrategy
        from strategies.flujo_filter_context import FlujoFilterContext
        strategy = DaskFlujoFilterStrategy()
        context = FlujoFilterContext(strategy)
        context.filtrar_flujos(file_path2, filtered_file)
        
        self.init_detection(filtered_file)
        # Asegúrate de llamar correctamente a estos métodos o atributos según tu implementación.
        self.detection_module.component_process()
        detection_logger.info("---- stage3_detection end ----")
        return {"stage": 3, "characterization_saved": True}
    
    def start_detection(self, prev_file: str, current_file: str, ejecutar_stage3: bool = True):
        """
        Ejecuta de forma encadenada el proceso completo de detección:
          - Inicializa el módulo con el archivo del ciclo anterior.
          - Ejecuta stage1 y stage2.
          - Ejecuta stage3 condicionalmente.
        """
        self.init_detection(prev_file)
        self.stage1_detection()
        self.stage2_detection()
        
        if ejecutar_stage3:
            self.stage3_detection(current_file)

