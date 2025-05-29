import numpy as np
from scipy.stats import entropy
from scipy.stats import iqr
from scipy.spatial.distance import jensenshannon
from scipy.spatial import distance
from numpy.linalg import inv
import pickle as pck
import matplotlib.pyplot as plt
#import pandas as pd


def managed_load(since=0, untilBot=5000, untilHuman=5000, e='3', smote=False):
    if smote:
        file = open("modulo/database-preprosesing/smote/" + e + "/minmax/" + e + ".minmax_smote.pickle", "ab+")
    else:
        file = open("modulo/database-preprosesing/no_balanced/" + e + "/minmax/" + e + ".minmax.pickle", "ab+")

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


"""
Devuelve dos arreglos con 10 matrices numpy cada uno y cada matriz numpy con 1000000 instancias de datos 
"""
def getData():
    data3, label3 = managed_load(0, 40000, 950000, '9') #myLoad(0, 100000, e='3')
    data11, label11 = managed_load(0, 50000, 950000, '10') #myLoad(0, 50000, e='11')

    data3 = np.array_split(data3, 10)
    data11 = np.array_split(data11, 10)

    return data3, data11


def media_pond(nEnt, e='3'):
    dict_expVariance = {
        '0': np.array([0.49616096, 0.30754947, 0.11054761, 0.0765011, 0.00516748, 0.00265275, 0.00074099]),
        '1': np.array([0.35666183, 0.33186138, 0.23084867, 0.0689442, 0.00690669, 0.00388782, 0.00045744]),
        '2': np.array([0.39070403, 0.29763827, 0.19412535, 0.10445739, 0.0074889, 0.00468122, 0.00054815]),
        '3': np.array([0.37962076, 0.36040663, 0.13714998, 0.10509267, 0.00888123, 0.00591864, 0.00265547]),
        '4': np.array([0.43464399, 0.2596431, 0.17971887, 0.10614641, 0.01268697, 0.00538046, 0.00101864]),
        '5': np.array([0.5517209, 0.23879579, 0.09471701, 0.06118631, 0.04742159, 0.00298028, 0.00211656]),
        '6': np.array([0.39295522, 0.35146312, 0.1546751, 0.08739967, 0.00727655, 0.00451535, 0.00086129]),
        '7': np.array([0.53977881, 0.23428666, 0.09880852, 0.06035776, 0.05697433, 0.00638463, 0.0021552]),
        '8': np.array([0.35318432, 0.31048351, 0.17486612, 0.08469572, 0.06839798, 0.00421982, 0.00255682]),
        '9': np.array([0.43446992, 0.27494765, 0.19693704, 0.08609938, 0.00384923, 0.00260077, 0.00060566]),
        '10': np.array([0.38205831, 0.22908203, 0.18580794, 0.13168935, 0.06450667, 0.00557837, 0.00078845]),
        '11': np.array([0.44148548, 0.22797933, 0.14130709, 0.11591418, 0.06185796, 0.00963631, 0.00076141]),
        '12': np.array([0.52930001, 0.2322891, 0.09531061, 0.0703681, 0.06227798, 0.00747323, 0.00216146]),
        '13': np.array([0.36643762, 0.31170778, 0.17185557, 0.0814886, 0.0614083, 0.00353696, 0.00192767])}

    return np.sum(nEnt * dict_expVariance[e]) / np.sum(dict_expVariance[e])


def calc_shannon(data, e):
    print('Calculating Shannon Entropy...\n')
    entropyArray = []
    for i in range(data.shape[1]):
        column = data[:, i]
        # intervs = bins_freedman_diaconis(column)
        # bins = np.linspace(min(column), max(column), intervs)
        histogram, bin_edges = np.histogram(column, bins='doane')
        probabilities = histogram / np.sum(histogram)

        entropyArray.append(entropy(probabilities, base=2))

    print('\nCalculating weighted mean...')
    return media_pond(np.array(entropyArray), e)


"""
    - data es donde estan guardados los datos de las instancias despues del pca
    Los trabajamos por columnas y despues generalizamos los resultados
    - mean es la media de los datos de referencia
    - e representa el escenario
    - threshold y nThreshold son los umbrales positivos y negativos respectivamente, son necesarios si se quiere detectar anomalias
"""
def ts_CUSUM(data, normalData, e):
    print('Calculating CUSUM...\n')
    cusumArray = []
    nCusumArray = []

    for i in range(data.shape[1]):
        cusum = 0
        nCusum = 0
        column = data[:, i]
        normalColumn = normalData[:, i]
        mean = np.mean(normalColumn)
        print(f"Mean of the column {i} = {mean}")

        # Calcular CUSUM
        for j in range(len(column)):
            cusum = max(0, cusum + column[j] - mean)
            nCusum = min(0, nCusum + column[j] - mean)
        # Anadir al arry una vez terminado el calculo
        cusumArray.append(cusum)
        nCusumArray.append(nCusum)

    print(f"Final CUSUM: {cusumArray}")
    print(f"Final N_CUSUM: {nCusumArray}")

    print('\nCalculating weighted mean...')
    return media_pond(np.array(cusumArray), e), media_pond(np.array(nCusumArray), e)


