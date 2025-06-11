import dask.dataframe as dd
from strategies.flujo_filter_strategy import FlujoFilterStrategy

class DaskFlujoFilterStrategy(FlujoFilterStrategy):
    def _valid_ip(self, ip: str) -> bool:
        """
        Método interno que valida el formato de la IP antes de extraer la última parte.
        Retorna True si el último segmento es <= 3, de lo contrario False.
        """
        parts = ip.rsplit('.', 1)
        if len(parts) > 1:
            try:
                return int(parts[1]) <= 3
            except ValueError:
                return False  # Si la conversión a entero falla, descartamos la IP
        return False  # Si la IP no tiene al menos un punto, la descartamos

    def filtrar(self, input_file: str, output_file: str) -> None:
        try:
            df = dd.read_csv(input_file, delimiter=',')
        except Exception:
            raise ValueError("Formato de archivo no soportado.")
        
        # Aplicamos validación a las columnas IP dentro de la clase
        mask_src = df['SrcAddr'].map(self._valid_ip, meta=('mask_src', 'bool'))
        mask_dst = df['DstAddr'].map(self._valid_ip, meta=('mask_dst', 'bool'))
        
        # Combinamos las condiciones para filtrar
        mask = mask_src & mask_dst
        
        # Aplicamos el filtro y guardamos el resultado en un único archivo CSV
        df_filtrado = df[mask]
        df_filtrado.to_csv(output_file, index=False, single_file=True)
