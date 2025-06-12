import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler, RobustScaler
from imblearn.over_sampling import RandomOverSampler, SMOTE, SVMSMOTE, ADASYN
from imblearn.under_sampling import RandomUnderSampler
from datetime import datetime
from sklearn.decomposition import PCA as pca
import pandas as pd
from datetime import datetime
import preprocessdata.dictionaries as dic
from app.config.logger_config import detection_logger 

def normalize_bitnetflow(file_path):
    df = pd.read_csv(file_path)

    # Normalizar formatos de fecha y hora
    df["StartTime"] = pd.to_datetime(df["StartTime"], format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")
    df["StartTime"] = df["StartTime"].fillna(pd.to_datetime(df["StartTime"], format="%Y/%m/%d %H:%M:%S.%f", errors="coerce"))
    df["StartTime"] = df["StartTime"].dt.strftime("%Y/%m/%d %H:%M:%S.%f")

    # Convertir el Protocolo a minúsculas
    df["Proto"] = df["Proto"].str.lower()

    # Manejar valores NA en los puertos y convertirlos a enteros
    df["Sport"] = df["Sport"].fillna(0).astype(int)
    df["Dport"] = df["Dport"].fillna(0).astype(int)

    # Asegurar que sTos y dTos sean consistentes
    df["sTos"] = df["sTos"].astype(str).replace("0", "0.0")
    df["dTos"] = df["dTos"].astype(str).replace("0", "0.0")

    # Guardar el archivo normalizado en formato binetflow, sobrescribiéndolo
    with open(file_path, "w") as f:
        headers = "StartTime,Dur,Proto,SrcAddr,Sport,Dir,DstAddr,Dport,State,sTos,dTos,TotPkts,TotBytes,SrcBytes,Label\n"
        f.write(headers)

        for _, row in df.iterrows():
            line = f"{row['StartTime']},{row['Dur']},{row['Proto']},{row['SrcAddr']},{row['Sport']},{row['Dir']}," \
                   f"{row['DstAddr']},{row['Dport']},{row['State']},{row['sTos']},{row['dTos']},{row['TotPkts']}," \
                   f"{row['TotBytes']},{row['SrcBytes']},{row['Label']}\n"
            f.write(line)

    detection_logger.info(f"Archivo binetflow normalizado modificado exitosamente en: {file_path}")


def convert_proto_and_state_atributes(dataframe, label):
    proto_list = dataframe['proto'].unique()
    state_list = dataframe['state'].unique()
    dictionaries = dic.select_dictionaries['0']
    for proto in proto_list:
        if proto != 0:
            try:
                dataframe['proto'].replace(proto, dictionaries[0][proto], inplace=True)
            except:
                if proto == 'ICMPV6':
                    dataframe['proto'].replace(proto, dictionaries[0]['ipv6-icmp'], inplace=True)
                else:
                    dataframe['proto'].replace(proto, dictionaries[0][proto.lower()], inplace=True)

    for state in state_list:
        if state != 0:
            dataframe['state'].replace(state, dictionaries[1][state], inplace=True)


# Function to convert Dir to integers
def conv_dir(key):
    return dic.dirDict[key]


def conv_label(value):
    if 'Botnet' in value:
        return 1
    elif 'Normal' in value:
        return 0
    elif 'Background' in value:
        return 0


def get_hour(startTime):
    dt = datetime.strptime(startTime, "%Y/%m/%d %H:%M:%S.%f")
    return int(dt.hour)


def conv_port(portString):
    if portString != '':
        try:
            return int(portString)
        except:
            # Hexadecimal convert
            return int(portString, 16)


class data_cleaning:
    def __init__(self, escenario, sep, label_scenarios):
        """
        :param escenario: correponde al path del archivo de datos en formato .csv.
        :param sep: caracter utilizado como separador de los atributos en archvo .csv.
        """
        self.escenario = escenario
        self.sep = sep
        self.label_scenarios = label_scenarios
        # Diccionario con las funciones de conversion de los atributos
        self.converters = {
            'sthour': get_hour,
            'label': conv_label,
            'dport': conv_port,
            'sport': conv_port,
            'dir': conv_dir
        }

    def loaddata(self):
        names = ['sthour', 'dur', 'proto', 'sip', 'sport', 'dir', 'dip', 'dport', 'state', 'stos', 'dtos', 'tpkts',
                 'tbytes', 'sbytes', 'label']

        # Cargar el archivo de datos, ignorando los nombre de las columnas, renombrando las columnas
        df = pd.read_csv(filepath_or_buffer=self.escenario, sep=self.sep, names=names, skiprows=1,
                         converters=self.converters
                         )

        # Tratamento de los valores NaN
        df = df.fillna(0)
        # Convierte los atributos proto y state
        convert_proto_and_state_atributes(df, self.label_scenarios)
        # Eliminar los atributos de dirección ip fuente y destino
        df = df.drop(columns=['sip', 'dip'])
        # Actualizar los índices de las líneas
        df = df.reset_index(drop=True)

        # Separar la varialble dependiente
        independent_variables = ['sthour', 'dur', 'proto', 'sport', 'dir', 'dport', 'state', 'stos', 'dtos', 'tpkts',
                                 'tbytes', 'sbytes']

        dependent_variables = 'label'
        X = df[independent_variables]
        y = df[dependent_variables]

        return np.array(X), np.array(y)


class data_transform:
    def __init__(self, scaler, data):
        """
        :param scaler: tipo de escalado.
        :param data: conjunto de las variables indepedientes.
        """
        self.scaler = scaler
        self.X = data

    def selection(self):
        scalerDict = {'standard': StandardScaler(with_mean=True, with_std=True),
                      'minmax': MinMaxScaler(),
                      'robust': RobustScaler(),
                      'max-abs': MaxAbsScaler()
                      }

        scaler_model = scalerDict[self.scaler].fit(self.X)
        train_data = scaler_model.transform(self.X)

        # Aplicar PCA a los datos para reducir su dimensionalidad considerando 98% de variaza explicativa acumulada
        pca_model = pca(n_components=7)
        results = pca_model.fit_transform(train_data)
        detection_logger.info(f'Varianza explicada: {pca_model.explained_variance_ratio_}')

        return results, scaler_model, pca_model #return np.array(results['PC']), scaler_model, pca_model


class class_balance:
    def __init__(self, sampler, data_x, data_y):
        """
        :param sampler: String con el nombre del muestreo seleccionado.
        :param data_x: conjunto de las variables independientes.
        :param data_y: etiquetas de clase.
        """
        self.sampler = sampler
        self.X = data_x
        self.y = data_y

    def sampling(self):
        sampling_method = {'under_sampling': RandomUnderSampler(),
                           'over_sampling': RandomOverSampler(),
                           'smote': SMOTE(k_neighbors=10, random_state=2022),
                           'svm-smote': SVMSMOTE(),
                           'adasyn': ADASYN()
                           }
        X_balanced, y_balanced = sampling_method[self.sampler].fit_resample(self.X, self.y)

        return X_balanced, y_balanced
