# flujo_filter_context.py
class FlujoFilterContext:
    def __init__(self, strategy):
        self._strategy = strategy

    def set_strategy(self, strategy):
        self._strategy = strategy

    def filtrar_flujos(self, input_file: str, output_file: str) -> None:
        """
        Ejecuta el filtrado utilizando la estrategia configurada.
        """
        self._strategy.filtrar(input_file, output_file)
