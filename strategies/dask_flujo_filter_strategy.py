# strategies/dask_flujo_filter_strategy.py
import dask.dataframe as dd
from strategies.flujo_filter_strategy import FlujoFilterStrategy

class DaskFlujoFilterStrategy(FlujoFilterStrategy):
    def filtrar(self, input_file: str, output_file: str) -> None:
        # Intentamos leer el archivo en formato CSV
        try:
            df = dd.read_csv(input_file, delimiter=',')
        except Exception:
            raise ValueError("Formato de archivo no soportado.")
        
        # Crear máscaras para las condiciones sin columnas intermedias
        mask_src = df['SrcAddr'].map(lambda ip: int(ip.rsplit('.', 1)[1]) <= 3, meta=('mask_src', 'bool'))
        mask_dst = df['DstAddr'].map(lambda ip: int(ip.rsplit('.', 1)[1]) <= 3, meta=('mask_dst', 'bool'))
        
        # Combinamos las condiciones para filtrar
        mask = mask_src & mask_dst

        # Aplicamos el filtro y guardamos el resultado
        df_filtrado = df[mask]
        df_filtrado.to_csv(output_file, index=False, single_file=True)
