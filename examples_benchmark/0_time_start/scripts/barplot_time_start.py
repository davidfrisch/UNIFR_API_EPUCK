import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.npyio import save
import pandas as pd


def read_values(path_json_file):
    with open(path_json_file) as json_file:
        data = json.load(json_file)
        return data


def get_averages(dict_data):
    return {key:np.average(dict_data[key]) for key in dict_data}

def get_subgraph(names, *dict_datas):
    r = list(range(len(names)))
    init_time = [dict_data['init_time'] for dict_data in dict_datas]
    init_camera_time = [dict_data['init_camera_time'] for dict_data in dict_datas]

  
    plt.barh(r, init_time, color='#58555A', edgecolor='white', label='Time to get the connection between the robot and the controller')
    left = init_time
    
    plt.barh(r, init_camera_time, left=left, color='y', edgecolor='white', label='Time to initialise the camera')


    plt.yticks(r, names, fontweight='bold')
    plt.xlabel('time [s]')
    plt.legend()
    plt.show()
#Benchmark speed of sending image to memory which will process

#folder pipuck no camera
pipuck_no_camera = read_values('pi_no_camera_init.json')
pipuck_no_camera = get_averages(pipuck_no_camera)
print(pipuck_no_camera)

#folder pipuck with camera
pipuck_with_camera = read_values('results_pi_start.json')
pipuck_with_camera = get_averages(pipuck_with_camera)
print(pipuck_with_camera)


#folder with WiFi
wifi_epuck = read_values('results_wifi_start.json')
wifi_epuck = get_averages(wifi_epuck)
#print(wifi_epuck)



get_subgraph(["Pi-puck with camera initialisation","Pi-puck without camera initialisation","E-puck2 controlled with WiFi"],pipuck_with_camera,pipuck_no_camera,wifi_epuck)


