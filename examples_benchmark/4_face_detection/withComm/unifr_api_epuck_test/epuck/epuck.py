from ..communication.client_communication import ClientCommunication
from multiprocessing.managers import SyncManager
import socket
import time
from math import sqrt, atan2, pi
import numpy as np
import sys

SyncManager.register("syncdict")
SyncManager.register("lock")


class Epuck:
    """

    .. note:: These are variables properties to call 

    :var ip_addr: str - 
        the private ip address of the robot
    :var ps_err: array of int - 
        denoise the infra-red values
    :var ls_err: array of int - 
        denoise the light values
    :var red: array of red values of the camera from the robot
    :var green: array of green values of the camera from the robot
    :var blue: array of blue value in the camera from the robot
    :var counter_img: number of picture taken from the robot (GUI counter and internal robot counter is different !)
    """

    def __init__(self, ip_addr):
        """
        Initiates the robot

        :param ip_addr: str - The IP address of the real Epuck
        """
        
        # Equivalent constants for Webots and Real Robots.
        self.MAX_SPEED = 7.536
        self.MAX_SPEED_IRL = 800
        self.LED_COUNT_ROBOT = 8

        self.NBR_CALIB = 50
        self.OFFSET_CALIB = 5

        self.host = None
        self.manager = None
        self.ClientComunication = None

        # var for identification
        self.ip_addr = ip_addr
        if ip_addr:
            self.id = ip_addr.replace('.', '_')
        else:
            self.id = 'pi-puck'


        # proximity sensors init
        self.PROX_SENSORS_COUNT = 8
        self.PROX_RIGHT_FRONT = 0
        self.PROX_RIGHT_FRONT_DIAG = 1
        self.PROX_RIGHT_SIDE = 2
        self.PROX_RIGHT_BACK = 3
        self.PROX_LEFT_BACK = 4
        self.PROX_LEFT_SIDE = 5
        self.PROX_LEFT_FRONT_DIAG = 6
        self.PROX_LEFT_FRONT = 7

        self.ps_err = []
        # light sensors init
        self.ls_err = []


        self.GROUND_SENSORS_COUNT = 3
        self.GS_LEFT = 0
        self.GS_CENTER = 1
        self.GS_RIGHT = 2

        self.MAX_MESSAGE = 30

        # pixel RGB in a picture of the EPUCK
        self.__camera_width = None
        self.__camera_height = None

        # var for camera
        self.has_start_stream = False
        self.start_time = 0
        self.counter_img = 0

    def get_id(self):
        pass

    def set_id(self, new_id):
        """
        Set new ID for the e-puck
        """
        self.id = new_id

    def get_ip(self):
        pass

    #############################
    ## COMMUNICATION METHODS   ##
    #############################
    def go_on(self):
        """
        .. important:: 
            Mandatory method.
            This method must be called before execution of next step of the robot.

        .. tip::
            Put it as a condition in a while loop.
            Then, if you would like to finish the infinite while loop, break inside.
        """
        try:
            if self.manager:
                self.__stay_alive()
        except:
            print('Error in go_on with host')
            

    def sleep(self, duration):
        """
        Pause the execution during *duration* seconds
        
        .. warning ::
            This implementation is to be preferred to the standard Python time.sleep() which can lead to problems in the sequence of event handling.

        :param duration: duration in seconds
        """

        time_finish = time.time()+duration
        while time.time() < time_finish:
            self.go_on()

    def get_battery_level(self):
        """
        Gets battery level
        """
        return -1

    def set_speed(self, speed_left, speed_right=None):
        """
        Sets the speed of the robot's motors
        
        :param speed_left: int
        :param speed_right: int, optional (default: is the same speed as speed_left)

        .. note:: 
            The speed of each wheel is already bounded between -7.536 and 7.536 

    
        """
        pass

    def get_speed(self):
        """
        Gets speed of the motors

        :returns: [left_wheel, right_wheel]
        :rtype: [int, int]
        """
        pass

    def bounded_speed(self, speed):
        """
        Limits the motor speed of the robot in case the user puts an excessive value

        :param speed: speed of a wheel of the e-puck
        """
       
        if speed > self.MAX_SPEED:
            return self.MAX_SPEED
        elif speed < -self.MAX_SPEED:
            return -self.MAX_SPEED

        return speed


    def enable_led(self, led_position, red=None, green=None, blue=None):
        """ 
        Turns ON led at led_position

        :param led_position: int
            value between 0 and 7 

        .. image:: ../res/leds_img.png
            :width: 300
            :alt: add the Node

        .. important:: 
            * Only LEDs at position 1,3,5 and 7 are RGB
            * the three colours must be specified to use RGB

        :param red: int - red intensity value is between 0 (low) and 100 (high)
        :param green: int - green intensity value is between 0 (low) and 100 (high)
        :param blue: int - blue intensity value is between 0 (low) and 100 (high)
        """
        pass

    def disable_led(self, led_position):
        """ 
        Turns OFF led at led_position

        :param led_position: int - (value between 0 and 7)
        """
        pass

    def enable_all_led(self):
        """
        Turns ON all LED lights
        """
        for i in range(self.LED_COUNT_ROBOT):
            self.enable_led(i)

    def disable_all_led(self):
        """
        Turns OFF all LED lights
        """
        for i in range(self.LED_COUNT_ROBOT):
            self.disable_led(i)

    def enable_body_led(self):
        """
        Turns ON green body light
        """
        pass

    def disable_body_led(self):
        """
        Turns OFF green body light
        """
        pass

    def enable_front_led(self):
        """
        Turns ON red front light
        """
        pass

    def disable_front_led(self):
        """
        Turns OFF red front light
        """
        pass

    ##### END ####
    #    LED     #
    ##############

    def init_sensors(self):
        """
        Starts the robot's sensors 
        """
        pass

    def disable_sensors(self):
        """
        Disables the robot's sensors 
        """
        pass

    def get_prox(self):
        """
        Gets the robot's proximity sensor raw values

        .. note::
            IR proximity: between 0 (no objects detected) and 4095 (object near the sensor)

        .. hint::
            **Array position**

            0. prox right front 
            1. prox right front diagonal
            2. prox right side 
            3. prox right back 
            4. prox left back 
            5. prox left side 
            6. prox left front diagonal 
            7. prox left front 

        :returns: the proximity sensor values 
        :rtype: int array - (length 8) 
        """
        pass

    def calibrate_prox(self):
        """
        Adjust the sensors to make them as error free as possible

        .. note::
            When all LEDs are ON, it indicates that the sensors are calibrating.
        """
        print(self.get_id() + ' start calibrating IR proximity')

        # enable light as witness
        self.enable_all_led()
        
        for _ in range(10):
            self.go_on()

        sums_per_sensor = np.array([0]*self.PROX_SENSORS_COUNT)
        # get multiple readings for each sensor
        for i in range(self.NBR_CALIB + self.OFFSET_CALIB):
            self.go_on()
            if i > self.OFFSET_CALIB:
                tmp = self.get_prox()
                sums_per_sensor = sums_per_sensor+tmp
               
        # calculate the average for each sensor
        self.ps_err = sums_per_sensor/self.NBR_CALIB

        
        self.disable_all_led()
        for _ in range(10):
            self.go_on()

        print(self.get_id() + ' finish calibrating IR proximity')


    def get_calibrate_prox(self):
        """
        Gets the calibrated proximity sensor values

        .. note:: IR proximity: between 0 (no objects detected) and 4095 (object near the sensor)

        .. hint::
            **Array proximites positions**

            0. prox right front 
            1. prox right front diagonal
            2. prox right side 
            3. prox right back 
            4. prox left back 
            5. prox left side 
            6. prox left front diagonal 
            7. prox left front 

        :returns: proximity values 
        :rtype: [int] - (length 8)
        """
        prox_vals = self.get_prox()
        prox_corr = [0]*self.PROX_SENSORS_COUNT

        for i in range(self.PROX_SENSORS_COUNT):
            if prox_vals[i] - self.ps_err[i] < 0:
                prox_corr[i] = 0
            else:
                prox_corr[i] = prox_vals[i] - self.ps_err[i]

        return prox_corr

    def init_ground(self):
        """
        Initiates the ground sensors of the robot
        """
        pass

    def get_ground(self):
        """
        Gets the values from the ground sensors

        .. note:: 
            Between 0 (no surface at all or not reflective surface e.g. black) and 1023 (very reflective surface e.g. white)
        
        .. hint:: 
            **Array positions**

            0. LEFT
            1. MIDDLE
            2. RIGHT

        :returns: ground values 
        :rtype: [int] - [LEFT, MIDDLE, RIGHT]
        """
        pass

    def get_gyro_axes(self):
        """
        Gets gyroscope values (axis x, y and z)

        :return: [x, y, z]
        :rtype: [int, int, int]
        """
        pass

    def get_acceleration(self):
        """
        Gets the magnitude of the acceleration vector, whose direction angles are provided by 
        the :py:meth:`get_pitch()<.get_pitch>` 
        and :py:meth:`get_roll()<.get_roll>`  functions 

        .. note:: acceleration magnitude, between 0.0 and about 2600.0 (~3.46 g)

        :returns: value of the accelerometer 
        :rtype: int
        """
        pass

    def get_accelerometer_axes(self):
        """
        Gets the accelerometer axis raw values.

        :returns: [x,y,z]
        :rtype: array of int
        """
        pass

    # https://stackoverflow.com/questions/3755059/3d-accelerometer-calculate-the-orientation
    # definition of roll and pitch https://www.youtube.com/watch?v=5IkPWZjUQlw
    def get_roll(self):
        """
        Gets roll degree reading.

        .. note:: Orientation between 0.0 and 360.0 degrees

        :returns: roll axis degree 
        :rtype: float
        """
        accelX, accelY, accelZ = self.get_accelerometer_axes()
        return 180 * atan2(accelX, sqrt(accelY*accelY + accelZ*accelZ))/ pi


    # https://engineering.stackexchange.com/questions/3348/calculating-pitch-yaw-and-roll-from-mag-acc-and-gyro-data
    # definitions of roll and pitch https://www.youtube.com/watch?v=5IkPWZjUQlw
    def get_pitch(self):
        """
        Gets pitch angle reading.

        .. note:: Inclination between 0.0 and 90.0 degrees (when tilted in any direction)

        :returns: pitch axis degree 
        :rtype: float
        """
        accelX, accelY, accelZ = self.get_accelerometer_axes()
        return 180 * atan2(accelY, sqrt(accelX*accelX + accelZ*accelZ))/ pi


    def get_temperature(self):
        pass

    def init_tof():
        """
        Initiates Time Of Flight sensor
        """
        pass

    def get_tof(self):
        """
        Gets the Time Of Flight value

        .. warning:: 
            The TOF sensor can have different orientations on the robot which will affect measurement.
        
        :returns: values in millimetres
        :rtype: int
        """
        pass

    def disable_tof(self):
        """
        Stops the TOF sensor
        """
        pass


    def init_camera(self, save_image_folder=None, filename=None, camera_rate=1, size=(None,None)):
        """
        Enables the robot's camera 

        :param save_image_folder: input directory folder to save the images taken by the robot
        :param camera_rate: camera_rate
        """
        pass

    def disable_camera(self):
        """
        Disables the robot's camera
        """
        pass

    def get_camera(self):
        """
        Gets raw images from robot

        .. note::
            More information in Examples/camera

        
        :return arrays: [[red],[green],[blue]]
        """
        pass

    def get_camera_width(self):
        return self.__camera_width

    def get_camera_height(self):
        return self.__camera_height

    def take_picture(self):
        pass

    def live_camera(self, duration=None):
        """
        Lets you stream from the GUI

        The live_camera method need to be called at each step.

        :param duration: int - duration of the stream. (default: until program ends)
        """
        pass


    # return front, right, back. left microphones
    def get_microphones(self):
        """
        .. warning:: 
            Only works with real robots
        """
        pass

    

    
    #################
    # COMMUNICATION #
    #################
    def init_client_communication(self, host_ip='localhost'):
        """
        .. warning:: The host should be created first before calling this method. (ref. Examples/Communication)
        """
        self.ClientComunication = ClientCommunication(self.id)
        self.ClientComunication.init_client_communication(host_ip)


    def __stay_alive(self):
        """
        Keeps the host aware that the epuck is alive
        """
        self.ClientComunication.stay_alive()

    def send_msg(self, msg):
        """
        Puts a message in queue to other robots

        :param msg: any 
        """
        self.ClientComunication.send_msg(msg)

    def has_receive_msg(self):
        """
        :returns: True if the robot has pending messages in his queue otherwise False.
        """
        return self.ClientComunication.has_receive_msg()

    def receive_msg(self):
        """
        Get next message from the robot queue otherwise returns None.
        """
        return self.ClientComunication.receive_msg()

    def get_connected_epucks(self):
        """
        Get list of connected epucks to the host.

        :returns: array of connected epucks
        """
        #method from host_epuck_communication
        return self.ClientComunication.get_available_epucks()

    def clean_msg(self):
        self.ClientComunication.clean_msg()
        
    def clean_up():
        pass