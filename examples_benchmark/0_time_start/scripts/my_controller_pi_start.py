from unifr_api_epuck import wrapper
import time,json

init_time = time.time()
r = wrapper.get_robot(is_pipuck=True)
init_time = time.time() - init_time

time_init_camera = time.time()
r.init_camera('.')
time_init_camera = time.time()-time_init_camera


print('init_time: '+ str(init_time))
print('init_camera_time: '+ str(time_init_camera))
print('total time: '+ str(init_time+time_init_camera))


with open('results_pi_start.json') as json_file:
    data = json.load(json_file)
    data['init_time'] += [init_time]
    data['init_camera_time'] += [time_init_camera]
    data['total_time'] += [init_time+time_init_camera]
    print(data)

with open('results_pi_start.json', 'w') as json_file:
    json.dump(data, json_file)


