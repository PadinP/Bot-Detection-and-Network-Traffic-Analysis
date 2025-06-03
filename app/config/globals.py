from modulo.deteccion import DetectionModule 


processes = {} # Diccionario global que nos permite almacenar la referencia al proceso de captura.

detection_module = DetectionModule()

# The interface to listen on.
NETWORK_INTERFACE = "br-127288f36ad3"

 
# The path to the pcap file to save.
PCAP_FILE = 'modulo/capturas/pcaps/capture.pcap'


# name of the log file
LOG_PATH = 'modulo/capturas/logs'
LOG_FILE = 'bto_logs.log'

OUTPUT_FOLDER="modulo/capturas/archivos_filtrados"