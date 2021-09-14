from numpy.lib.function_base import average
from unifr_api_epuck_test import wrapper
import time

r = wrapper.get_robot('192.168.224.240')
r.init_sensors()
r.init_camera()
#r.set_clock_speed(500)
print('go !')
sum = []
chrono = time.time()
for _ in range(300):
    r.go_on()
  
