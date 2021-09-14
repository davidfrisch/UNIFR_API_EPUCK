import json
from os import read
import matplotlib.pyplot as plt
import numpy as np
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
    create_checksum = [dict_data['create_checksum']*2 for dict_data in dict_datas]
    update_sensor_data = [dict_data['update_sensor_data']for dict_data in dict_datas]
    retrieve_checksum_from_robot = [dict_data['retrieve_checksum_from_robot'] for dict_data in dict_datas]
    
  
    barWidth = 1
    #plt.title('Time for the e-puck2 with pipuck to do a simple loop go_on without communication')
    plt.barh(r, create_checksum, color='#F52D22', edgecolor='#F52D22', label='Time to create checksum')
    left_wifi = create_checksum


    
    plt.barh(r, update_sensor_data, left=left_wifi, color='#65CAA0', edgecolor='#65CAA0', label='Time to update the data sensors')
    left_wifi = np.add(left_wifi, update_sensor_data)


    
    plt.barh(r, retrieve_checksum_from_robot, left=left_wifi, color='#783F34', edgecolor='#783F34', label='Time to check the received checksum')
    left_wifi = np.add(left_wifi, retrieve_checksum_from_robot)

    time_to_wait = [0.05-(retrieve_checksum_from_robot[0]+update_sensor_data[0]+create_checksum[0]),0]
    plt.barh(r, time_to_wait, left=left_wifi, color='#E1A36C', edgecolor='#E1A36C', label='Time sleep for stable frequency')


    #print(process_time_values)
    
    plt.autoscale()
    plt.yticks([0,1], [names[0],names[1]], fontweight='bold')
    plt.xlabel('time [s]')
  
    plt.legend()
    plt.show()
   

#Benchmark speed of sending image to memory which will process


pipuck_normal = read_values('results_go_on_pipuck_normal.json')
pipuck_normal = get_averages(pipuck_normal)


pipuck_stress = read_values('results_go_on_pipuck_stress.json')
pipuck_stress = get_averages(pipuck_stress)

print(1/(sum(pipuck_stress.values())))

#get_subgraph(['Pi-puck default speed','Pi-puck overlock'], pipuck_normal, pipuck_stress)


