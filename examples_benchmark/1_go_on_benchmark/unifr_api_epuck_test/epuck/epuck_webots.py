#from unifr_api_epuck.epuck import *
from .epuck import Epuck
import time
import socket
from math import sqrt
import numpy as np

class WebotsEpuck(Epuck):

    def __init__(self):
        from controller import Robot
        super().__init__('localhost')

        self.TIME_STEP = 64

        self.__robot = Robot()
        # init the motors
        self.left_motor = self.__robot.getDevice('left wheel motor')
        self.right_motor = self.__robot.getDevice('right wheel motor')

        self.left_motor_counter = 0
        self.right_motor_counter = 0

        # init the leds
        self.__led = []
        self.__id = self.__robot.getName()

        # led 8 is body and 9 is front red LED
        ledNames = [
            'led0', 'led1', 'led2', 'led3',
            'led4', 'led5', 'led6', 'led7',
            'led8', 'led9'
        ]
        for i in range(len(ledNames)):
            self.__led.append(self.__robot.getDevice(ledNames[i]))
            self.__led[i].set(0)

        # init camera
        self.camera = self.__robot.getDevice('camera')
        self.__camera_width = self.camera.getWidth()
        self.__camera_height = self.camera.getHeight()

        # other components
        self.accelerometer = self.__robot.getDevice('accelerometer')
        self.accelerometer.enable(self.TIME_STEP)

        self.gyro = self.__robot.getDevice('gyro')
        self.gyro.enable(self.TIME_STEP)

        self.tof = self.__robot.getDevice('tof')
        self.tof.enable(self.TIME_STEP)

        
        # To uncomment if you want to use Webot specific communication
         
        self.emitter = None
        self.receiver = None
 
    
    def get_id(self):
        """
        :returns: The host name of the computer
        """
        return self.__id

    def set_id(self, new_id):
        return super().set_id(new_id)

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
        self.__robot.step(self.TIME_STEP)

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
        if led_position in range(self.LED_COUNT_ROBOT):

            if led_position % 2 == 0:

                if red or green or blue:
                    print('LED ' + led_position + ' is not RGB')

                self.__led[led_position].set(1)

            else:

                if red != None and green != None and blue != None:

                    # lambda function to check if r,g,b are between 0 and 100
                    def between(color_val): return 0 <= color_val <= 100
                    in_rgb_range_values = list(
                        map(between, (red, green, blue)))

                    if all(in_rgb_range_values):
                        rgb = red*256**2 + green*256 + blue
                        self.__led[led_position].set(rgb)
                    else:
                        for i in range(3):
                            color = {0: 'red', 1: 'green', 2: 'blue'}
                            if not in_rgb_range_values[i]:
                                print(
                                    'color '+ color[i] + ' is not between 0 and 100')

                else:
                    self.__led[led_position].set(0xFF0000)

        else:
            print(
                'invalid led position: ' + led_position + '. Accepts 0 <= x <= 7. LEDs unchanged.')

    def disable_led(self, led_position):
        if led_position not in range(self.LED_COUNT_ROBOT):
            print(
                'invalid led position: '+ led_position + '. Accepts 0 <= x <= 7. LED stays ON.')

        self.__led[led_position].set(0)

    def enable_all_led(self):
        return super().enable_all_led()

    def disable_all_led(self):
        return super().disable_all_led()

    def enable_body_led(self):
        self.__led[8].set(1)

    def disable_body_led(self):
        self.__led[8].set(0)

    def enable_front_led(self):
        self.__led[9].set(1)

    def disable_front_led(self):
        self.__led[9].set(0)

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
        self.__ps = []
        for i in range(self.PROX_SENSORS_COUNT):
            self.__ps.append(self.__robot.getDevice(psNames[i]))
            self.__ps[i].enable(self.TIME_STEP)

    def disable_sensors(self):
        return super().disable_sensors()

    def get_prox(self):

        try:
            prox_values = [self.__ps[i].getValue()
                           for i in range(self.PROX_SENSORS_COUNT)]
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
            self.__gs = []
            for i in range(self.GROUND_SENSORS_COUNT):
                self.__gs.append(self.__robot.getDevice(gsNames[i]))
                self.__gs[i].enable(self.TIME_STEP)
        except Exception as e:
            print('Did you add the ground sensor extension ? \n'+str(e))

    def get_ground(self):
        try:
            ground_values = [self.__gs[i].getValue()
                             for i in range(self.GROUND_SENSORS_COUNT)]

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

    def init_camera(self, save_image_folder=None, camera_rate=1, size=(None,None)):
        
        if not save_image_folder:
            save_image_folder = './'

        self.__save_image_folder = save_image_folder
        self.camera.enable(self.TIME_STEP*camera_rate)
         
        if (self.__camera_width,self.__camera_height) != (self.camera.getWidth(), self.camera.getHeight()):
            self.__camera_width = self.camera.getWidth()
            self.__camera_height = self.camera.getHeight()
            print('Camera size adjusted (width,height) : (' +str(self.__camera_width) +','+str(self.__camera_height)+')')

        
        width, height = size
        if width and height:
            print('Camera size must be configure in the e-puck Node')
            print('Camera (width,height) : ('+str(self.__camera_width) +','+str(self.__camera_height)+')')
            

    def disable_camera(self):
        self.camera.disable()


    def get_camera(self):
        red,green,blue = [],[],[]
        cameraData = self.camera.getImageArray()

        #print(len(cameraData[0]))
        # get the rgb of each pixel
        for n in range(self.__camera_width):
            for m in range(self.__camera_height):
                red.append(cameraData[n][m][0])
                green.append(cameraData[n][m][1])
                blue.append(cameraData[n][m][2])

    
        #resize 1dim to array of 2dim  
        red = np.array(red).reshape(self.__camera_height, self.__camera_width)
        green = np.array(green).reshape(self.__camera_height, self.__camera_width)
        blue = np.array(blue).reshape(self.__camera_height, self.__camera_width)
        
        return [red, green, blue]

    # https://www.cyberbotics.com/doc/reference/camera?tab-language=python
    def take_picture(self, filename = None):
        """
        Takes a picture and saves it in defined image folder from :py:meth:`init_camera<unifr_api_epuck.epuck_webots.WebotsEpuck.init_camera>`
        """
        try:
            if not filename:
                counter = '{:04d}'.format(self.counter_img)
                save_as = self.__save_image_folder+ '/'+self.get_id()+'_image'+ counter +  '.png'
                self.camera.saveImage(save_as,100)  # 100 for best quality
                self.counter_img += 1
            else:
                self.camera.saveImage(self.__save_image_folder+'/'+filename +'.png',100)

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
                save_as = self.__save_image_folder + '/'+ self.get_id() +'_image_video.png'
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
    def init_webots_communication(self):
        """
            Call this method to use Webots specific communication
        """
        #if host_id == self.get_id():
        #   Thread(target=hec.main, args=(host_ip,)).start()"""
        self.emitter = self.__robot.getDevice('emitter')
        self.receiver = self.__robot.getDevice('receiver')
        self.emitter.setChannel(1)
        self.receiver.setChannel(1)
        self.receiver.enable(self.TIME_STEP)

    def init_client_communication(self, host_ip='localhost'):
        """

        *   If you called the init_webots_communication(), then the e-puck will connect to the specific Webots 
            communication.

        *   If you do not call the init_webots_communication(), then the robot will try to find 
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