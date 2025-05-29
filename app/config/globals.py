from modulo.deteccion import DetectionModule 


processes = {} # Diccionario global que nos permite almacenar la referencia al proceso de captura.

detection_module = DetectionModule()

# The interface to listen on.
NETWORK_INTERFACE = "br-c7e7ec0172e0"

# 'br-05d0a28ad910' 
# The path to the pcap file to save.
PCAP_FILE = 'modulo/capturas/pcaps/capture.pcap'


# name of the log file
LOG_PATH = 'modulo/capturas/logs'
LOG_FILE = 'bto_logs.log'

#The path to the capture file to save
FILE_PATH = "modulo/capturas/flow_analysis.binetflow"

