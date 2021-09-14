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
    return {key: np.average(dict_data[key]) for key in dict_data}


def get_subgraph(names, *dict_datas):
    r = list(range(len(names)))

    loop_img_time = [dict_data['loop_img_time']  * 1000 for dict_data in dict_datas]
    time_to_write_image = [ dict_data['time_to_write_image']*1000 for dict_data in dict_datas]
    resize_img_time = [dict_data['resize_img_time'] * 1000 for dict_data in dict_datas]

    barWidth = 1
    #plt.title('Time to capture an image using the e-puck2 with the pipuck')

    plt.barh(r, loop_img_time, color='g',
             label='Time to capture and receive 5 images')
    left = loop_img_time

    plt.barh(r, resize_img_time, left=left, color='y', label='Time to resize the image')
    left = np.add(left, resize_img_time)

    plt.barh(r, time_to_write_image, left=left, color='#ffc0cb',
              label='Time to write the image')
    #left = np.add(left, loop_img_time)

    time_for_a_picture_0 = loop_img_time[0]/5
    time_for_a_picture_1 = loop_img_time[1]/5
    #time_for_a_picture_2 = loop_img_time[2]/5
    #time_for_a_picture_3 = loop_img_time[3]/5
    
    left_sep_0 = time_for_a_picture_0
    left_sep_1 = time_for_a_picture_1
    #left_sep_2 = time_for_a_picture_2
    #left_sep_3 = time_for_a_picture_3

    for _ in range(4):
        plt.barh(r[0], [0.5,0.5], left = left_sep_0, color='r')
        plt.barh(r[1], [0.5,0.5], left = left_sep_1, color='r')
        #plt.barh(r[2], [0.5,0.5], left = left_sep_2, color='r')
        #plt.barh(r[3], [0.5,0.5], left = left_sep_3, color='r')
        left_sep_0 += time_for_a_picture_0
        left_sep_1 += time_for_a_picture_1
        #left_sep_2 += time_for_a_picture_2
        #left_sep_3 += time_for_a_picture_3
    

    # plt.barh(r, process_time_values, left=left, color='#ffA500', edgecolor='white', label='time to get feedback')

    # print(process_time_values)
    plt.yticks(r, names, fontweight='bold')
    plt.xlabel('time [ms]')
    plt.legend(loc="upper right")
    plt.show()


grab_results_160120 = read_values('data/grab_results_160120.json')
grab_results_640480 = read_values('data/grab_results_640480.json')

read_results_160120 = read_values('data/open_cv_results_160120.json')
read_results_640480 = read_values('data/open_cv_results_640480.json')


read_results_160120 = get_averages(read_results_160120)
read_results_640480 = get_averages(read_results_640480)
grab_results_160120 = get_averages(grab_results_160120)
grab_results_640480 = get_averages(grab_results_640480)


get_subgraph([
    'pi-puck \n camera resolution 160x120',
    'pi-puck \n camera resolution 640x480',], 
    read_results_160120,
    read_results_640480,)
