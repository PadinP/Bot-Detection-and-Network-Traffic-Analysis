from MyBaseHechos import managed_load, calculateAll
from Facade import managed_classification_process_NoLoad
from utils import utils
from models.proactive_forest_classifier import PFClassifier
from models.adaboost import ABClassifier
from models.decision_tree import *
from modulo import GradientClassifier
from models.random_forest_classifier import *
from models.knn_classifier import *
import pandas as pd
import numpy as np
import time
from preprocessdata.preprocess import data_cleaning, data_transform, class_balance
import joblib

samples = [
    [0 * 20, 5000 * 20],
    # [750*20, 4250*20],
    # [1000*20, 4000*20],
    # [1250*20, 3750*20],
    # [1500*20, 3500*20],
    # [1750*20, 3250*20],
    # [2000*20, 3000*20],
    # [2250*20, 2750*20],
    # [2500*20, 2500*20],
    # [4500*20, 500*20],
    # [4250*20, 750*20],
    # [4000*20, 1000*20],
    # [3750*20, 1250*20],
    # [3500*20, 1500*20],
    # [3250*20, 1750*20],
    # [3000*20, 2000*20],
    # [2750*20, 2250*20],
]


def createDataset():
    modelList = [
        # joblib.load('model-load/pfr_model_central1.joblib'),
        # joblib.load('model-load/pfr_model_central2.joblib'),
        # joblib.load('model-load/pfr_model_central3.joblib'),
        # joblib.load('model-load/rf_model_central1.joblib'),
        # joblib.load('model-load/rf_model_central2.joblib'),
        # joblib.load('model-load/rf_model_central3.joblib'),
        # joblib.load('model-load/dt_model_central1.joblib'),
        # joblib.load('model-load/dt_model_central2.joblib'),
        # joblib.load('model-load/dt_model_central3.joblib'),
        # joblib.load('model-load/knn_model_central1.joblib'),
        # joblib.load('model-load/knn_model_central2.joblib'),
        # joblib.load('model-load/knn_model_central3.joblib'),
        # joblib.load('model-load/ab_model_central1.joblib'),
        # joblib.load('model-load/ab_model_central2.joblib'),
        joblib.load('modulo/model-load/ab_model_central3.joblib'),
        # joblib.load('model-load/gtb_model_central1.joblib'),
        # joblib.load('model-load/gtb_model_central2.joblib'),
        # joblib.load('model-load/gtb_model_central3.joblib'),
    ]
    escenarios = ['0']
    for e in escenarios:
        print(f'Esc {e}')
        mcList = []
        for s in range(len(samples)):
            print(f'sample {s + 1}')
            sample = samples[s]
            escWrapper = []
            for t in range(25):
                since = t * 50000
                data, label = managed_load(since=since, untilBot=sample[0], untilHuman=sample[1], e=e, smote=True)
                if len(label) != 100000:
                    counts = np.unique(label, return_counts=True)
                    print('>>>>>>>>>>>>>>>>>')
                    print(">>>INVALID LEN>>>")
                    print(len(label))
                    print(counts)
                    print('>>>>>>>>>>>>>>>>>')
                normaldata, normalLabel = managed_load(since=0, untilBot=0, untilHuman=len(data), e='0')
                metrics_characterization = calculateAll(data, normaldata, e)

                # lista de accuracy de los modelos en orden Random Forest, KNN, Decision Tree, Adaboost, Gradient
                avgList = []

                for m in modelList:
                    avg = managed_classification_process_NoLoad(m, data, label)
                    avgList.append(avg)
                metrics_characterization.extend(avgList)
                escWrapper.append(metrics_characterization)
            mcList.extend(escWrapper)
        csv = pd.DataFrame(mcList,
                           columns=['cusum', 'nCusum', 'ShannonEntropy', 'jensen-shannon', 'mahalanobis', 'iqr', 'mad',
                                    'ADA3'])
        csv.to_csv(f'cd_{e}.csv')


def smote():
    data = pd.read_csv('cd_0.csv')
    X = data.iloc[:, :-1]  # Todas las columnas menos la última
    Y = data.iloc[:, -1]
    X_balanced, y_balanced = class_balance(sampler='smote', data_x=X, data_y=Y).sampling()
    X_balanced['class'] = y_balanced
    print(X_balanced)
    X_balanced.to_csv('fi.csv')

def train_m():
    e = '0'
    print(f'Training e = {e}')
    model_filename = [
        "PF_model_20k.joblib",
        "RF_model_20k.joblib",
        "RF_model_20kv2.joblib",
        "RF_model_20kv3.joblib",
        "KNN_model_20k.joblib",
        "DT_model_20k.joblib",
        "ABC_model_20k.joblib",
        "GRA_model_20k.joblib"
    ]
    candiates = [
        PFClassifier(escenario=e, k=5),
        RFClassifier(escenario=e, k=5),
        RFClassifier(escenario=e, k=5),
        RFClassifier(escenario=e, k=5),
        KNNClassifier(n_neighbors=5, escenario=e),
        DecisionTree(escenario=e, test_size=0.2),
        ABClassifier(escenario=e, k=5),
        GradientClassifier.GClassifier(n_estimators=250, escenario=e, k=5)
    ]
    for i in range(len(candiates)):
        m = candiates[i]
        name = model_filename[i]
        pfc_model = m
        # pfc = RFClassifier(escenario=e, k=5)
        # pfc = PFClassifier(escenario=e, k=5)
        # pfc = KNNClassifier(n_neighbors=5, escenario='0')
        # pfc = DecisionTree(escenario='0', test_size=0.2)
        # pfc = ABClassifier(escenario='0', k=5)
        # pfc = GradientClassifier.GClassifier(n_estimators=250, escenario='0', k=5)
        train, test = m.prepareData()  # preprocesamiento
        if len(train) != 0:
            pfc_model, avg, max_score = utils.cross_validation_train(m, train, test)
        print('dumping')
        print(name)
        joblib.dump(pfc_model, name)


if __name__ == '__main__':
    # train_m()
    # df = pd.concat([pd. read_csv(f'metricas_escenario_{i+1}.csv') for i in range(5)])
    # df.to_csv("CSV_completo")
    # start_time = time.time()
    # createDataset()
    # end_time = time.time()
    # print(f"Process completed in {end_time - start_time:.2f} seconds.")
    smote()
