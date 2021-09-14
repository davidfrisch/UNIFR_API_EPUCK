#the unifr_api_epuck_test in the same folder of this file contains additional time measures for the benchmark
#in the take_picture() and get_camera_read() method
from unifr_api_epuck_test import wrapper
import os

r = wrapper.get_robot(is_pipuck=True)
r.init_camera(size=(120,160))
r.init_sensors()

for _ in range(300):
    r.go_on()
    r.take_picture('pi_pic.jpg')
    #os.system('scp "%s" "%s:%s"' % ('pi_pic.jpg', 'THEMACBOOK@192.168.89.24', '/Users/THEMACBOOK/Desktop'))
