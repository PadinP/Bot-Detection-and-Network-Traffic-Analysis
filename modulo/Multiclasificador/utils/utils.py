import errno
import os
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from deslib.util.diversity import double_fault, disagreement_measure, correlation_coefficient, Q_statistic
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from modulo.Multiclasificador.utils.metrics import Metric

# Inicializar clasificadores individuales
estimators = {
    'LR': LogisticRegression(max_iter=1500),
    'CART': DecisionTreeClassifier(),
    'NAIVE': GaussianNB(),
    'KNN': KNeighborsClassifier(),
    'SGD': SGDClassifier(loss='log_loss', max_iter=1000),  # Actualiza la función de pérdida a 'log'
    'SVC': SVC(max_iter=15000, probability=True),
    'MLP': MLPClassifier(random_state=0, max_iter=4000),
    'EXTRA': ExtraTreeClassifier()
}


metricas = {
    'Accuracy': accuracy_score,
    'Precision': precision_score,
    'Recall': recall_score,
    'F1': f1_score,
    'AUC': roc_auc_score
}


def create_txt_report(dataframe, subsets, file):
    file.write(str(dataframe))
    file.write('\n')
    file.write('\n')
    for i, j in enumerate(subsets):
        number = 1 + i
        file.write('Vot-' + str(number) + ' -----> ' + str(j) + '\n')


def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def extract_pickle_file(file_path):
    with (open(file_path, 'rb')) as f:
        while True:
            try:
                reading = pickle.load(f)
            except EOFError:
                break

    return reading[0], reading[1]


def plot_results(data, name_graph, title, x_label, y_label):
    plt.rcParams.update({'font.size': 13})
    print(data) # Añade esta línea para imprimir los datos
    data.plot(kind='bar', rot=30, width=0.8, figsize=[8, 6])
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.legend(title='Métricas', bbox_to_anchor=(1, 1), loc=2, borderaxespad=1)
    plt.savefig(name_graph, bbox_inches='tight')
    plt.show()


def create_list_tuple(clfs_list, dictionary):
    out_list = []
    for i in clfs_list:
        new_l = []
        converted_list = eval(i)
        for value in converted_list:
            tupl = (value, dictionary[value])
            new_l.append(tupl)
        out_list.append(new_l)
    return out_list


def selected_conbination(i, results, file):
    file.write(str(i)
               + ';' + str(results[0])
               + ';' + str(results[1])
               + ';' + str(results[2])
               + ';' + str(results[3])
               + '\n'
               )


def loadData(database_path):
    names = ['cusum', 'nCusum', 'ShannonEntropy', 'jensen-shannon', 'mahalanobis', 'iqr', 'mad', 'label']
    try:
        df = pd.read_csv(database_path, sep=',', names=names, engine='python', on_bad_lines='skip')
        # df['c2'].replace([np.inf, -np.inf], 0, inplace=True)
        df = df.dropna()  # Elimina filas con datos faltantes
        return np.array(df)
    except pd.errors.ParserError as e:
        print(f"Error al analizar el archivo CSV: {e}")
        return None


def sored_data_with_label(id_subset, length, metrics, label, file):
    file.write(str(id_subset) + ';' + str(length)
               + ';' + str(metrics[0])
               + ';' + str(metrics[1])
               + ';' + str(metrics[2])
               + ';' + str(metrics[3])
               + ';' + str(metrics[4])
               + ';' + str(metrics[5])
               + ';' + str(metrics[6])
               + ';' + str(metrics[7])
               + ';' + str(metrics[8])
               + ';' + str(metrics[9])
               + ';' + str(metrics[10])
               + ';' + str(metrics[11])
               + ';' + str(metrics[12])
               + ';' + str(metrics[13])
               + ';' + str(metrics[14])
               + ';' + str(metrics[15])
               + ';' + str(metrics[16])
               + ';' + str(label)
               + '\n'
               )
    