def J_Distance(data, dataNormal, e='3'):
    print('Calculating Jensen-Shannon Distance...\n')
    distArray = []
    for i in range(data.shape[1]):
        column = data[:, i]
        normalColumn = dataNormal[:, i]

        histogram, bin_edges = np.histogram(column, bins='doane')
        intervs1 = len(bin_edges) - 1
        histogram, bin_edges = np.histogram(normalColumn, bins='doane')
        intervs2 = len(bin_edges) - 1
        intervs = int((intervs1 + intervs2)/2)
        # print(intervs1)
        # print(intervs2)

        # Distribucion p de datos recogidos
        bins = np.linspace(min(column), max(column), intervs)
        histogram, bin_edges = np.histogram(column, bins=bins)
        P = histogram / np.sum(histogram)
        # print('Probabilidades: ', P)

        # Distibucion q de datos "normales"
        bins = np.linspace(min(normalColumn), max(normalColumn), intervs)
        histogram, bin_edges = np.histogram(normalColumn, bins=bins)
        Q = histogram / np.sum(histogram)
        # print('Probabilidades normales: ', Q)

        # Calcular Distancia de Jensen–Shannon
        js = jensenshannon(P, Q)
        distArray.append(js)
        print(f"Jensen-Shannon: {js}")

    print('\nCalculating weighted mean...')
    return media_pond(np.array(distArray), e)


def mahala(data, normalData):
    print('Calculating Mahalanobis Distance...\n')
    # vector de medias y matriz de covarianza de los datos de referencia
    mean = np.mean(normalData, axis=0)
    # Calcular la matriz de covarianza y la inversa
    cov = np.cov(normalData, rowvar=False)
    inv_cov = inv(cov)

    # Para cada fila.
    dList = []
    for i in range(data.shape[0]):
        # Calcular la distancia de Mahalanobis entre la fila y la media
        d = distance.mahalanobis(data[i], mean, inv_cov)
        dList.append(d)
        # print(f"La distancia de Mahalanobis para la observación {i} es {d}")

    ret = np.array(dList)

    # print('Calculating Median, Max and Min')
    print('Calculating Mean')
    # finalMedian = np.median(ret)
    # maxVal = np.max(ret)
    # minVal = np.min(ret)
    testMean = np.mean(ret)
    # print(f'La mediana de todas las distancias es {finalMedian}')
    # print(f'El valor maximo es: {maxVal}')
    # print(f'El valor minimo es: {minVal}')
    print(f'La media es: {testMean}')
    return testMean


'''El Rango Intercuartil (IQR) es una medida de dispersión estadística que indica la diferencia entre el tercer y el 
primer cuartil de un conjunto de datos. Se utiliza para evaluar la variabilidad en la que se encuentra la mayoría de 
los valores. Los valores más grandes indican que la parte central de sus datos se dispersa más. Una de las 
características más ventajosas del rango intercuartil es que es un estadístico robusto, es decir, tiene una alta 
robustez a los valores atípicos. Este estadístico es robusto, lo que significa que es resistente a los valores 
atípicos (outliers). Ya que en el cálculo no se tienen en cuenta los valores extremos, su valor variará muy poco si 
aparecen nuevas observaciones atípicas. Por esta razón, es una forma confiable de medir la dispersión del 50% medio 
de los valores en cualquier distribución. '''
def calc_IQR(data):
    print('Calculating IQR...')
    iqr_value = iqr(data)
    return iqr_value


'''La Media Absoluta de Desviaciones (MAD) es una medida de dispersión estadística que se utiliza para describir la 
variación en un conjunto de datos. Se calcula como el promedio de las diferencias absolutas entre cada valor y la 
media del conjunto de datos.La MAD es útil porque es menos sensible a los valores atípicos en comparación con otras 
medidas de dispersión como la desviación estándar. Esto significa que la MAD puede proporcionar una medida más 
robusta de la dispersión de los datos, especialmente en conjuntos de datos con valores extremos. Cuanto mayor sea el 
valor de la MAD, significa que los datos están más dispersos en relación con la media aritmética. Por el contrario, 
una MAD más pequeña indica que los datos están más concentrados alrededor de la media. '''
def MAD(data):
    print('Calculating MAD...')
    media = np.mean(data)
    desviaciones_absolutas = np.abs(data - media)
    mad = np.mean(desviaciones_absolutas)
    return mad


def IQR_range(data):
    iqr_value = calc_IQR(data)
    lg = np.percentile(data, 25) - 1.5 * iqr_value
    hg = np.percentile(data, 75) + 1.5 * iqr_value

    print(f'Lower gate: {lg}')
    print(f'Higher gate: {hg}')
    print('\n')

    return lg, hg


def calculateAll(data, normaldata, e):

    print('Starting generation...')
    cusum, nCusum = ts_CUSUM(data, normaldata, e)
    print(cusum)
    print(nCusum)
    print('Finishing CUSUM...')
    shannon = calc_shannon(data, e)
    print(shannon)
    print('Finishing Shannon entropy...')
    js = J_Distance(data, normaldata)
    print(js)
    print('Finishing Jensen-Shannon Distance...')
    mahaMean = mahala(data, normaldata)
    print(mahaMean)
    print('Finishing Mahalanobis Distance...')
    iqr_value = calc_IQR(data[:, 0])
    print(iqr_value)
    print('Finishing IQR')
    mad = MAD(data[:, 0])
    print(mad)
    print('Finishing MAD')

    arr = [cusum, nCusum, shannon, js, mahaMean, iqr_value, mad]
    print(f'Metrics: {arr}')

    return arr


if __name__ == '__main__':
    # Prueba de que todo funciona
    data9, data10 = getData()
    normaldata, normalLabel3 = managed_load(since=0, untilBot=0, untilHuman=1000000, e='0')
    for dat in data9:
        calculateAll(dat, normaldata, '9')
        print("----------------Next Iteration----------------------")
    for dat in data10:
        calculateAll(dat, normaldata, '10')
        print("----------------Next Iteration----------------------")
    # testiqr()

    # esto para ver cuantas instancias hay en cada escenario
    # for i in range(13):
    #     data3_10000_2, label = managed_load(0, 9000 * 1000, 9000 * 1000, e=str(i+1))
    #     print(f'escenario {i+1}')
    #     u, c = np.unique(label, return_counts=True)
    #     print(dict(zip(u, c)))
