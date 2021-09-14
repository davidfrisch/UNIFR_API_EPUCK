import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.function_base import average
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




wifi_go_on_image = read_values('results_120_wifi.json')


time_to_write_image = [number*1000 for number in wifi_go_on_image['time_to_write_image']]
time_to_capture_image = [number*1000 for number in wifi_go_on_image['time_to_receive_camera_info']]
time_to_convert_image = [number*1000 for number in wifi_go_on_image['time_convert_rgb565_to_bgr888']]


bp = plt.boxplot(time_to_capture_image)
color_box(bp, 'g')



plt.autoscale()
plt.ylim(top=1700)
plt.ylabel('time [ms]')
plt.xticks([1],['(WiFi)\n Time to convert image \n RGB565 to BGR888'], fontweight='bold')
plt.show()
