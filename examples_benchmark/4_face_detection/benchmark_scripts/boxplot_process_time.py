import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.npyio import save
import pandas as pd

def color_box(bp, color):

    # Define the elements to color. You can also add medians, fliers and means
    elements = ['boxes','caps','whiskers']

    # Iterate over each of the elements changing the color
    for elem in elements:
        [plt.setp(bp[elem][idx], color=color) for idx in range(len(bp[elem]))]
    return

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
    r = [i+1 for i in range(len(names))]
    start_time_values = [dict_data['start_time'] for dict_data in dict_datas]
    exchange_time_values = [dict_data['exchange_data'] for dict_data in dict_datas]
    take_image_time = [dict_data['take_image'] for dict_data in dict_datas]
    process_time_values = [dict_data['process_image'] for dict_data in dict_datas]
   

    bp = plt.boxplot(process_time_values)
    color_box(bp, '#ffA500')
    plt.ylim((0,3.3))
    plt.xticks(r, names)
    plt.ylabel('time [s]')
    plt.title('Time to process the algorithm and get feedback')
    plt.show()

#Benchmark speed of sending image to memory which will process


#folder withComm
withComm160120 = read_values('withComm/160120_results_pi_withCommMac_face_detection.json')
withComm640480 = read_values('withComm/640480_results_pi_withCommMac_face_detection.json')





#folder withoutMac
withoutMac160120 = read_values('withoutMac/160120_results_pi_solo_face_detection.json')
withoutMac640480 = read_values('withoutMac/640480_results_pi_solo_face_detection.json')





#folder withScp
withScp160120 = read_values('withScp/160120_results_pi_withScpMac_face_detection.json')
withScp640480 = read_values('withScp/640480_results_pi_withScpMac_face_detection.json')




#folder withWifi
withWifi160120 = read_values('withWifi/results_wifi_solo_face_detection.json')



get_subgraph([ 
    '(160x120 px)\n E-puck2 control via WiFi \n(no pi-puck)',
    '(160x120 px)\n Only with pi-puck ',
    '(640x480 px)\n Only with pi-puck ',
    '(160x120 px)\n Pi-puck \n scp command \n PC ',
    '(640x480 px)\n Pi-puck \n scp command \n PC ',
    '(160x120 px)\n Pi-puck \n intercommunication \n PC ',
    '(640x480 px)\n Pi-puck \n intercommunication \n PC '],
    withWifi160120,
    withoutMac160120,
    withoutMac640480,
    withScp160120,
    withScp640480,
    withComm160120,
    withComm640480,  
    )


