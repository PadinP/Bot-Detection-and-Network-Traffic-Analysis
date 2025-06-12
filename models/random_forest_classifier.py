import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import decomposition
from utils import utils, LoadData
from preprocessdata import preprocesssing as pre


class RFClassifier(RandomForestClassifier):
    def __init__(self, n_estimators=250, max_features='sqrt', escenario="11", k=5, test_size=0.2):
        super().__init__(n_estimators=n_estimators, max_features=max_features, criterion='entropy', random_state=0)
        self.escenario = f"database-preprosesing/smote/" + escenario + "/minmax/" + escenario + ".minmax_smote.pickle"
        self.escenario_noBalanced = f"database-preprosesing/no_balanced/" + escenario + "/minmax/" + escenario + ".minmax.pickle"
        self.test_size = test_size
        self.k = k

    def fit(self, X_train, y_train):
        return super().fit(X_train,y_train)

    def predict(self,X_test):
        return super().predict(X_test)

    def score(self, X_test, y_test):
        return super().score(X_test,y_test)


    def prepareData(self, cross_val = True):
        data = 'database/*[0123456789].binetflow'
        # data = './DETECTION SYSTEM/database/*[0123456789].binetflow'
        scalers = {'minmax'}  # {'standard', 'minmax', 'robust', 'max-abs'}
        samplers = ['no_balanced']  # 'under_sampling', 'over_sampling', 'smote', 'svm-smote' 'adasyn'
        pre.preprocessing(data, scalers, samplers) #carga y preprocesamiento de los datos
        train_data, train_labels = utils.load_and_divide(self.escenario_noBalanced) #carga de datos preprocesados
        train=[]
        test=[]
        if not cross_val:
            X_train, X_test, y_train, y_test = utils.train_test_split(train_data, train_labels, test_size=self.test_size)# Separar los datos del entrenamiento
            train.append([X_train,y_train])
            test.append([X_test,y_test])
        else:
            train, test = utils.create_k(train_data, train_labels,self.k)# conjuntos de entrenamiento prueba de validacion cruzada
        return train, test
        
