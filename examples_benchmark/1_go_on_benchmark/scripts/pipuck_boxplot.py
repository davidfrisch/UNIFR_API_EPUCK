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



pipuck_normal = read_values('results_go_on_pipuck_normal.json')
pipuck_stress = read_values('results_go_on_pipuck_stress.json')

create_checksum=  [number*1000 for number in pipuck_normal['create_checksum']]
update_sensor_data = pipuck_normal['update_sensor_data']
update_sensor_data_stress = pipuck_stress['update_sensor_data']

retrieve_checksum_from_robot = [number*1000 for number in pipuck_normal['retrieve_checksum_from_robot']]



bp = plt.boxplot([update_sensor_data,update_sensor_data_stress])


color_box(bp, '#65CAA0')

plt.autoscale()

#yaxe = [i/100 for i in range(9)]
plt.ylim((0.008,0.015))
plt.ylabel('time [s]')
plt.xticks([1,2],['(Pi-puck default speed)\nTime to update the sensors','(Pi-puck overclock)\nTime to update the sensors'], fontweight='bold')

#plt.legend()
plt.show()
