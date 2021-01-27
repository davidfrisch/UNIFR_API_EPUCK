from multiprocessing.managers import SyncManager
import socket
import time
from .api_epuck import *
from math import sqrt, atan2, pi
##########################################
##          CONSTANTS FOR Epucks        ##
#########################################

# Equivalent constants for Webots and Real Robots.
TIME_STEP = 64

MAX_SPEED_WEBOTS = 7.536
MAX_SPEED_IRL = 800

NBR_CALIB = 50

LED_COUNT_ROBOT = 8

OFFSET_CALIB = 5

CAMERA_WIDTH = 160
CAMERA_HEIGHT = 120

PROX_SENSORS_COUNT = 8
PROX_RIGHT_FRONT = 0
PROX_RIGHT_FRONT_DIAG = 1
PROX_RIGHT_SIDE = 2
PROX_RIGHT_BACK = 3
PROX_LEFT_BACK = 4
PROX_LEFT_SIDE = 5
PROX_LEFT_FRONT_DIAG = 6
PROX_LEFT_FRONT = 7

GROUND_SENSORS_COUNT = 3
GS_LEFT = 0
GS_CENTER = 1
GS_RIGHT = 2

MAX_MESSAGE = 30

######################
## CONSTANTS FOR Real Robot ##
######################
# For TCP communication
COMMAND_PACKET_SIZE = 21
HEADER_PACKET_SIZE = 1
SENSORS_PACKET_SIZE = 104
IMAGE_PACKET_SIZE = 160 * 120 * 2  # Max buffer size = widthxheightx2
MAX_NUM_CONN_TRIALS = 5
SENS_THRESHOLD = 250
TCP_PORT = 1000  # This is fixed.

SyncManager.register("syncdict")
SyncManager.register("lock")
SyncManager.register("shutdown")


