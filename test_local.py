from unifr_api_epuck import wrapper

robot = wrapper.get_robot()
robot.init_client_communication()

while(True):
    if(robot.has_receive_msg()):
        robot.receive_msg()
        
    robot.go_on()