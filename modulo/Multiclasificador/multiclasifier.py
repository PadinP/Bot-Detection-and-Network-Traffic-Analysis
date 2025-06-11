import joblib
import glob
import numpy as np
import pandas as pd
from modulo.Multiclasificador.models.individual import Diversity
from modulo.Multiclasificador.models.voting import build_voting_models
from modulo.Multiclasificador.utils.utils import estimators
from app.config.logger_config import detection_logger    

class Multiclasifier:
    def __init__(self):
        # caracterizacion del conjunto de datos a evaluar
        self.metrics = None
        self.database = 'modulo/files/characterization_database.txt'

    def setMetrics(self, metrics):
        self.metrics = metrics

    def build_models(self):
        diversity = Diversity(estimators, self.database)
        diversity.diversity_calc()
        subsets = diversity.select_subsets()
        build_voting_models(subsets, self.database)

    def evaluate(self):
        all_predictions = pd.DataFrame()
        list_models = []
        path_models = f'modulo/Multiclasificador/voting/models_and_evaluation/models/*.pickle'
        for i, modelWithB in enumerate(glob.glob(path_models)):
            model = modelWithB.replace("\\", '/')
            file_name = model.split('/')[-1]
            label = file_name.replace('.pickle', '')
            try:
                if label.startswith('Vot-'):
                    list_models.append(int(label.replace('Vot-', '')))
                else:
                    detection_logger.info(f"Formato inesperado de label: {label}")
            except ValueError as e:
                detection_logger.info(f"Error al convertir label a entero: {e}")

            model_extracted = joblib.load(model)
            np_metrics = np.array(self.metrics)
            if np_metrics.ndim == 1:
                pred_label = model_extracted.predict(np_metrics.reshape(1, -1))
            else:
                pred_label = model_extracted.predict(self.metrics)
            # Añadir predicciones al DataFrame
            all_predictions[f'voting_{label}'] = pred_label

        detection_logger.info('Clasificacion con models voting realizada')
        counts = all_predictions.iloc[0].value_counts()
        detection_logger.info(counts)
        if counts.get(1.0, 0) > counts.get(0.0, 0):
            return 1
        elif counts.get(0.0, 0) > counts.get(1.0, 0):
            return 0