class Epuck:
    """
    .. note:: variables available to call for real robot and Webots Epucks
    :var ip_addr: str - 
        the private ip address of the robot
    :var ps: array of int - 
        for storing the values of the infra-red sensors 
    :var ps_err: array of int - 
        denoise the infra-red values
    :var ls: array of int - 
        for storing the values of the light sensors
    :var ls_err: array of int - 
        denoise the light values
    :var gs: array of int - 
        for storing the ground sensors values
    :var red: array of red values of the camera from the robot
    :var green: array of green values of the camera from the robot
    :var blue: array of blue value in the camera from the robot
    :var counter_img: number of picture taken from the robot (GUI counter and internal robot counter is different !)
    """

    def __init__(self, ip_addr):
        """
        Initiate the robot
        :param ip_addr: str - The IP address of the real Epuck
        """
        self.host = None
        self.manager = None

        # var for identification
        self.ip_addr = ip_addr

        # proximity sensors init
        self.ps = []
        self.ps_err = []
        # light sensors init
        self.ls = []
        self.ls_err = []

        # ground sensors init
        self.gs = []

        # pixel RGB in a picture of the EPUCK
        self.red = []
        self.green = []
        self.blue = []

        # var for camera
        self.has_start_stream = False
        self.start_time = 0
        self.counter_img = 0

    def before_jpy_cell(self):
        """
        First method to call in every jupyter notebook cell.
        """
        pass

    def after_jpy_cell(self):
        """
        Last method to call in every jupyter notebook cell.
        """
        pass


    def get_id(self):
        """
        :returns:   On Webots : The id of the robot 
                    On Real Robot : The ip address (replace the dots with underscores e.g: 192_168_x_x)
        """
        pass

    def get_ip(self):
        """
        same as get_id()
        :returns:   On Webots : The host name of the computer
                    On Real Robot : The ip address
        """
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
            Then, if you would like to finish this infinite loop, `break` inside.
        In Webots:
            Simulate next frame
        Real Robot:
            Send and receive commands between computer and robot.
        :returns: True (Real Robot: if no problem occured)
        """

    def get_battery_level(self):
        """Get battery level"""
        return -1


    def set_speed(self, speed_left, speed_right=None):
        """Set speed of the robot motors. 
        :param speed_left: int
            left motor speed 
        :param speed_right: int, optional
            right motor speed, (default is speed_left)
        .. note:: 
            Speed: must be between -6.9 and 6.9
        """
        pass

    def get_speed(self):
        """Get speed of the motors
        :returns: [left_wheel, right_wheel]
        :rtype: [int, int]
        """
        pass

    def bounded_speed(self, speed):
        """
        Bounds the motor speeds of the robot in case if the user put an excessive value.
        :param speed: speed of a wheel of the Epuck
        """
       
        if speed > MAX_SPEED_WEBOTS:
            return MAX_SPEED_WEBOTS
        elif speed < -MAX_SPEED_WEBOTS:
            return -MAX_SPEED_WEBOTS

        return speed

    def get_motors_steps(self):
        """ 
        Get the number of steps since the beggining of the process. 
        .. warning:: Only works with real robots
        .. hint:: 1000 steps are 1 revolution (1 full turn of the wheel)
        :returns: [left_wheel, right_wheel]
        :rtype: [int, int]
        """
        pass

    def toggle_led(self, led_position, red=None, green=None, blue=None):
        """ Turn on led at led_position
        :param led_position: int
            value between 0 and 7
        .. important:: 
            * Only LED 1,3,5 and 7 are RGB
            * the three color must be specify to use rgb
        :param red: int - red intensity (value between 0 and 100)
        :param green: int - green intensity (value between 0 and 100)
        :param blue: int - blue intensity (value between 0 and 100)
        """
        pass

    def disable_led(self, led_position):
        """ Turn off led at led_position
        :param led_position: int - (value between 0 and 7)
        """
        pass

    def toggle_all_led(self):
        """Turn on all LED aroud the robot"""
        for i in range(LED_COUNT_ROBOT):
            self.toggle_led(i)

    def disable_all_led(self):
        """Turn off all LED aroud the robot"""
        for i in range(LED_COUNT_ROBOT):
            self.disable_led(i)

    def enable_body_led(self):
        """Turn on green body light of the robot"""
        pass

    def disable_body_led(self):
        """Turn off green body light of the robot"""
        pass

    def enable_front_led(self):
        """Turn on red front light of the robot"""
        pass

    def disable_front_led(self):
        """Turn off red front light of the robot"""
        pass

    ##### END ####
    #    LED     #
    ##############

    def init_sensors(self):
        """
        Start sensors of the robot
        """
        pass

    def disable_sensors(self):
        """
        Disable sensors of the robot
        """
        pass

    def get_prox(self):
        """Get proximity sensors values of the robot
        .. note::
            IR proximity: between 0 (no objects detected) and 4095 (object near the sensor)
        .. hint::
            **Array position**
            0. prox right front 
            1. prox right front diagonale
            2. prox right side 
            3. prox right back 
            4. prox left back 
            5. prox left side 
            6. prox left front diagonale 
            7. prox left front 
        :returns: the proximities values 
        :rtype: int array - (length 8) 
        """
        pass

    def calibrate_prox(self):
        """
        .. warning:: Only works with real robots
        Clean the default values of the infra-red proximitors when robot has no obstacles near it. (take off "noise")  
        Robot is calibrating when all its LEDs are ON.
        """
        # init array for calibration values
        self.ps_err = [0 for _ in range(PROX_SENSORS_COUNT)]

        print(self.get_id() + ' start calibrating IR proximity')

        # toggle light as witness
        self.toggle_all_led()

        # get multiple readings for each sensor
        for i in range(NBR_CALIB + OFFSET_CALIB):
            self.go_on()
            if i > OFFSET_CALIB:
                tmp = self.get_prox()
                for j in range(PROX_SENSORS_COUNT):
                    self.ps_err[j] += tmp[j]

        # calculate the average for each sensor
        for i in range(PROX_SENSORS_COUNT):
            self.ps_err[i] /= NBR_CALIB

        print(self.get_id() + ' finish calibrating IR proximity')

        self.disable_all_led()

    def get_calibrate_prox(self):
        """
        .. warning:: Only works with real robots
        Get the array prox values without the noise of the proximitors
        .. note:: IR proximity: between 0 (no objects detected) and 4095 (object near the sensor)
        .. hint::
            **Array proximites positions**
            0. prox right front 
            1. prox right front diagonale
            2. prox right side 
            3. prox right back 
            4. prox left back 
            5. prox left side 
            6. prox left front diagonale 
            7. prox left front 
        :returns:  The corrected proximities values 
        :rtype: int array - (length 8)
        """
        prox_vals = self.get_prox()
        prox_corr = [0]*PROX_SENSORS_COUNT

        for i in range(PROX_SENSORS_COUNT):
            if prox_vals[i] - self.ps_err[i] < 0:
                prox_corr[i] = 0
            else:
                prox_corr[i] = prox_vals[i] - self.ps_err[i]

        return prox_corr

    def init_ground(self):
        """
        Initiates the ground sensors of the robot.
        .. note::
            On Webots, you must add ➕ the exentension node name 'E-puckGroundSensors (Transform)' to the robot otherwise it will not work.
        .. image:: res/addGroundSensors.png
            :width: 400
            :alt: Picture of the main GUI Epuck
        """
        pass

    def get_ground(self):
        """Get the values of the ground sensors
        .. note:: 
            Between 0 (no surface at all or not reflective surface e.g. black) and 1023 (very reflective surface e.g. white)
        .. hint:: 
            **Array positions**
            0. LEFT
            1. MIDDLE
            2. RIGHT
        :returns: int array of the ground values 
        :rtype: int array - [LEFT,MIDDLE,RIGHT]
        """
        pass

    def get_gyro_axes(self):
        """Get gyroscope values (axis x, y and z)
        :return int: [x, y, z]
        :rtype: [int, int, int]
        """
        pass

    def get_acceleration(self):
        """
        Get the accelerometer value
        .. note:: acceleration magnitude, between 0.0 and about 2600.0 (~3.46 g)
        :returns: value of the accelerometer 
        :rtype: int
        """
        pass

    def get_accelerometer_axes(self):
        """
        Get the accelerometer axis values
        :returns: [x,y,z]
        :rtype: array of int
        """
        pass

    # https://stackoverflow.com/questions/3755059/3d-accelerometer-calculate-the-orientation
    # definition of roll and pitch https://www.youtube.com/watch?v=5IkPWZjUQlw
    def get_roll(self):
        """
        Get roll degree
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
        Get pitch degree
        .. note:: Inclination between 0.0 and 90.0 degrees (when tilted in any direction)
        :returns: pitch axis degree 
        :rtype: float
        """
        accelX, accelY, accelZ = self.get_accelerometer_axes()
        return 180 * atan2(accelY, sqrt(accelX*accelX + accelZ*accelZ))/ pi


    def get_temperature(self):
        """
        Returns temperature of robot in degree Celsius
        :returns: temperature
        :rtype: int (degree Celcius)
        """
        pass

    def init_tof():
        """
            Must be called if you're using the PiPuck.
            It will not affect other Epucks variant.
        """
        pass

    def get_tof(self):
        """
        Get the Time Of Flight value
        .. caution:: The TOF sensor can physically have different orientation depending of the robot.
        :returns: values in millimiters
        :rtype: int
        """
        pass

    def disable_tof(self):
        """
        Stop computing with the TOF sensor.
        It will not affect other Epucks variant
        """
        pass


    def __rgb565_to_bgr888(self):
        """
        Convert rgb555 to bgr888
        Credits : http://projects.gctronic.com/epuck2/getimage.py
        """
        pass

    def __save_bmp_image(self, filename):
        """
        .. warning:: Only works with real robots
        The bmp image save as the filename in the computer
        :param filename: str - filename where to save the images
        """
        pass

    def init_camera(self, save_image_folder=None, camera_rate=1):
        """
        Enable camera of the robot
        :param save_image_folder: insert directory folder to save the image taken by the camera of the robot.
        :param camera_rate: camera_rate
        """
        pass

    def disable_camera(self):
        """Disable camera of the robot"""
        pass

    def get_camera(self):
        """
        Process raw image from robot
        .. tip:: when you combine the colors of a specific position of the three color arrays, it gives you the value of the pixel
        :return arrays: [red],[green],[blue]
        """
        pass

    def take_picture(self):
        """
        Take a picture and save it 
        """
        pass

    def live_camera(self, live_time=None):
        """
        .. warning:: Only works with real robots
        Live camera from the embedded camera of the robot
        The live_camera need to be refresh at each step
            .. attention::
                Requires :
                    * PIL 'pip install Pillow'
            :param live_time: int - Lifetime of the stream. (default: until program ends)
        """
        pass

    def live_camera_webots(self, live_time=None):
        """
        .. warning:: Only works with Webots simulation
        .. note:: Only call this method if you prefer to stream from the provided GUI instead of Webots.
        """
        pass

    # return front, right, back. left microphones
    def get_microphones(self):
        """
        .. warning:: Only works with real robots
        Get microphones intensity 
        .. note:: Mic volume: between 0 and 4095
        :returns: [front, right, back, left]
        :rtype: array of int
        """
        pass

    def play_sound(self, sound_number):
        """
        .. warning:: Only works with real robots
        Plays correspond music of the sound_number
        0. Play Main Mario Theme
        1. Play Underworld Mario Theme
        2. Play Star Wars Theme
        :param sound_number: int - (between 0 and 2)
        """
        switcher = {
            1: self.play_mario,
            2: self.play_underworld,
            3: self.play_star_wars
        }

        func = switcher.get(sound_number, self.stop_sound)
        func()

    def play_mario(self):
        """
        .. warning:: Only works with real robots
        Plays mario music from the robot
        """
        pass

    def play_underworld(self):
        """
        .. warning:: Only works with real robots
        Plays underworld music from the robot
        """
        pass

    def play_star_wars(self):
        """
        .. warning:: Only works with real robots
        Plays Star Wars music from the robot
        """
        pass

    def stop_sound(self):
        """
        .. warning:: Only works with real robots
        Stop music from the robot
        """
        pass

    #################
    # COMMUNICATION #
    #################
    def init_host_communication(host_ip='localhost'):
        """
        .. attention:: If host_ip is not defined, you must first `run python -m unifr_api_epuck` before launching the robots.
        Initiate the communication between host and robots.
        """
        pass

    def init_client_communication(self, host_ip='localhost'):
        """
        .. attention:: init_host_communication should be called or the GUI has to be called before connecting the client.
        """
       
        is_online = 1

        time_fail = time.time() + 10
        while is_online != 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            is_online = sock.connect_ex((host_ip, 50000))
            if time_fail < time.time():
                print('No communication for ' + self.get_id() +
                        '. Not connected to host manager.')
                if not host_ip:
                    print(
                        'Please create a GUI host by executing on your terminal: `python3 -m unifr_api_epuck`')

                # exit method
                return

        # connecting to host manager
        is_connect = False
        while not is_connect:
            try:
                # connect to host ip
                self.manager = SyncManager((host_ip, 50000), authkey=b"abc")
                self.manager.connect()
                print('CONNECT to host IP!')
                is_connect = True

                # get shared dictionnary of host
                self.lock = self.manager.lock()
                self.syncdict = self. manager.syncdict()

                self.lock.acquire(timeout=1)
                # adding its own id in the dictionnary and life points 
                tmp_dict = self.syncdict.copy()
                tmp_dict[self.get_id()] = []
                tmp_dict['connected'][self.get_id()] = 100
                
                self.syncdict.update(tmp_dict)
                self.lock.release()

            except Exception as e:
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')
                self.manager = None

    def __stay_alive(self):
        """
            Keep the host aware that the epuck is alive
        """
        if self.manager:
            try:
                self.lock.acquire(timeout=1)
                # must make a copy to get value from key
                current_dict = self.syncdict.copy()
                current_dict['connected'][self.get_id()] += 1
                
                self.syncdict.update(current_dict)
                self.lock.release()
                
            except Exception as e:
                self.manager = None
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')



    def send_msg(self, msg):
        """
            Put a message to each queue of other robots.
            :param msg: any - Message to send
        """
        # strictly subjective value to avoid overload
        if self.manager:
            try:
                self.lock.acquire(timeout=1)
                # we can only iterate on a copy
                current_dict = self.syncdict.copy()
                for epuck, epuck_mailbox in current_dict.items():

                    if epuck != self.get_id() and epuck != 'connected':

                        if len(epuck_mailbox) < MAX_MESSAGE:
                            epuck_mailbox.append(msg)

                        # update the dictionnary
                        current_dict.update({epuck: epuck_mailbox})

                self.syncdict.update(current_dict)
                self.lock.release()

            except Exception as e:
                self.manager = None
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


    def has_receive_msg(self):
        self.__stay_alive()
        """
        :returns: True if the robot has pending messages in his queue.
        """
        if self.manager:
            try:
                self.lock.acquire(timeout=1)

                # must make a copy if we want to acces via key
                current_dict = self.syncdict.copy()
                epuck_array = current_dict[self.get_id()]

                # Check if array is empty
                has_msg = len(epuck_array) > 0
                self.lock.release()

                return has_msg

            except Exception as e:
                self.manager = None
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


    def receive_msg(self):
        """
        Get next message of the robot queue
        :returns recv_mess: anytype - msg
        """
        self.__stay_alive()
        if self.manager:
            try:
                if self.has_receive_msg():
                    self.lock.acquire(timeout=1)
                    # must make a copy to get value from key
                    current_dict = self.syncdict.copy()
                    recv_mess = current_dict[self.get_id()].pop(0)
                    self.syncdict.update(
                        {self.get_id(): current_dict[self.get_id()]})
                    self.lock.release()
                    return recv_mess
         
            except Exception as e:
                self.manager = None
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


        return None
