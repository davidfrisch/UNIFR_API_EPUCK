import json
from os import read
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.function_base import average
from numpy.lib.npyio import save
import pandas as pd


def read_values(path_json_file):
    with open(path_json_file) as json_file:
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
    #WiFi data    
    time_to_send_data = [dict_data['time_to_send_data'] for dict_data in dict_datas]
    time_to_receive_image = [dict_data['time_to_receive_image']for dict_data in dict_datas]
    time_to_receive_sensor = [dict_data['time_to_receive_sensor']for dict_data in dict_datas]
    time_check_header = [dict_data['time_to_check_header']for dict_data in dict_datas]
  
    barWidth = 1
    #plt.title('Time for the e-puck2 with pipuck to do a simple loop go_on without communication')
    plt.barh(r, [0.001,0.001], color='#F5F121', edgecolor='white', label='Time to send the data')
    left_wifi = [0.001,0.001]

    plt.barh(r, time_check_header, left=left_wifi, color='#B625E8', edgecolor='white', label='Time to check the header')
    left_wifi = np.add(left_wifi, time_check_header)

    
    plt.barh(r, time_to_receive_image, left=left_wifi, color='#1DB6E0', edgecolor='white', label='Time to receive image')
    left_wifi = np.add(left_wifi, time_to_receive_image)

    plt.barh(r, time_to_receive_sensor, left=left_wifi, color='#148AF7', edgecolor='white', label='Time to receive sensor data')
    left_wifi = np.add(left_wifi, time_to_receive_sensor)


    
    #plt.barh([2,3], update_sensor_data, color='#ffA500', edgecolor='white', label='Time to update sensor data')

    #print(process_time_values)
    
    plt.autoscale()
    plt.yticks([0,1], names, fontweight='bold')
    plt.xlabel('time [s]')
    plt.legend()
    plt.show()
   

#Benchmark speed of sending image to memory which will process

#file epuck wifi_image
wifi_go_on_with_image = read_values('results_go_on_wifi_with_image.json')
wifi_go_on_with_image = get_averages(wifi_go_on_with_image)


#file epuck wifi_no_image
wifi_go_on_no_image = read_values('results_go_on_wifi_no_image.json')
wifi_go_on_no_image = get_averages(wifi_go_on_no_image)


print(sum(wifi_go_on_with_image.values())/sum(wifi_go_on_no_image.values()))
#print(1/sum(wifi_go_on_with_image.values()))
#get_subgraph(['WiFi with image','WiFi without image'], wifi_go_on_with_image, wifi_go_on_no_image)


