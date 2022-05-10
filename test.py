import time
from unifr_api_epuck import wrapper
r = wrapper.get_robot()

###########################
#####    Motos      ######
###########################

for _ in range(50):
    r.go_on()
    r.set_speed(2)

for _ in range(50):
    r.go_on()
    r.set_speed(-2)

r.set_speed(0)
r.go_on()

###########################
#####     SENSORS    ######
###########################
r.init_sensors()

print('Values of proximity sensors')
#get proximity sensors
for _ in range(100):
    r.go_on()
    print('proximity sensors: '+ str(r.get_prox()))

print('Values of ground sensors')
#get ground sensors 
for _ in range(100):
    r.go_on()
    print('ground sensors: '+ str(r.get_ground()))

print('Value of Tof sensors')
#get Time Of Flight
for _ in range(100):
    r.go_on()
    print('Tof sensors'+ str(r.get_tof()))

###########################
#####     CAMEARA    ######
###########################

r.init_camera('/Users/THEMACBOOK/Desktop/images')
print('init camera')
#take pictures

for _ in range(10):
    r.go_on()

for _ in range(3):
    r.go_on()
    r.take_picture()
    
#live stream
for _ in range(50):
    r.go_on()
    r.live_camera()

r.disable_camera()
print('camera disable')


###########################
#####  Comunication  ######
###########################

#robot connects to the host communication
print('init_comm')
try:
    r.init_client_communication('localhost')

    start_time = time.time()

    while start_time + 15 > time.time():
        if r.has_receive_msg():
            print(r.receive_msg())
except:
    print("Communication is not online")

