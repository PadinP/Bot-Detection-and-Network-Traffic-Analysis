
import joblib
import pickle
import numpy as np
from datetime import datetime

from preprocessdata.utils import create_folder
from preprocessdata.preprocess import data_cleaning, data_transform, class_balance
from colorama import Fore, init

init()


def preprocessing(data, scaler, sampler):
    """
    :param data: Path del conjunto de datos con codificación basada en glob.
    :param scaler: Escaldor seleccionado.
    :param sampler: Tipo de muestreo seleccionado.
    :return:
    """
    # print(f"data {data}")
    # name = data.split('\\')[-1]
    # label = name.replace('.binetflow', '')
    label = datetime.now().strftime('%Y-%m-%d %H_%M_%S')



    folders = 'database-preprosesing/' + sampler + '/' + label + '/' + scaler + '/models'
    name_scaler_model = 'database-preprosesing/' + sampler + '/' + label + '/' + scaler + '/models/' + label + '.' + scaler + \
                        '_model.pickle '
    name_pca_model = 'database-preprosesing/' + sampler + '/' + label + '/' + scaler + '/models/' + label + '.' + scaler + \
                     '_PCA_model.pickle'
    name_scaled_data = 'database-preprosesing/' + sampler + '/' + label + '/' + scaler + '/' + label + '.' + scaler + '.pickle'
    name_sampled_data = 'database-preprosesing/' + sampler + '/' + label + '/' + scaler + '/' + label + '.' + scaler + '_' + \
                        sampler + '.pickle'
    # Crea las carpertas de forma recursiva
    create_folder(folders)

    # Carga los datos
    X, y = data_cleaning(escenario=data, sep=',', label_scenarios=label).loaddata()

    # Escala y reduce la dimensionalidad de los datos
    X_trans, scaler_model, pca_model = data_transform(scaler=scaler, data=X).selection()
    # pca_model.explained_variance_ratio_

    # Almacenar los modelos del escaldo, pca
    joblib.dump(scaler_model, r'' + name_scaler_model)
    joblib.dump(pca_model, r'' + name_pca_model)

    if sampler == 'no_balanced':
        # Almacenar los datos no balanceados
        final_data = [np.array(X_trans), np.array(y)]
        try:
            file = open(name_scaled_data, 'wb')
            pickle.dump(final_data, file)
            file.close()
        except Exception as e:
            print(e)
    else:
        # Balancear y almacenar los datos
        X_balanced, y_balanced = class_balance(sampler=sampler, data_x=X_trans, data_y=y).sampling()
        final_data = [np.array(X_balanced), np.array(y_balanced)]
        try:
            file = open(name_sampled_data, 'wb')
            pickle.dump(final_data, file)
            file.close()
        except Exception as e:
            print(e)
    return final_data[0], final_data[1], pca_model.explained_variance_ratio_
