from modulo.deteccion import DetectionModule 


processes = {} # Diccionario global que nos permite almacenar la referencia al proceso de captura.

detection_module = DetectionModule()

# The interface to listen on.
NETWORK_INTERFACE = "br-1d4e96a902cd"

 
# The path to the pcap file to save.
PCAP_FILE = 'modulo/capturas/pcaps/capture.pcap'


# name of the log file
LOG_PATH = 'modulo/capturas/logs'
LOG_FILE = 'bto_logs.log'

#The path to the capture file to save
FILE_PATH = "modulo/capturas/flow_analysis.binetflow"

def set_file_path(new_path):
    global FILE_PATH
    FILE_PATH = new_path
    print(f"[globals.py] FILE_PATH actualizado a: {FILE_PATH}")