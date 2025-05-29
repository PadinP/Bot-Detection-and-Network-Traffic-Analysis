import multiprocessing
import time
import sys
import os
from SniffPyBot.features_capture_mp.capture import Capture
from SniffPyBot.features_capture_mp.settings import logger as logging
from SniffPyBot.features_capture_mp.utils import verify_interface
from app.config.globals import NETWORK_INTERFACE, PCAP_FILE

def run_capture():
    logging.info('Starting application with PID: %s' % os.getpid())
    print('PID: %s' % os.getpid())
    interface = NETWORK_INTERFACE
    out_file = PCAP_FILE
    if verify_interface(interface):
        capture = Capture(interface, out_file)
        capture.start()
    else:
        logging.error(f'Interface {interface} doesnt exists, exiting application')
        sys.exit()


if __name__ == '__main__':
    start = time.perf_counter()
    run_capture()
    # to avoid execution ends if packets to capture is different than 0 ( 0 = forever)
    # if its necessary to measure the execution time
    while multiprocessing.active_children():
        pass
    total = time.perf_counter() - start
    print(total)
