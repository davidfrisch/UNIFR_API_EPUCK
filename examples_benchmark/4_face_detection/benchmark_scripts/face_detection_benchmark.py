import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.npyio import save
import pandas as pd


def read_values(path_json_file):
    with open('../'+path_json_file) as json_file:
        data = json.load(json_file)
        return data

def combine_datas(data1, data2):
    combine_data = None
    if len(data1.keys()) > len(data2.keys()):
        for key in data2:
            data1[key] += data2[key]
        combine_data = data1
    else:
        for key in data1:
            data2[key] += data1[key]
        combine_data = data2

    return combine_data


def get_averages(dict_data):
    return {key:np.average(dict_data[key]) for key in dict_data}

def get_subgraph(names, *dict_datas):
    r = list(range(len(names)))
    start_time_values = [dict_data['start_time'] for dict_data in dict_datas]
    exchange_time_values = [dict_data['exchange_data'] for dict_data in dict_datas]
    take_image_time = [dict_data['take_image'] for dict_data in dict_datas]
    process_time_values = [dict_data['process_image'] for dict_data in dict_datas]
    

    barWidth = 1
    left = 0 #start_time_values

    plt.barh(r, take_image_time, left=left, color='y', edgecolor='white', label='Time to retrieve and save image')
    left = np.add(left, take_image_time)

    plt.barh(r, process_time_values, left=left, color='#ffA500', edgecolor='white', label='Time to get feedback from face detection algorithm')

    plt.yticks(r, names, fontweight='bold')
    plt.xlabel('time [s]')
    plt.legend(loc='lower right')
    plt.show()

#Benchmark speed of sending image to memory which will process

#folder withComm
withComm160120 = read_values('withComm/160120_results_pi_withCommMac_face_detection.json')
withComm640480 = read_values('withComm/640480_results_pi_withCommMac_face_detection.json')

withComm160120 = get_averages(withComm160120)
withComm640480 = get_averages(withComm640480)


#folder withoutMac
withoutMac160120 = read_values('withoutMac/160120_results_pi_solo_face_detection.json')
withoutMac640480 = read_values('withoutMac/640480_results_pi_solo_face_detection.json')

withoutMac160120 = get_averages(withoutMac160120)
withoutMac640480 = get_averages(withoutMac640480)


#folder withScp
withScp160120 = read_values('withScp/160120_results_pi_withScpMac_face_detection.json')
withScp640480 = read_values('withScp/640480_results_pi_withScpMac_face_detection.json')

withScp160120 = get_averages(withScp160120)
withScp640480 = get_averages(withScp640480)

#folder withWifi
withWifi160120 = read_values('withWifi/results_wifi_solo_face_detection.json')
withWifi160120 = get_averages(withWifi160120)


get_subgraph([ 
    'E-puck2 control from PC via WiFi (no pi-puck)',
    'Only with pi-puck (160x120 px)',
    'Only with pi-puck (640x480 px)',
    'Pi-puck - scp command - PC (160x120 px)',
    'Pi-puck - scp command - PC (640x480 px)',
    'Pi-puck - intercommunication - PC (160x120 px)',
    'Pi-puck - intercommunication - PC (640x480 px)'],
    withWifi160120,
    withoutMac160120,
    withoutMac640480,
    withScp160120,
    withScp640480,
    withComm160120,
    withComm640480,  
    )


