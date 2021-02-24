#from unifr_api_epuck.epuck import *
from .epuck import Epuck
from .constants import *
import time
import socket
from math import sqrt

class WebotsEpuck(Epuck):

    def __init__(self):
        from controller import Robot
        super().__init__('localhost')
        self.robot = Robot()
        # init the motors
        self.left_motor = self.robot.getDevice('left wheel motor')
        self.right_motor = self.robot.getDevice('right wheel motor')

        self.left_motor_counter = 0
        self.right_motor_counter = 0

        # init the leds
        self.led = []

        # led 8 is body and 9 is front red LED
        ledNames = [
            'led0', 'led1', 'led2', 'led3',
            'led4', 'led5', 'led6', 'led7',
            'led8', 'led9'
        ]
        for i in range(len(ledNames)):
            self.led.append(self.robot.getDevice(ledNames[i]))
            self.led[i].set(0)

        # init camera
        self.camera = self.robot.getDevice('camera')

        # other components
        self.accelerometer = self.robot.getDevice('accelerometer')
        self.accelerometer.enable(TIME_STEP)

        self.gyro = self.robot.getDevice('gyro')
        self.gyro.enable(TIME_STEP)

        self.tof = self.robot.getDevice('tof')
        self.tof.enable(TIME_STEP)

        
        # To uncomment if you want to use Webot specific communication
         
        self.emitter = None
        self.receiver = None
 
    
    def get_id(self):
        """
        :returns: The host name of the computer
        """
        
        return self.robot.getName()

    def get_ip(self):
        """
        Gets name of the host
        """
        return socket.gethostname()

    def go_on(self):
        """
        Goes to next frame
        """
        super().go_on()
        self.robot.step(TIME_STEP)

        return True

    def sleep(self, duration):
        return super().sleep(duration)

    def get_battery_level(self):
        """
        .. warning::
            Only works with real robots
        """
        return super().get_battery_level()

    #################
    #    MOTORS      #
    #################

    def set_speed(self, speed_left, speed_right=None):
        if speed_right is None:
            speed_right = speed_left

        # get a handler to the motors and set target position to infinity (speed control)
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))

        # set up the motor speeds at 10% of the MAX_SPEED.
        self.left_motor.setVelocity(super().bounded_speed(speed_left))
        self.right_motor.setVelocity(super().bounded_speed(speed_right))

    def get_speed(self):
        return [self.left_motor.getVelocity(), self.right_motor.getVelocity()]

    def bounded_speed(self, speed):
        return super().bounded_speed(speed)


    #################
    #       LED      #
    #################

    # LEDS are initiated when creation of the instance of the robot
    def enable_led(self, led_position, red=None, green=None, blue=None):
        if led_position in range(LED_COUNT_ROBOT):

            if led_position % 2 == 0:

                if red or green or blue:
                    print('LED ' + led_position + ' is not RGB')

                self.led[led_position].set(1)

            else:

                if red != None and green != None and blue != None:

                    # lambda function to check if r,g,b are between 0 and 100
                    def between(color_val): return 0 <= color_val <= 100
                    in_rgb_range_values = list(
                        map(between, (red, green, blue)))

                    if all(in_rgb_range_values):
                        rgb = red*256**2 + green*256 + blue
                        self.led[led_position].set(rgb)
                    else:
                        for i in range(3):
                            color = {0: 'red', 1: 'green', 2: 'blue'}
                            if not in_rgb_range_values[i]:
                                print(
                                    'color '+ color[i] + ' is not between 0 and 100')

                else:
                    self.led[led_position].set(0xFF0000)

        else:
            print(
                'invalid led position: ' + led_position + '. Accepts 0 <= x <= 7. LEDs unchanged.')

    def disable_led(self, led_position):
        if led_position not in range(LED_COUNT_ROBOT):
            print(
                'invalid led position: '+ led_position + '. Accepts 0 <= x <= 7. LED stays ON.')

        self.led[led_position].set(0)

    def enable_all_led(self):
        return super().enable_all_led()

    def disable_all_led(self):
        return super().disable_all_led()

    def enable_body_led(self):
        self.led[8].set(1)

    def disable_body_led(self):
        self.led[8].set(0)

    def enable_front_led(self):
        self.led[9].set(1)

    def disable_front_led(self):
        self.led[9].set(0)

    ##### END ####
    #    LED     #
    ##############
    #################
    #   SENSORS     #
    #################
    # Need to init sensors before using them

    def init_sensors(self):
        psNames = [
            'ps0', 'ps1', 'ps2', 'ps3',
            'ps4', 'ps5', 'ps6', 'ps7'
        ]
        for i in range(8):
            self.ps.append(self.robot.getDevice(psNames[i]))
            self.ps[i].enable(TIME_STEP)

    def disable_sensors(self):
        return super().disable_sensors()

    def get_prox(self):

        try:
            prox_values = [self.ps[i].getValue()
                           for i in range(PROX_SENSORS_COUNT)]
        except:
            print('Did you forget to my_robot.init_sensors() ?')
            return

        return prox_values

    def calibrate_prox(self):
        return super().calibrate_prox()

    def get_calibrate_prox(self):
        return super().get_calibrate_prox()

    def init_tof():
        pass

    def get_tof(self):
        return self.tof.getValue()

    def disable_tof(self):
        return super().disable_tof()
        
    def init_ground(self):
        """
        Initiates the ground sensors of the robot

        .. note::
            On Webots, initally the robot does not embed the ground sensors. You must add the NODE 'E-puckGroundSensors (Transform)' to the robot to embed it.
        
        .. image:: ../res/add_node_webots_p1.png
            :width: 300
            :alt: add the Node

        .. image:: ../res/add_node_webots_p2.png
            :width: 300
            :alt: add the Node
        
        .. image:: ../res/addGroundSensors.png
            :width: 500
            :alt: select the ground sensor
        """
        gsNames = [
            'gs0', 'gs1', 'gs2'
        ]
        try:
            for i in range(GROUND_SENSORS_COUNT):
                self.gs.append(self.robot.getDevice(gsNames[i]))
                self.gs[i].enable(TIME_STEP)
        except Exception as e:
            print('Did you add the ground sensor extension ? \n'+str(e))

    def get_ground(self):
        try:
            ground_values = [self.gs[i].getValue()
                             for i in range(GROUND_SENSORS_COUNT)]

        except:
            print('Robot must add ground sensors to simulation and/or must init_ground()')
            return

        return ground_values

    ###   BEGIN ##########
    #  Gyroscope         #
    # acceleration       #
    # acceleration axes  #
    #  microphone        #
    #  orientation       #
    #  inclination       #
    #  temperature       #
    #  Time Of Fight     #
    ######################


    def get_gyro_axes(self):
        # round values to integers for homogeniety with real robot
        round_values = [round(i) for i in self.gyro.getValues()]
        return round_values

    def get_accelerometer_axes(self):
        # round values to integers for homogeniety with real robot
        round_values = [round(i) for i in self.accelerometer.getValues()]
        return round_values

    def get_acceleration(self):
        [x,y,z] = self.get_accelerometer_axes
        return sqrt(x**2 + y**2 + z**2)

    def get_roll(self):
        return super().get_roll()

    def get_pitch(self):
        return super().get_pitch()

    def get_microphones(self):
        """
        .. warning::
            Only works with real robots
        """
        return super().get_microphones()

    def get_temperature(self):
        """
        .. warning::
            Only works with real robots
        """
        return super().get_temperature()

    def get_temp(self):
        print('no temperature on Webots')

    #####   END    ######
    #  Gyroscope        #
    # acceleration      #
    # acceleration axes #
    #  microphone       #
    #  pitch            #
    #  roll             #
    #  temperature      #
    #  Time Of Fight    #
    ####################

 

    #### begin ####
    #    CAMERA  #
    ##############
    # Need to init_camera before calling other methods

    def init_camera(self, save_image_folder=None, camera_rate=1):
        if not save_image_folder:
            save_image_folder = './'

        self.save_image_folder = save_image_folder
        self.camera.enable(TIME_STEP*camera_rate)

    def disable_camera(self):
        self.camera.disable()


    def get_camera(self):
        self.red, self.blue, self.green = [], [], []
        cameraData = self.camera.getImage()

        # get the rgb of each pixel
        for n in range(CAMERA_WIDTH):
            for m in range(CAMERA_HEIGHT):
                # get the color component of the pixel (n,m)
                self.red += [self.camera.imageGetRed(
                    cameraData, CAMERA_WIDTH, n, m)]
                self.green += [self.camera.imageGetGreen(
                    cameraData, CAMERA_WIDTH, n, m)]
                self.blue += [self.camera.imageGetBlue(
                    cameraData, CAMERA_WIDTH, n, m)]

        return self.red, self.green, self.blue

    # https://www.cyberbotics.com/doc/reference/camera?tab-language=python
    def take_picture(self):
        """
        Takes a picture and saves it in defined image folder from :py:meth:`init_camera<unifr_api_epuck.epuck_webots.WebotsEpuck.init_camera>`
        """
        try:
            counter = '{:04d}'.format(self.counter_img)
            save_as = self.save_image_folder + '/image' + counter + '.jpg'
            self.camera.saveImage(save_as, 100)  # 100 for best quality
            self.counter_img += 1
        except Exception as e:
            print(e)

    def live_camera(self, live_time=None):
        """
        .. note:: 
            Only call this method if you prefer to stream from the unifr_api_epuck GUI instead of Webots.
        """
        if not self.has_start_stream:
            # time setting
            self.start_time = time.time()
            self.has_start_stream = True

        # refresh time
        self.current_time = time.time()

        if live_time is None or (self.current_time - self.start_time) < live_time:
            try:
                save_as = self.save_image_folder + '/'+ self.get_id() +'_image_video.jpg'
                self.camera.saveImage(save_as, 100)  # 100 for best quality
                self.counter_img += 1
            except Exception as e:
                print(e)
        else:
            self.disable_camera()

    #################
    #       MUSIC   #
    #################

    # No music on Webots

    #################
    # COMMUNICATION #
    #################
    # Communication is initiated during creation of instance of the robot
    def init_host_communication(self):
        """
            Call this method to use Webots specific communication
        """
        #if host_id == self.get_id():
        #   Thread(target=hec.main, args=(host_ip,)).start()"""
        self.emitter = self.robot.getDevice('emitter')
        self.receiver = self.robot.getDevice('receiver')
        self.emitter.setChannel(1)
        self.receiver.setChannel(1)
        self.receiver.enable(TIME_STEP)

    def init_client_communication(self, host_ip='localhost'):
        """

        *   If you called the init_host_communication(), then the e-puck will connect to the specific Webots 
            communication.

        *   If you do not call the init_host_communication(), then the robot will try to find 
            a host communication.

        """
        if self.emitter == None:
            return super().init_client_communication(host_ip=host_ip)

    def send_msg(self, msg):
        """
        Puts a message in queue to other robots.

        .. warning ::
            If you use Webots communication then you can only send strings.
        """
        if self.emitter == None:
            super().send_msg(msg)
        else:
            if isinstance(msg, str):
                bmsg = str.encode(msg)
                self.emitter.send(bmsg)

            else:
                print('Error : Emitter can only send string')

        
    def has_receive_msg(self):
        if self.emitter == None:
            return super().has_receive_msg()
        else:
            return self.receiver.getQueueLength() > 0
        
    def receive_msg(self):
        if self.emitter == None:
            return super().receive_msg()
        else:
            if self.has_receive_msg():
                bmsg = self.receiver.getData()
                msg = bmsg.decode()
                self.receiver.nextPacket()
                return msg

        return None

    def clean_up(self):
        for _ in range(50):
            self.set_speed(0, 0)
            self.go_on()
        #print('Robot cleaned')