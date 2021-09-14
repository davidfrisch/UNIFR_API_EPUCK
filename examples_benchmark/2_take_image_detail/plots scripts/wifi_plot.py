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


    time_convert_rgb565_to_bgr888 = [dict_data["time_convert_rgb565_to_bgr888"]*1000 for dict_data in dict_datas]
    time_to_write_image = [dict_data['time_to_write_image']*1000 for dict_data in dict_datas]
    time_to_receive_camera_info = [dict_data['time_to_receive_camera_info']*1000 for dict_data in dict_datas]
    

    #plt.title('Time to capture an image using the e-puck2 with WiFi')

    plt.barh(r, time_to_receive_camera_info, color='g', edgecolor='white', label='Time to capture and receive the image: '+str(round(time_to_receive_camera_info[0],2))+'ms.')
    left = time_to_receive_camera_info#np.add(0, time_to_receive_camera_info)
   
    plt.barh(r, time_convert_rgb565_to_bgr888 ,left=left, color='y', edgecolor='white', label='Time to convert from RGB565 to BGR888: '+str(round(time_convert_rgb565_to_bgr888[0],2))+'ms.')
    
    left = np.add(left,time_convert_rgb565_to_bgr888 )

    plt.barh(r, [3], left=left, color='#ffc0cb', edgecolor='white', label='Time to write image in the computer: '+str(round(time_to_write_image[0],2))+'ms.')
    #left = np.add(left, time_convert_rgb565_to_bgr888)
    
   

    #plt.barh(r, process_time_values, left=left, color='#ffA500', edgecolor='white', label='time to get feedback')

    plt.autoscale()
    plt.yticks(r, names, fontweight='bold')
    plt.xlabel('time [ms]')
    plt.legend()
    plt.show()


wifi_go_on_image = read_values('data/results_120_wifi.json')
wifi_go_on_image = get_averages(wifi_go_on_image)


get_subgraph(['epuck2 with WiFi'], wifi_go_on_image)


