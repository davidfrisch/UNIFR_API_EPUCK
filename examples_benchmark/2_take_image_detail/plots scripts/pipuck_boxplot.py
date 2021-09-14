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



grab_results_160120 = read_values('data/grab_results_160120.json')
grab_results_640480 = read_values('data/grab_results_640480.json')
read_results_160120 = read_values('data/read_results_160120.json')
read_results_640480 = read_values('data/read_results_640480.json')

time_to_write_160120 = [number*1000 for number in read_values('data/grab_results_160120.json')['time_to_write_image']]
time_to_write_640480 = [number*1000 for number in read_values('data/open_cv_results_640480.json')['time_to_write_image']]

read_time_to_take_picture_120 = [number*1000 for number in read_results_160120['loop_img_time']]
read_time_to_take_picture_640 = [number*1000 for number in read_results_640480['loop_img_time']]

read_time_to_resize_120 = [number*1000 for number in read_results_160120['resize_img_time']]


bp = plt.boxplot([read_time_to_take_picture_120])
color_box(bp, 'g')



plt.autoscale()

plt.ylim((190,280))
plt.ylabel('time [ms]')
plt.xticks([1],['(Pi-puck 160x120px)\nTime to capture 5 images'], fontweight='bold')
plt.show()
