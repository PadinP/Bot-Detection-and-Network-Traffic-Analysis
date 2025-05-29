import pickle as pck
import random as ram
import os
import logging
from modulo.metric_extractor.metrics import Metric
from modulo.files.db_handler import save_data_characterization
from modulo.enfoqueMedia.pruebaEnf25 import *
from modulo.enfoqueMedia.pruebaEnf50 import *
from modulo.enfoqueMedia.pruebaEnf100 import *
from modulo.enfoqueMedia.pruebaEnf_200 import *
from modulo.enfoqueMedia.pruebaEnf_300 import *


class Component:
    # Nota del meta-componente.
    # Como nosotros no desplegamos este metacomponente es como un campo de pruebas,
    # donde se simula un cambio en las caracteristicas de los usuarios
    # Ademas se obtiene el subconjunto de datos clasificados como humanos de los datos clasificados en la etapa 2
    # mas detalles en la tesis de Dany epigrafe 2.3.5 y en las practicas 2 de Adrian y yo epigrafe 2.1 y 2.6
    # se eliminaron los primeros pasos de guardar los datos en el archivo "file_clasf_pf_bueno.pckl" e inmediatamente cargar el archivo de nuevo porque ya no hace falta

    def __init__(self, expVariance):
        self.x_positives = []
        self.expVariance = expVariance
        self.metrics_characterization = []
        self.file_human = "modulo/exclusiones/no_bots.csv"
        self.file_bot = "modulo/exclusiones/bots.csv"
        self.headers = "StartTime,DstAddr\n"
        

    def validate(self, tipe, x_new=[], y_new=[]):
        if tipe == 1:
            if len(y_new) == 0 or len(x_new) == 0:
                print("New data array is empty")
                return False
        if tipe == 2:
            if len(self.x_positives) == 0:
                print("No human user data exists")
                return False
        if tipe == 3:
            if len(self.metrics_characterization) == 0:
                print("Lista de de metricas de caracterización vacia")
                return False

        return True

    def show(self, lista):
        uniq, count = np.unique(lista, return_counts=True)
        try:
            print("Number of human users in reclassification:", count[0])
        except:
            print("Number of human users in reclassification:", 0)
        try:
            print("Number of bots users in reclassification:", count[1])
        except:
            print("Number of bots users in reclassification:", 0)

    def simulate_positives(self, x, porcent_cant_min):
        """
        Altera los datos clasificados como humanos dentro de un rango especificado sin introducir aleatoriedad.

        Args:
            x: Matriz de datos a alterar.
            porcent_cant_min: Porcentaje mínimo de datos a alterar.

        Returns:
            Matriz de datos alterada.
        """

        # Calcular el número de datos a alterar
        cant = len(x)
        cant_atributes = x.shape[1]
        cant_modif = int(porcent_cant_min * cant)
        print("Cantidad de instancias modificadas", cant_modif)

        # Obtener el rango de valores para la alteración
        max_value = np.max(self.x_positives)
        min_value = np.min(self.x_positives)
        range_value = max_value - min_value

        # Alterar los datos
        for index in range(cant_modif):
            # Seleccionar una columna y calcular el nuevo valor basado en el índice
            colum = index % cant_atributes
            new_value = min_value + (index / cant_modif) * range_value

            # Alterar el valor en la matriz de datos
            x[index][colum] = new_value

        return x

    def save_data(self, file_path, start_time, dst_addr):
        try:
            # Si el archivo no existe, crearlo primero
            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Crear directorios si no existen
                open(file_path, "w").close()  # Crear el archivo vacío

            # Abrir el archivo en modo agregar ('a')
            with open(file_path, "a") as f:
                # Solo escribir el encabezado si el archivo está vacío
                if os.stat(file_path).st_size == 0:
                    f.write(self.headers + "\n")

                # Escribir los datos
                f.write(f"{start_time},{dst_addr}\n")
        except Exception as e:
            logging.error(f"Error writing to file: {str(e)}")


    def set_positives(self, x_clasf, y_clasf, start_dst):
        print('Eliminando instancias de bots de los datos de entrada...')
        print(f'Total de datos: {len(x_clasf)}')

        for i, j, (start_time, dst_addr) in zip(x_clasf, y_clasf, start_dst):
            if j == 0:  # Filtrar datos de humanos
                self.x_positives.append(i)
                self.save_data(self.file_human, start_time, dst_addr)
            elif j == 1:  # Filtrar datos de bots
                self.save_data(self.file_bot, start_time, dst_addr)

        print('Instancias de bots eliminadas y datos almacenados correctamente')
        self.x_positives = np.array(self.x_positives) 
        # self.x_positives = self.simulate_positives(np.array(self.x_positives), 0.4) #simular cambio de comportamiento

    def set_characterization_label(self):
        """Método para asignar la etiqueta basado en el menor resto, dividiendo en sublotes
        y añadiendo el resto al último sublote"""

        if self.validate(3):
            denominaciones = [25000, 50000, 100000, 200000, 300000]
            num_instancias = len(self.x_positives)

            # 1. Encontrar la denominación con menor resto
            mejor_denominacion = None
            menor_resto = float('inf')

            for denom in denominaciones:
                if denom > num_instancias:
                    continue  # No considerar denominaciones mayores que el número de instancias

                resto = num_instancias % denom
                if resto < menor_resto:
                    menor_resto = resto
                    mejor_denominacion = denom
                # En caso de empate, preferir la denominación mayor
                elif resto == menor_resto and denom > mejor_denominacion:
                    mejor_denominacion = denom

            # Si todas las denominaciones son mayores que el número de instancias
            if mejor_denominacion is None:
                mejor_denominacion = min(denominaciones)
                menor_resto = num_instancias

            # 2. Calcular número de sublotes
            num_sublotes = num_instancias // mejor_denominacion
            resto_final = num_instancias % mejor_denominacion

            resultados = []

            # 3. Procesar los sublotes
            for i in range(num_sublotes):
                inicio = i * mejor_denominacion
                # Para el último sublote, añadir el resto
                if i == num_sublotes - 1 and resto_final > 0:
                    fin = inicio + mejor_denominacion + resto_final
                else:
                    fin = inicio + mejor_denominacion

                sublote = self.x_positives[inicio:fin]

                # Llamar al método correspondiente a la denominación base
                resultado_sublote = self.procesar_lote(mejor_denominacion, sublote)
                resultados.append(resultado_sublote)

            # 4. Determinar el resultado final
            # Si al menos un sublote es detectado como bots, se considera bots
            if any(resultados):
                print('Etiqueta asignada: bots')
                self.metrics_characterization.append(1)
            else:
                print('Etiqueta asignada: no bots')
                self.metrics_characterization.append(0)

    def procesar_lote(self, denominacion, datos):
        """Método auxiliar para llamar a la función de prueba correspondiente"""
        resultado = None

        match denominacion:
            case 25000:
                resultado = pruebaEnfoque_i25_tp20(datos)
            case 50000:
                resultado = pruebaEnfoque_i50_tp20(datos)
            case 100000:
                resultado = pruebaEnfoque_i100_tp25(datos)
            case 200000:
                resultado = pruebaEnfoque_i200_tp5(datos)
            case 300000:
                resultado = pruebaEnfoque_i300_tp25(datos)
            case _:
                print(f'Denominación no reconocida: {denominacion}')
                return False

        return resultado

    def save_data_charac(
            self):  # metodo para salvar la caracterizacion del cojunto de datos en la base de hechos
        if self.validate(3):
            save_data_characterization(self.metrics_characterization)

    def calculate_metrics(self):  # se claculan las metricas
        if self.validate(2):
            self.metrics_characterization = Metric(self.x_positives, self.expVariance).run_metrics()

    def run_charact(self, x_clasf, y_clasf,dst_addr):
        if len(x_clasf) == 0 or len(y_clasf) == 0:
            print("The users array is empty")
        else:
            print('Inicializando meta-componente\n')
            self.set_positives(x_clasf, y_clasf,dst_addr)  # De todos los datos que entraron nos quedamos con los humanos y después se simula un cambio
            print('Calculando metricas\n')
            self.calculate_metrics()  # se recalculan las metricas para describir el conjunto de datos despues del cambio de comportamiento
            print('Corriendo el enfoque para asignar la etiqueta\n')
            self.set_characterization_label()  # Se le asigna la etiqueta al conjunto de datos usando el enfoque de entropia
            print('Anadiendo fila a la base de hecho\n')
            self.save_data_charac()  # se guarda la nueva fila en la base de hechos
