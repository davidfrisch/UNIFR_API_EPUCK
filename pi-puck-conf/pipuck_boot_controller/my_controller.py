from unifr_api_epuck import wrapper 

r = wrapper.get_robot('192.168.93.89', is_pipuck=True)

r.set_speed(1,-1)

for _ in range(30):
    r.go_on()

r.clean_up()