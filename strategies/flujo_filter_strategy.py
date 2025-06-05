# strategies/flujo_filter_strategy.py
from abc import ABC, abstractmethod

class FlujoFilterStrategy(ABC):
    @abstractmethod
    def filtrar(self, input_file: str, output_file: str) -> None:
        """
        Filtra el archivo de flujos dado input_file y escribe el resultado en output_file.
        """
        pass
