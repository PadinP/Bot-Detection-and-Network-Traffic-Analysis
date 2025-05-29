import socket
import struct
import sys
import numpy as np
import pickle


def loaddata(fileName):
    file = open(fileName, 'r')

    xdata = []
    ydata = []
    xdataT = []
    ydataT = []

    count1 = 0
    count2 = 0

    # Diccionarios para convertir protocolos y estados a enteros
    protoDict = {
        'arp': 5, 'unas': 13, 'udp': 1, 'rtcp': 7, 'pim': 3, 'udt': 11, 'esp': 12, 'tcp': 0,
        'rarp': 14, 'ipv6-icmp': 9, 'rtp': 2, 'ipv6': 10, 'ipx/spx': 6, 'icmp': 4, 'igmp': 8
    }

    stateDict = {
        "Background": 0, "Normal": 0, "Botnet": 1
    }

    file.readline()  # Saltar la primera línea

    for line in file:
        sd = line.strip().split(',')
        dur, proto, sport, dport, sip, dip, totP, totB, label, state = (
            sd[1], sd[2], sd[4], sd[7], sd[3], sd[6], sd[-4], sd[-3], sd[-1], sd[8]
        )

        try:
            sip = struct.unpack("!L", socket.inet_aton(sip))[0]
            dip = struct.unpack("!L", socket.inet_aton(dip))[0]
        except socket.error:
            continue

        if not sport or not dport:
            continue

        try:
            label = stateDict.get(label, -1)
            if label == 0 and count1 < 25000:
                xdata.append([
                    float(dur), protoDict.get(proto, -1), int(sport), int(dport),
                    sip, dip, int(totP), int(totB), stateDict.get(state, -1)
                ])
                ydata.append(label)
                count1 += 1
            elif label == 1 and count2 < 25000:
                xdata.append([
                    float(dur), protoDict.get(proto, -1), int(sport), int(dport),
                    sip, dip, int(totP), int(totB), stateDict.get(state, -1)
                ])
                ydata.append(label)
                count2 += 1
        except ValueError:
            continue

    # Guardar los datos preprocesados en un archivo pickle
    with open('modulo/database/pickle/flowdata.pickle', 'wb') as file:
        pickle.dump([np.array(xdata), np.array(ydata), np.array(xdataT), np.array(ydataT)], file)

    return np.array(xdata), np.array(ydata)


if __name__ == "__main__":
    loaddata('flowdata.binetflow')
