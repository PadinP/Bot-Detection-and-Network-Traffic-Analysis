import dask.dataframe as dd

def filtrar_flujos_dask(input_file, output_file):
    # Intentamos leer el archivo con distintos formatos
    try:
        df = dd.read_csv(input_file, delimiter=',')  # Si es CSV
    except Exception:
            raise ValueError("Formato de archivo no soportado.")

    # Crear una máscara booleana para cada condición sin agregar columnas intermedias
    mask_src = df['SrcAddr'].map(lambda ip: int(ip.rsplit('.', 1)[1]) <= 3, meta=('mask_src', 'bool'))
    mask_dst = df['DstAddr'].map(lambda ip: int(ip.rsplit('.', 1)[1]) <= 3, meta=('mask_dst', 'bool'))
    
    # Combinar ambas condiciones
    mask = mask_src & mask_dst

    # Filtrar las filas donde la condición se cumpla
    df_filtrado = df[mask]

    # Guardar el resultado con la extensión .binetflow
    df_filtrado.to_csv(output_file, index=False, single_file=True)

