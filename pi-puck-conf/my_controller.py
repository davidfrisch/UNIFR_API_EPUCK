#Example of a simple code with the pi-puck
#The robot turns around its self

from unifr_api_epuck import wrapper

robot = wrapper.get_robot(is_pipuck=True)
robot.set_speed(2, -2)

for _ in range(100):
    robot.go_on()

robot.clean_up()