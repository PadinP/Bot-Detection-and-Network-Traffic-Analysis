from sklearn.ensemble import AdaBoostClassifier
from modulo.utils import utils
from modulo.preprocessdata import preprocesssing as pre


class ABClassifier(AdaBoostClassifier):

    def __init__(self, n_estimators=250, escenario='11', k=5, test_size=0.2):
        super().__init__(n_estimators=n_estimators)
        self.escenario = f"modulo/database-preprosesing/smote/" + escenario + "/minmax/" + escenario + ".minmax_smote.pickle"
        self.escenario_noBalanced = f"modulo/database-preprosesing/no_balanced/" + escenario + "/minmax/" + escenario + ".minmax.pickle"
        self.k = k
        self.test_size = test_size

    def fit(self, X, y, sample_weight=None):
        return super().fit(X, y)

    def predict(self, X):
        return super().predict(X)

    def score(self, X, y, sample_weight=None):
        return super().score(X, y)

    def prepareData(self, cross_val=True):
        data = 'modulo/database/*[0123456789].binetflow'
        # {'standard', 'minmax', 'robust', 'max-abs'}
        scalers = {'minmax'}
        # 'under_sampling', 'over_sampling', 'smote', 'svm-smote' 'adasyn' 'no_balanced'
        samplers = ['smote']
        pre.preprocessing(data, scalers, samplers)
        train_data, train_labels = utils.load_and_divide(self.escenario)
        train = []
        test = []
        if not cross_val:
            X_train, X_test, y_train, y_test = utils.train_test_split(train_data, train_labels,
                                                                      test_size=self.test_size)
            train.append([X_train, y_train])
            test.append([X_test, y_test])
        else:
            train, test = utils.create_k(train_data, train_labels, self.k)
        return train, test
