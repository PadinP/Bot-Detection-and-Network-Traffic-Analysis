import numpy as np
from scipy.stats import entropy
from scipy.stats import iqr
from scipy.spatial.distance import jensenshannon
from scipy.spatial import distance
from numpy.linalg import inv
import pickle as pck


def managed_load(since=0, untilBot=5000, untilHuman=5000, e='0', smote=False):
    if smote:
        file = open("database-preprosesing/smote/" + e + "/minmax/" + e + ".minmax_smote.pickle", "ab+")
    else:
        file = open("database-preprosesing/no_balanced/" + e + "/minmax/" + e + ".minmax.pickle", "ab+")

    file.seek(0)
    inst = pck.load(file)

    x_arr = []
    y_arr = []

    count1 = 0
    count2 = 0

    skip = 0

    for x_ins, y_ins in zip(inst[0], inst[1]):
        if since > skip:
            skip += 1
            continue
        if count1 < untilHuman and y_ins == 0:
            x_arr.append(x_ins)
            y_arr.append(y_ins)
            count1 += 1
        elif count2 < untilBot and y_ins == 1:
            x_arr.append(x_ins)
            y_arr.append(y_ins)
            count2 += 1

    x_arr = np.array(x_arr)
    y_arr = np.array(y_arr)
    file.close()

    return x_arr, y_arr


def media_pond(nEnt, expVariance):
    return np.sum(nEnt * expVariance) / np.sum(expVariance)


class Metric:
    def __init__(self, x_instances, expV):
        self.data = x_instances
        self.normalData, _ = managed_load(since=0, untilBot=0, untilHuman=len(self.data), e='0')
        self.expVariance = expV
        self.cusum = None
        self.nCusum = None
        self.entropy = None
        self.js = None
        self.mahalanobis = None
        self.iqr = None
        self.mad = None

    def calc_shannon(self):
        # print('Calculating Shannon Entropy...\n')
        entropyArray = []
        for i in range(self.data.shape[1]):
            column = self.data[:, i]
            # intervs = bins_freedman_diaconis(column)
            # bins = np.linspace(min(column), max(column), intervs)
            histogram, bin_edges = np.histogram(column, bins='doane')
            probabilities = histogram / np.sum(histogram)

            entropyArray.append(entropy(probabilities, base=2))

        # print('\nCalculating weighted mean...')
        self.entropy = media_pond(np.array(entropyArray), self.expVariance)

    def ts_CUSUM(self):
        # print('Calculating CUSUM...\n')
        cusumArray = []
        nCusumArray = []

        for i in range(self.data.shape[1]):
            cusum = 0
            nCusum = 0
            column = self.data[:, i]
            normalColumn = self.normalData[:, i]
            mean = np.mean(normalColumn)
            # #print(f"Mean of the column {i} = {mean}")

            # Calcular CUSUM
            for j in range(len(column)):
                cusum = max(0, cusum + column[j] - mean)
                nCusum = min(0, nCusum + column[j] - mean)
            # Anadir al arry una vez terminado el calculo
            cusumArray.append(cusum)
            nCusumArray.append(nCusum)

        # print(f"Final CUSUM: {cusumArray}")
        # print(f"Final N_CUSUM: {nCusumArray}")

        # print('\nCalculating weighted mean...')
        self.cusum = media_pond(np.array(cusumArray), self.expVariance)
        self.nCusum = media_pond(np.array(nCusumArray), self.expVariance)

    def J_Distance(self):
        # print('Calculating Jensen-Shannon Distance...\n')
        distArray = []
        for i in range(self.data.shape[1]):
            column = self.data[:, i]
            normalColumn = self.normalData[:, i]

            histogram, bin_edges = np.histogram(column, bins='doane')
            intervs1 = len(bin_edges) - 1
            histogram, bin_edges = np.histogram(normalColumn, bins='doane')
            intervs2 = len(bin_edges) - 1
            intervs = int((intervs1 + intervs2) / 2)
            #  #print(intervs1)
            #  #print(intervs2)

            # Distribucion p de datos recogidos
            bins = np.linspace(min(column), max(column), intervs)
            histogram, bin_edges = np.histogram(column, bins=bins)
            P = histogram / np.sum(histogram)
            #  #print('Probabilidades: ', P)

            # Distibucion q de datos "normales"
            bins = np.linspace(min(normalColumn), max(normalColumn), intervs)
            histogram, bin_edges = np.histogram(normalColumn, bins=bins)
            Q = histogram / np.sum(histogram)
            #  #print('Probabilidades normales: ', Q)

            # Calcular Distancia de Jensen–Shannon
            js = jensenshannon(P, Q)
            distArray.append(js)
        # #print(f"Jensen-Shannon: {js}")

        # print('\nCalculating weighted mean...')
        self.js = media_pond(np.array(distArray), self.expVariance)

    def mahala(self):
        # print('Calculating Mahalanobis Distance...\n')
        # vector de medias y matriz de covarianza de los datos de referencia
        mean = np.mean(self.normalData, axis=0)
        # Calcular la matriz de covarianza y la inversa
        cov = np.cov(self.normalData, rowvar=False)
        inv_cov = inv(cov)

        # Para cada fila.
        dList = []
        for i in range(self.data.shape[0]):
            # Calcular la distancia de Mahalanobis entre la fila y la media
            d = distance.mahalanobis(self.data[i], mean, inv_cov)
            dList.append(d)
        #  #print(f"La distancia de Mahalanobis para la observación {i} es {d}")

        ret = np.array(dList)

        #  #print('Calculating Median, Max and Min')
        # #print('Calculating Mean')
        # finalMedian = np.median(ret)
        # maxVal = np.max(ret)
        # minVal = np.min(ret)
        testMean = np.mean(ret)
        #  #print(f'La mediana de todas las distancias es {finalMedian}')
        #  #print(f'El valor maximo es: {maxVal}')
        #  #print(f'El valor minimo es: {minVal}')
        # print(f'La media es: {testMean}')
        return testMean

    def calc_IQR(self):
        # print('Calculating IQR...')
        iqr_value = iqr(self.data[:, 0])
        return iqr_value

    def MAD(self):
        # print('Calculating MAD...')
        media = np.mean(self.data[:, 0])
        desviaciones_absolutas = np.abs(self.data[:, 0] - media)
        mad = np.mean(desviaciones_absolutas)
        return mad

    def run_metrics(self):
        if len(self.data) != 0:
            # print('Starting generation...')
            self.ts_CUSUM()
            self.calc_shannon()
            self.J_Distance()
            self.mahala()
            self.calc_IQR()
            self.MAD()

            arr = [self.cusum, self.nCusum, self.entropy, self.js, self.mahalanobis, self.iqr, self.mad]
            print(f'Metrics: {arr}')

            return arr
        else:
            print("No existen datos")
            return []
