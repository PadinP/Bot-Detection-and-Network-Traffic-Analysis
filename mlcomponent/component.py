import pickle as pck
import random as ram
from metric_extractor.metrics import Metric
from files.db_handler import save_data_characterization
from enfoqueMedia.pruebaEnf25 import *
from enfoqueMedia.pruebaEnf50 import *
from enfoqueMedia.pruebaEnf100 import *
from enfoqueMedia.pruebaEnf_200 import *
from enfoqueMedia.pruebaEnf_300 import *
from app.config.logger_config import detection_logger 

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

    def validate(self, tipe):
        if tipe == 2:
            if len(self.x_positives) == 0:
                detection_logger.info("No human user data exists")
                return False
        if tipe == 3:
            if len(self.metrics_characterization) == 0:
                detection_logger.info("Lista de de metricas de caracterización vacia")
                return False

        return True


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
                detection_logger.info('Etiqueta asignada: bots')
                self.metrics_characterization.append(1)
            else:
                detection_logger.info('Etiqueta asignada: no bots')
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
                detection_logger.info(f'Denominación no reconocida: {denominacion}')
                return False

        return resultado

    def save_data_charac(
            self):  # metodo para salvar la caracterizacion del cojunto de datos en la base de hechos
        if self.validate(3):
            save_data_characterization(self.metrics_characterization)

    def calculate_metrics(self):  # se claculan las metricas
        if self.validate(2):
            self.metrics_characterization = Metric(self.x_positives, self.expVariance).run_metrics()

    def run_charact(self):
        if len(self.x_positives) == 0:
            detection_logger.info("The users array is empty")
        else:
            detection_logger.info('Calculando métricas\n')
            self.calculate_metrics()  # Se recalculan las métricas usando self.x_positives y self.expVariance.
            detection_logger.info('Corriendo el enfoque para asignar la etiqueta\n')
            self.set_characterization_label()  # Se asigna la etiqueta (bots o no bots) según la lógica interna.
            detection_logger.info('Añadiendo fila a la base de hechos\n')
            self.save_data_charac()  # Se guarda la caracterización en la base de hechos.