# def write_data(id_subset, length, metrics,file):
#     file.write(str(id_subset) + ';' + str(length)
#                + ';' + str(metrics[0])
#                + ';' + str(metrics[1])
#                + ';' + str(metrics[2])
#                + ';' + str(metrics[3])
#                + ';' + str(metrics[4])
#                + ';' + str(metrics[5])
#                + ';' + str(metrics[6])
#                + ';' + str(metrics[7])
#                + ';' + str(metrics[8])
#                + ';' + str(metrics[9])
#                + ';' + str(metrics[10])
#                + ';' + str(metrics[11])
#                + ';' + str(metrics[12])
#                + ';' + str(metrics[13])
#                + ';' + str(metrics[14])
#                + ';' + str(metrics[15])
#                + ';' + str(metrics[16])
#                + '\n'
#                )


def sored_data_with_label_1(length, metrics, file,label):
    file.write(str(length)
               + ';' + str(metrics[0])
               + ';' + str(metrics[1])
               + ';' + str(metrics[2])
               + ';' + str(metrics[3])
               + ';' + str(metrics[4])
               + ';' + str(metrics[5])
               + ';' + str(metrics[6])
               + ';' + str(metrics[7])
               + ';' + str(metrics[8])
               + ';' + str(metrics[9])
               + ';' + str(metrics[10])
               + ';' + str(metrics[11])
               + ';' + str(metrics[12])
               + ';' + str(metrics[13])
               + ';' + str(metrics[14])
               + ';' + str(metrics[15])
               + ';' + str(metrics[16])
               + ';' + str(label)
               + '\n'
               )



def data_labeling(data, y, file_pf):
    file = open(file_pf, "ab+")
    file.seek(0)
    train_data = np.array(pickle.load(file))

    train_columns = train_data.shape[1]
    x_train_data = train_data[:, :train_columns - 1]
    y_train_data = train_data[:, -1]

    # y_labelled = y_instances
    model = estimators['CART']
    model.fit(x_train_data, y_train_data)
    y_labelled = model.predict(data)

    return data, y, y_labelled


def data_set_metrics(x_instances, label, value):
    X_subset, x_b, y_subset, y_b = train_test_split(x_instances, label, train_size=value)

    return Metric(X_subset, y_subset).run_metrics(), y_subset


class DiversityMeasures:
    def __init__(self, y, predictions):
        self.y = y
        self.predictions = predictions

    def get_measures(self):
        n_predictors = self.predictions.shape[1]
        df_total, df_ij, p_total, p_ij, q_total, q_ij, d_total, d_ij = 0, 0, 0, 0, 0, 0, 0, 0

        # Ajustar los nombres de las columnas
        columns = list(range(len(self.predictions.columns)))
        self.predictions.columns = columns

        # Iterar sobre los pares de predictores
        for i in range(0, n_predictors - 1):
            for j in range(i + 1, n_predictors):
                i_pred = self.predictions[i]
                j_pred = self.predictions[j]
                
                # Calcular las métricas de diversidad
                df_ij = double_fault(self.y, i_pred, j_pred)
                p_ij = correlation_coefficient(self.y, i_pred, j_pred)
                
                # Comprobar el denominador antes de llamar a Q_statistic
                try:
                    q_ij = Q_statistic(self.y, i_pred, j_pred)
                except ZeroDivisionError:
                    q_ij = 0  # Valor predeterminado si ocurre división por cero
                
                d_ij = disagreement_measure(self.y, i_pred, j_pred)
                
                # Acumular los resultados
                df_total += df_ij
                p_total += p_ij
                q_total += q_ij
                d_total += d_ij

        # Calcular los promedios finales
        divisor = n_predictors * (n_predictors - 1)
        df = round(2 * df_total / divisor, 2)
        p = round(2 * p_total / divisor, 2)
        q = round(2 * q_total / divisor, 2)
        d = round(2 * d_total / divisor, 2)

        return df, p, q, d



def merge_scenarios(escenario1, escenario2):
    X1, y1 = extract_pickle_file(escenario1)
    X2, y2 = extract_pickle_file(escenario2)

    X1_test, y1_test, X2_test, y2_test = X1, y1, X2, y2  # para particionar los datos en el futuro

    X_test = np.concatenate((X1, X2), axis=0)
    y_test = np.concatenate((y1_test, y2_test))

    return X_test, y_test
