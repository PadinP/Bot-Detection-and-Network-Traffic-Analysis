from itertools import combinations
import pandas as pd
import os
from modulo.Multiclasificador.utils import utils

estimators = utils.estimators


def create_individual_classifiers(data_path, estimators_dict):
    """
    Function to create each individual classifier. It will load the characterization database and train each model.
    :param data_path: Recibe un txt
    :param estimators_dict: diccionarios con los algoritmos supervisados
    :return:
    """
    data = utils.loadData(data_path)
    n_columns = data.shape[1]
    x_instances = data[:, :n_columns - 1]
    y_instances = data[:, -1]
    predictions = pd.DataFrame(columns=estimators_dict.keys())

    for key in estimators_dict.keys():
        model = estimators_dict[key].fit(x_instances, y_instances)
        estimators_dict[key] = model
        predictions[key] = estimators_dict[key].predict(x_instances)
    return predictions, y_instances


class Diversity:
    def __init__(self, estimators_dict, data):
        self.data = data
        self.estimators = estimators_dict
        self.file = 'modulo/diversity_values.csv'
        # self.predictions son las predicciones de la base de hechos de cada modulo (CART, LR, NAIVE...)
        # self.y son los valores de clase verdaderos
        self.predictions, self.y = create_individual_classifiers(self.data, self.estimators)
        self.columns = self.predictions.columns

    def diversity_calc(self):
        if os.path.exists(self.file):
            os.remove(self.file)

        for length in range(2, len(self.columns) + 1):
            combiner = combinations(self.columns, length)
            for subset in list(combiner):
                subset_columns = list(subset)
                selected_dataframe = self.predictions[subset_columns]
                df, p, q, d = utils.DiversityMeasures(y=self.y, predictions=selected_dataframe).get_measures()
                results = [df, p, q, d]
                with open(self.file, 'a') as f:
                    utils.selected_conbination(subset_columns, results, f)

    def select_subsets(self):
        names = ['subset', 'df', 'p', 'q', 'd']
        div_data = pd.read_csv(self.file, sep=';', names=names, index_col='subset', na_filter=True, header=None)
        # ordenar segun la combinación más diversidad
        dataframe_ordered = div_data.sort_values(['q', 'df', 'd'],
                                                 na_position='last',
                                                 ascending=[True, True, False]
                                                 )
        # descending_ord = ascending_ord.sort_values('d', na_position='last', ascending=False)
        selected = list(dataframe_ordered.head(15).index)
        dataframe_ordered.head(15).to_csv('modulo/combinaciones.csv', sep=';')
        out_dict = utils.create_list_tuple(selected, estimators)

        return out_dict
