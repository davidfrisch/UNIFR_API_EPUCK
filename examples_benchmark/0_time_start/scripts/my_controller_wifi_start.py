from numpy.lib.function_base import average
from unifr_api_epuck_test import wrapper
import time,json


r = wrapper.get_robot('192.168.224.240')
sum = []
for _ in range(300): 
    time_go_on = time.time()
    r.go_on()
    sum += [time.time() - time_go_on]

print(1/average(sum))

