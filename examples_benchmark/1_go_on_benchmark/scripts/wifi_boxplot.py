import json
from os import read
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.function_base import _average_dispatcher, average
from numpy.lib.npyio import save
import pandas as pd


def read_values(path_json_file):
    with open(path_json_file) as json_file:
        data = json.load(json_file)
        return data


def get_averages(dict_data):
    return {key:np.average(dict_data[key]) for key in dict_data}

def color_box(bp, color):

    # Define the elements to color. You can also add medians, fliers and means
    elements = ['boxes','caps','whiskers']

    # Iterate over each of the elements changing the color
    for elem in elements:
        [plt.setp(bp[elem][idx], color=color) for idx in range(len(bp[elem]))]
    return



#Benchmark speed of sending image to memory which will process


wifi_go_on = read_values('results_go_on_wifi_with_image.json')

time_to_send_data=  [number*1000 for number in wifi_go_on['time_to_send_data']]
time_to_check_header = wifi_go_on['time_to_check_header']
time_to_receive_sensor = wifi_go_on['time_to_receive_sensor']
time_to_receive_image = wifi_go_on['time_to_receive_image']


bp = plt.boxplot([time_to_receive_image])


color_box(bp, '#1DB6E0')



plt.autoscale()

#yaxe = [i/100 for i in range(9)]
plt.ylim((0,1))
plt.ylabel('time [s]')
plt.xticks([1],['(WiFi)\nTime to receive image'], fontweight='bold')

#plt.legend()
plt.show()
