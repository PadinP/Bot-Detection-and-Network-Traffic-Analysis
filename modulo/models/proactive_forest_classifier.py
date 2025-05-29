import numpy as np
from sklearn.metrics import accuracy_score
from sklearn import decomposition

from modulo.utils import utils
from modulo.proactive_forest.estimator import DecisionForestClassifier, ProactiveForestClassifier
from modulo.mlcomponent.component import Component as comp
from modulo.preprocessdata import preprocesssing as pre

class PFClassifier(ProactiveForestClassifier):

	
    def __init__(self,escenario = "11", k=5):
        super().__init__(n_estimators = 250,feature_selection = 'log', split_criterion= 'entropy')
        self.escenario = f"modulo/database-preprosesing/smote/" + escenario + "/minmax/" + escenario + ".minmax_smote.pickle"
        self.escenario_noBalanced = f"modulo/database-preprosesing/no_balanced/" + escenario + "/minmax/" + escenario + ".minmax.pickle"
        self.k = k
        self.validate = True

    def fit(self,X_train,y_train):
        return super().fit(X_train,y_train)

    def predict(self,X_test):
        return super().predict(X_test)

    def score(self,X_test,y_test):
        return accuracy_score(y_test, self.predict(X_test))

    """
        Método de preprocesamiento y carga de los datos, la base de datos se encuentra dividida en 13 escenarios 
        lo que hace que sea necesario entrenar y probar el algoritmo con el mismo escenario. En un futuro se establecerá 
        una base de datos centralizada.
        """
    def prepareData(self, cross_val = True):
        data = 'modulo/database/*[0123456789].binetflow'
        scalers = {'minmax'}  # {'standard', 'minmax', 'robust', 'max-abs'}
        samplers = ['smote']  # 'under_sampling', 'over_sampling', 'smote', 'svm-smote' 'adasyn'
        pre.preprocessing(data, scalers, samplers) #carga y preprocesamiento de los datos
        train=[]
        test=[]

        train_data, train_labels = utils.load_and_divide(self.escenario_noBalanced) #carga de datos preprocesados

        try:
            train, test = utils.create_k(train_data, train_labels,self.k)# conjuntos de entrenamiento prueba de validacion cruzada   
        except:
            print("k is not integer")       

        return train, test

   
    
 