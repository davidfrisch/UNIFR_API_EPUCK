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


#folder pipuck no camera
pipuck_no_camera = read_values('pi_no_camera_init.json')['init_time']

#folder pipuck with camera
pipuck_with_camera = read_values('results_pi_start.json')['init_time']
pipuck_with_camera_init_camera = read_values('results_pi_start.json')['init_camera_time']
for i in range(len(pipuck_with_camera)):
    pipuck_with_camera[i]+=pipuck_with_camera_init_camera[i]

#folder with WiFi
wifi_epuck = read_values('results_wifi_start.json')['init_time']


bp = plt.boxplot([pipuck_with_camera])


color_box(bp, '#58555A')

plt.autoscale()

plt.ylabel('time [s]')
plt.xticks([1],['(Pi-puck with camera)\nTime to initialisation'], fontweight='bold')
#,'(Pi-puck no camera)\nTime to initialisation','(Pi-puck with camera)\nTime to initialisation'
#plt.legend()
plt.show()
