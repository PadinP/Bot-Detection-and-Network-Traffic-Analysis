import joblib
import numpy as np
from Facade import *
from metric_extractor.metrics import Metric
from files.db_handler import save_data_characterization
from preprocessdata import preprocesssing as pre
from mlcomponent.component import Component as comp
from model_selector.selector import Selector
from Multiclasificador.multiclasifier import Multiclasifier

from app.config.logger_config import detection_logger  

class DetectionModule:
    def __init__(self):
        self.selector = Selector()
        self.multiclasifer = Multiclasifier()
        self.selected_model = None
        self.data = None  # Ruta al archivo .binetflow
        self.data_preprocess = None
        self.data_charac = None
        self.data_explained_variance_ratio = None

    def set_data(self, data):
        self.data = data

    def run_charac(self):
        metricCalc = Metric(self.data_preprocess, self.data_explained_variance_ratio)
        self.data_charac = metricCalc.run_metrics()

    def preprocess_data(self, scalers='minmax', samplers='smote'):
        final_data, final_labels, explained_variance_ratio = pre.preprocessing(self.data, scalers, samplers)
        self.data_preprocess = final_data
        self.data_explained_variance_ratio = explained_variance_ratio

    def select_model(self):
        self.selector.loadModels()
        modelAcc = self.selector.predict(X=self.data_charac)
        
        # Cuento la cantidad total de modelos
        total_models = len(modelAcc)
        detection_logger.info(f'Total models: {total_models}')
        
        # Imprimo la lista completa de precisiones
        detection_logger.info(f'Model accuracies: {modelAcc}')
        
        # Selecciono el mejor modelo
        bestAcc = max(modelAcc)
        bestAccIndex = modelAcc.index(bestAcc)
        modelName = self.selector.column_names[bestAccIndex]
        detection_logger.info(f'Best model: {modelName}, acc = {bestAcc}')

        # Ruta relativa al archivo del modulo
        filepath = f"model_load/{modelName}.joblib"
       
        # Verificar si existe el archivo
        try:
            self.selected_model = joblib.load(filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"El archivo {filepath} no se encontró. Verifica la estructura de carpetas.")

        detection_logger.info(f'Cargando el modulo desde: {filepath}')

    def multiclasifier_process(self):
        self.multiclasifer.setMetrics(self.data_charac)
        self.multiclasifer.build_models()
        result = self.multiclasifer.evaluate()
        return result

    def classification_process(self):
        y = self.selected_model.predict(self.data_preprocess)
        return y

    def component_process(self):
        detection_logger.info('Inicializando meta-componente\n')
        component = comp(expVariance=self.data_explained_variance_ratio)
        component.x_positives = self.data_preprocess
        component.run_charact()

def main():
    dm = DetectionModule()
    dm.set_data('100K.binetflow')
    dm.preprocess_data()
    dm.run_charac()
    detection_logger.info('Datos preprocesados y métricas calculadas')
    # etapa 1
    tieneBots = dm.multiclasifier_process()
    if tieneBots == 0:
        save_data_characterization(dm.data_charac)
        return
     # hay bots, pasando a la etapa 2
    dm.select_model()
    predictions = dm.classification_process()
    amountBots = np.sum(predictions == 1)
    amountHumans = np.sum(predictions == 0)
    detection_logger.info(f'Cantidad de Bots: {amountBots}')
    detection_logger.info(f'Cantidad de Humanos: {amountHumans}')
     # Etapa 3
    dm.component_process()

if __name__ == "__main__":
    main()
