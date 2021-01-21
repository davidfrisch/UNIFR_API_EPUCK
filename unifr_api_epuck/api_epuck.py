import socket
import logging
import struct
import time
import sys
from math import atan2, sqrt, pi, sin, cos
from . import host_epuck_communication as hec
from multiprocessing.managers import SyncManager
from multiprocessing import Process


##########################################
## CONSTANTS FOR WEBOTS AND Real Robot  ##
#########################################

# Equivalent constants for Webots and Real Robots.
TIME_STEP = 64

MAX_SPEED = 6.9
NBR_CALIB = 50

LED_COUNT = 8

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


def get_robot(ip_addr=None):
    """
    Get EPUCK instance
    :params ip_addr: ip address of the EPUCK.

    :returns: instance of the EPUCK
    """
    if(ip_addr != None):
        return __get_robot_direct(ip_addr)

    return __get_robot_webot()


def __get_robot_direct(ip_addr):
    "Return an Real Robot Epuck instance"
    print('starting connection with ' + str(ip_addr))

    return __DirectEpuck(ip_addr)


def __get_robot_webot():
    """
    Return a simulation Epuck instance
    """
    try:
        return __WebotsEpuck()

    except ModuleNotFoundError:
        print(
            '\033[91m'+'You did not enter an IP address, Please launch the script from Webots.'+'\033[0m')


def robot_setup(ip_addr=None, main_loop=None):
    """
    configure the robot before launching it.

    :params ip_addr: ip address of the EPUCK.
    :params main_loop: Robot code instructions during execution.

    .. note:: Leave empty the main_loop if you will be using a jupyter notebook.
    """

    if not main_loop and ip_addr:
        rob = get_robot(ip_addr)
        return rob

    if ip_addr:
        rob = get_robot(ip_addr)
        main_loop(rob)

    elif main_loop:
        rob = get_robot()
        main_loop(rob)

    else:
        print('No instance of robot created.')


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

    def __tcp_init(self):
        """
            Initiate the TCP communication between the robot and host computer.

            prints "connected to x.x.x.x" once connection succeed

            :raises socket.timeout:
                (4) this exception is raised when a timeout occurs on a socket

            :raises socket.OSError:
                This exception is raised when a system function returns a system-related error Exception

        """
        pass

    def __init_command(self):
        """
        Initial command packet that is send to the Epuck once the first connection succeeded.
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

    def __send_to_robot(self):
        """Send a new packet from the computer to the robot"""
        pass

    def __receive_from_robot(self, msg_len):
        """Receive a new packet from the robot to the computer"""
        pass

    def __receive_from_robot(self):
        """Receive the packet from the robot

        :returns: True if no problem occured
        """
        pass

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

    def __set_speed_left(self, speed_left):
        """
        Set speed of the left motor of the robot

        .. note: Only works with real robots 

        :param speed_left: left wheel speed
        """
        pass

    def __set_speed_right(self, speed_right):
        """
        .. note: Only works with real robots

        Set speed of the right motor of the robot

        :param speed_right: right wheel speed
        """
        pass

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
        if speed > MAX_SPEED:
            return MAX_SPEED
        elif speed < -MAX_SPEED:
            return -MAX_SPEED
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
        for i in range(LED_COUNT):
            self.toggle_led(i)

    def disable_all_led(self):
        """Turn off all LED aroud the robot"""
        for i in range(LED_COUNT):
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

    ######### START #######
    #    AMBIENT LIGHT    #
    #######################
    def init_lights(self):
        """
            .. note:: Specific to Webots

            This will not affect Real Robot code but it is only useful to initiate lights on Webots.
        """
        pass

    def get_lights(self):
        """Get the lights intensity surrounding the robot

        .. note:: IR ambient: between 0 (strong light) and 4095 (dark)

        :returns: The light sensors values 
        :rtype: int array - (length 8)
        """
        pass

    def __calibrate_lights(self):
        """
        .. warning:: Only works with real robots

        Clean the default values of the light proximitors when robot 
             is in ambient light. (take off "noise")  

             Robot is calibrating when all its LEDs are ON.
        """
        pass

    def get_lights_calibrated(self):
        """
        .. warning:: Only works with real robots

        Get the array lights values without the noise of the lights

        .. note:: 
            IR ambient: between 0 (strong light) and 4095 (dark)

        :returns:  The corrected lights values 
        :rtype: int array - (length 8)
        """
        pass

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

    def get_tof(self):
        """
        Get the Time Of Flight value

        .. caution:: The TOF sensor can physically have different orientation depending of the robot.

        :returns: values in millimiters
        :rtype: int
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
        pass

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

    def init_communication(self, host_ip='localhost'):
        """

        .. attention:: If host_creator is not defined, you must first `run python -m unifr_api_epuck` before launching the robots.

        Initiate the communication between host and robots.
        """
        # Firstly it creates host from host_creator (if host_creator specified to an e-puck)
        # Secondly robot connects to host

        # creating host manager
        if self.get_ip() == host_ip:
            try:
                print('    starting server', end=" "),

                Process(target=hec.start_manager, args=(host_ip,)).start()

            except Exception as e:
                print(e)

        else:
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

                # adding its own id in the dictionnary
                self.lock.acquire()
                self.syncdict.update({self.get_id(): []})
                self.lock.release()

            except:
                pass

    def send_msg(self, msg):
        """
            Put a message to each queue of other robots.

            :param msg: any - Message to send

        """
        # strictly subjective value to avoid overload

        if self.manager:
            try:
                self.lock.acquire()
                # we can only iterate on a copy
                current_dict = self.syncdict.copy()
                for epuck_value in current_dict:

                    if epuck_value != self.get_id():
                        current_array = current_dict[epuck_value]

                        if len(current_array) < MAX_MESSAGE:
                            current_array.append(msg)

                        # update the dictionnary
                        current_dict.update({epuck_value: current_array})

                self.syncdict.update(current_dict)
                self.lock.release()

            except AttributeError as e:
                print(e)

            except Exception as e:
                print(e)

    def has_receive_msg(self):
        """
        :returns: True if the robot has pending messages in his queue.
        """
        if self.manager:
            try:
                self.lock.acquire()

                # must make a copy if we want to acces via key
                current_dict = self.syncdict.copy()
                epuck_array = current_dict[self.get_id()]

                # Check if array is empty
                has_msg = len(epuck_array) > 0
                self.lock.release()

                return has_msg

            except AttributeError as e:
                print('No communication with host manager messages')

            except Exception as e:
                print(e)

    def receive_msg(self):
        """

        Get next message of the robot queue

        :returns recv_mess: anytype - msg

        """
        if self.manager:
            try:
                if self.has_receive_msg():
                    self.lock.acquire()
                    # must make a copy to get value from key
                    current_dict = self.syncdict.copy()
                    recv_mess = current_dict[self.get_id()].pop(0)
                    self.syncdict.update(
                        {self.get_id(): current_dict[self.get_id()]})
                    self.lock.release()
                    return recv_mess
            except AttributeError:
                print('No communication with host manager messages')

            except Exception as e:
                print(e)

        return None


class __DirectEpuck(Epuck):

    def __init__(self, ip_addr):

        super().__init__(ip_addr)
        """
        A class used to represent a robot Real Robot.

        :param ip_addr: str - The IP address of the Epuck
        """
        # communication Robot <-> Computer
        self.sock = 0
        self.header = bytearray([0] * 1)
        self.command = bytearray([0] * COMMAND_PACKET_SIZE)

        # camera init specific for Real Robot
        self.camera_width = CAMERA_WIDTH
        self.camera_height = CAMERA_HEIGHT
        self.rgb565 = [0 for _ in range(IMAGE_PACKET_SIZE)]
        self.bgr888 = bytearray([0] * 115200)  # 160x120x3x2
        self.camera_updated = False
        self.my_filename_current_image = ''


        # start communication with computer
        self.__tcp_init()
        self.__init_command()

    def before_jpy_cell(self):
        self.__tcp_init()
        self.go_on()

    def after_jpy_cell(self):
        self.go_on()

    def __tcp_init(self):
        trials = 0
        ip_address = self.ip_addr
        print("Try to connect to " + ip_address +
              ":" + str(TCP_PORT) + " (TCP)")
        while trials < MAX_NUM_CONN_TRIALS:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(10)  # non-blocking socket
            try:
                self.sock.connect((ip_address, TCP_PORT))
            except socket.timeout as err:
                self.sock.close()
                logging.error("Error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            except socket.OSError as err:
                self.sock.close()
                logging.error("Error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            except Exception as err:
                self.sock.close()
                logging.error("Error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            break

        if trials == MAX_NUM_CONN_TRIALS:
            print("Can't connect to " + ip_address)
            return

        print("Connected to " + ip_address)
        print("\r\n")

    def __init_command(self):
        # Init the array containing the commands to be sent to the robot.
        self.command[0] = 0x80  # Packet id for settings actuators
        self.command[1] = 2  # Request: only sensors enabled
        self.command[2] = 0  # Settings: set motors speed
        self.command[3] = 0  # left motor LSB
        self.command[4] = 0  # left motor MSB
        self.command[5] = 0  # right motor LSB
        self.command[6] = 0  # right motor MSB
        self.command[7] = 0  # lEDs
        self.command[8] = 0  # LED2 red
        self.command[9] = 0  # LED2 green
        self.command[10] = 0  # LED2 blue
        self.command[11] = 0  # LED4 red
        self.command[12] = 0  # LED4 green
        self.command[13] = 0  # LED4 blue
        self.command[14] = 0  # LED6 red
        self.command[15] = 0  # LED6 green
        self.command[16] = 0  # LED6 blue
        self.command[17] = 0  # LED8 red
        self.command[18] = 0  # LED8 green
        self.command[19] = 0  # LED8 blue
        self.command[20] = 0  # speaker

    def get_id(self):
        return self.get_ip().replace('.', '_')

    def get_ip(self):
        return self.ip_addr

    def init_sensors(self):
        self.command[1] = self.command[1] | (1 << 1)
        # start sensor calibration, with the intern calibration
        #self.command[2] = 1
        # calibrate on board
        self.command[2] = 0 

    def disable_sensors(self):
        # put the second bit to last at 0
        self.command[1] = self.command[1] & 0xFD

    #####################################################
    ## COMMUNICATION METHODS between robot and master  ##
    #####################################################

    def __send_to_robot(self):
        byte_send = 0

        # loop until all fragments of the packet has been sent
        while byte_send < COMMAND_PACKET_SIZE:
            sent = self.sock.send(self.command[byte_send:])
            if sent == 0:
                raise RuntimeError("Send error")

            byte_send = byte_send + sent

        # stop calibration
        self.command[2] = 0

    def __receive_part_from_robot(self, msg_len):
        # receiving data in fragments
        chunks = []
        bytes_recd = 0
        try:
            while bytes_recd < msg_len:
                chunk = self.sock.recv(min(msg_len - bytes_recd, 2048))
                if chunk == b'':
                    raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            return b''.join(chunks)
        except:
            print('\033[91m'+'Lost connection of : ' +
                  str(self.get_ip())+'\033[0m')
            sys.exit(1)

    def __receive_from_robot(self):

        # depending of the header, we know what data we receive
        header = self.__receive_part_from_robot(HEADER_PACKET_SIZE)

        # camera information
        if header == bytearray([1]):
            self.rgb565 = self.__receive_part_from_robot(IMAGE_PACKET_SIZE)
            self.camera_updated = True

        # sensors information
        elif header == bytearray([2]):
            self.sensor = self.__receive_part_from_robot(SENSORS_PACKET_SIZE)

        # no information
        else:
            return False

        return True

    def go_on(self):
        super().go_on()
        self.__send_to_robot()

        # check return is a boolean to say if all went ok.
        check_return = self.__receive_from_robot()

        return check_return

    def __set_speed_left(self, speed_left):
        speed_left = int(super().bounded_speed(speed_left)*100)

        # get the two's complement for neg values
        if speed_left < 0:
            speed_left = speed_left & 0xFFFF

        self.command[3] = speed_left & 0xFF  # LSByte
        self.command[4] = speed_left >> 8  # MSByte

    def __set_speed_right(self, speed_right):

        # *100 offset with Webots
        speed_right = int(super().bounded_speed(speed_right)*100)

        # get the two's complement for neg values
        if speed_right < 0:
            speed_right = speed_right & 0xFFFF

        self.command[5] = speed_right & 0xFF  # LSByte
        self.command[6] = speed_right >> 8  # MSByte

    def set_speed(self, speed_left, speed_right=None):
        # robot goes staight if user only put one speed
        if speed_right is None:
            speed_right = speed_left

        self.__set_speed_left(speed_left)
        self.__set_speed_right(speed_right)

    def get_speed(self):
        right_speed = self.command[5]/100  # offset of 100 with Webots
        left_speed = self.command[6]/100

        return [left_speed, right_speed]

    def get_motors_steps(self):
        sensors = self.sensor
        left_steps = struct.unpack("<h", struct.pack(
            "<BB", sensors[79], sensors[80]))[0]
        right_steps = struct.unpack("<h", struct.pack(
            "<BB", sensors[81], sensors[82]))[0]
        return [left_steps, right_steps]

    #### begin ###
    #    LED     #
    ##############

    def toggle_led(self, led_position, red=None, green=None, blue=None):
        if led_position in range(LED_COUNT):
            # LEDs in even position are not RGB
            if led_position % 2 == 0:

                if red or green or blue:
                    print(f'LED{led_position} is not RGB')

                self.command[7] = self.command[7] | 1 << (led_position//2)

            else:
                # led_position corresponding to the position in the self.command packet
                led_position = (led_position-1)*3//2 + 8

                # if RGB is not specified, we process it like a LED with no RGB
                if red != None and green != None and blue != None:

                    # lambda function to check if r,g,b are between 0 and 100
                    def between(color_val): return 0 <= color_val <= 100
                    in_rgb_range_values = list(
                        map(between, (red, green, blue)))

                    if all(in_rgb_range_values):
                        self.command[led_position] = red
                        self.command[led_position+1] = green
                        self.command[led_position+2] = blue
                    else:
                        # Inform what happend
                        for i in range(3):
                            color = {0: 'red', 1: 'green', 2: 'blue'}
                            if not in_rgb_range_values[i]:
                                print(
                                    f'color {color[i]} is not between 0 and 100')

                else:

                    self.command[led_position] = 15 & 0xFF  # red
                    self.command[led_position+1] = 0  # greeen
                    self.command[led_position+2] = 0  # blue

        else:
            print(
                f'invalid led position: {led_position}. Accepts 0 <= x <= 7. LED stays unchange.')

    def disable_led(self, led_position):
        if led_position in range(LED_COUNT):

            if led_position % 2 == 0:
                led_position //= 2

                # mask will shift the correct bit in the byte for LEDs
                mask = ~(1 << led_position)
                self.command[7] = self.command[7] & mask

            else:

                # led_position corresponding to the position in the self.command packet
                led_position = (led_position-1)*3//2 + 8

                self.command[led_position] = 0x00
                self.command[led_position+1] = 0x00
                self.command[led_position+2] = 0x00

        else:
            print(
                f'invalid led position: {led_position}. Accepts 0 <= x <= 7. LED stays ON.')

    def enable_body_led(self):
        # Shift 1 to the position of the current LED (binary representation),
        # then bitwise OR it with current byte LEDs
        self.command[7] = self.command[7] | 1 << 4

    def disable_body_led(self):
        mask = ~(1 << 4)
        self.command[7] = self.command[7] & mask

    def enable_front_led(self):
        self.command[7] = self.command[7] | 1 << 5

    def disable_front_led(self):
        mask = ~(1 << 5)
        self.command[7] = self.command[7] & mask

    ##### END ####
    #    LED     #
    ##############

    def get_prox(self):
        prox_values = [0 for _ in range(PROX_SENSORS_COUNT)]
        sensor = self.sensor

        # Please note that we can easily do a for loop but for comprehension stake we keep it this way.
        # 2 byte per sensor, odd position is LSB and even position is MSB
        prox_values[PROX_RIGHT_FRONT] = struct.unpack(
            "H", struct.pack("<BB", sensor[37], sensor[38]))[0]
        prox_values[PROX_RIGHT_FRONT_DIAG] = struct.unpack(
            "H", struct.pack("<BB", sensor[39], sensor[40]))[0]
        prox_values[PROX_RIGHT_SIDE] = struct.unpack(
            "H", struct.pack("<BB", sensor[41], sensor[42]))[0]
        prox_values[PROX_RIGHT_BACK] = struct.unpack(
            "H", struct.pack("<BB", sensor[43], sensor[44]))[0]

        prox_values[PROX_LEFT_BACK] = struct.unpack(
            "H", struct.pack("<BB", sensor[45], sensor[46]))[0]
        prox_values[PROX_LEFT_SIDE] = struct.unpack(
            "H", struct.pack("<BB", sensor[47], sensor[48]))[0]
        prox_values[PROX_LEFT_FRONT_DIAG] = struct.unpack(
            "H", struct.pack("<BB", sensor[49], sensor[50]))[0]
        prox_values[PROX_LEFT_FRONT] = struct.unpack(
            "H", struct.pack("<BB", sensor[51], sensor[52]))[0]

        self.ps = prox_values

        return prox_values

    ######### START #######
    #    AMBIENT LIGHT    #
    #######################

    def get_lights(self):
        sensor = self.sensor
        light_values = [0 for _ in range(PROX_SENSORS_COUNT)]

        light_values[PROX_RIGHT_FRONT] = struct.unpack(
            "H", struct.pack("<BB", sensor[53], sensor[54]))[0]
        light_values[PROX_RIGHT_FRONT_DIAG] = struct.unpack(
            "H", struct.pack("<BB", sensor[55], sensor[56]))[0]
        light_values[PROX_RIGHT_SIDE] = struct.unpack(
            "H", struct.pack("<BB", sensor[57], sensor[58]))[0]
        light_values[PROX_RIGHT_BACK] = struct.unpack(
            "H", struct.pack("<BB", sensor[59], sensor[60]))[0]

        light_values[PROX_LEFT_BACK] = struct.unpack(
            "H", struct.pack("<BB", sensor[61], sensor[62]))[0]
        light_values[PROX_LEFT_SIDE] = struct.unpack(
            "H", struct.pack("<BB", sensor[63], sensor[64]))[0]
        light_values[PROX_LEFT_FRONT_DIAG] = struct.unpack(
            "H", struct.pack("<BB", sensor[65], sensor[66]))[0]
        light_values[PROX_LEFT_FRONT] = struct.unpack(
            "H", struct.pack("<BB", sensor[67], sensor[68]))[0]

        self.ls = light_values

        return light_values

    def __calibrate_lights(self):
        # init array for calibration values
        self.ls_err = [0 for _ in range(PROX_SENSORS_COUNT)]

        print(self.get_id() + ' start calibrating IR proximity')

        # toggle light as witness
        self.toggle_all_led()

        # get multiple readings for each sensor
        for i in range(NBR_CALIB + OFFSET_CALIB):
            self.go_on()
            if i > OFFSET_CALIB:
                tmp = self.get_lights()
                for j in range(PROX_SENSORS_COUNT):
                    self.ls_err[j] += tmp[j]

        # calculate the average for each sensor
        for i in range(PROX_SENSORS_COUNT):
            self.ls_err[i] /= NBR_CALIB

        print(self.get_id() + ' finish calibrating IR proximity')

        self.disable_all_led()

    def get_lights_calibrated(self):
        light_values = self.get_lights()
        self.__calibrate_lights()
        for i in range(PROX_SENSORS_COUNT):
            if light_values[i]-self.ls_err[i] < 0:
                light_values[i] = 0
            else:
                light_values[i] -= self.ls_err[i]

        return light_values

    def init_ground(self):
        "No need for Real Robots."
        pass

    def get_ground(self):
        sensor = self.sensor
        ground_values = [0]*GROUND_SENSORS_COUNT
        ground_values[GS_LEFT] = struct.unpack(
            "H", struct.pack("<BB", sensor[90], sensor[91]))[0]
        ground_values[GS_CENTER] = struct.unpack(
            "H", struct.pack("<BB", sensor[92], sensor[93]))[0]
        ground_values[GS_RIGHT] = struct.unpack(
            "H", struct.pack("<BB", sensor[94], sensor[95]))[0]

        self.gs = ground_values

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

    def get_accelerometer_axes(self):
        sensor = self.sensor
        axe_x = struct.unpack("<h", struct.pack(
            "<BB", sensor[0], sensor[1]))[0]
        axe_y = struct.unpack("<h", struct.pack(
            "<BB", sensor[2], sensor[3]))[0]
        axe_z = struct.unpack("<h", struct.pack(
            "<BB", sensor[4], sensor[5]))[0]
        return [axe_x, axe_y, axe_z]

    def get_acceleration(self):
        sensor = self.sensor
        return struct.unpack("f", struct.pack("<BBBB", sensor[6], sensor[7], sensor[8], sensor[9]))[0]


    def get_gyro_axes(self):
        sensor = self.sensor
        gyro_x = struct.unpack("<h", struct.pack(
            "<BB", sensor[18], sensor[19]))[0]
        gyro_y = struct.unpack("<h", struct.pack(
            "<BB", sensor[20], sensor[21]))[0]
        gyro_z = struct.unpack("<h", struct.pack(
            "<BB", sensor[22], sensor[23]))[0]
        return [gyro_x, gyro_y, gyro_z]


    # return front, right, back. left microphones
    def get_microphones(self):
        sensor = self.sensor
        front = struct.unpack("<h", struct.pack(
            "<BB", sensor[77], sensor[78]))[0]
        right = struct.unpack("<h", struct.pack(
            "<BB", sensor[71], sensor[72]))[0]
        back = struct.unpack("<h", struct.pack(
            "<BB", sensor[75], sensor[76]))[0]
        left = struct.unpack("<h", struct.pack(
            "<BB", sensor[73], sensor[74]))[0]

        return [front, right, back, left]

#https://students.iitk.ac.in/roboclub/2017/12/21/Beginners-Guide-to-IMU.html#:~:text=it%20a%20try!-,Gyroscope,in%20roll%2C%20pitch%20and%20yaw.    
# def of roll and pitch https://www.youtube.com/watch?v=5IkPWZjUQlw


    def get_temperature(self):
        sensor = self.sensor
        return struct.unpack("b", struct.pack("<B", sensor[36]))[0]

    def get_tof(self):
        sensor = self.sensor
        return struct.unpack("h", struct.pack("<BB", sensor[69], sensor[70]))[0]



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

    def __rgb565_to_bgr888(self):
        counter = 0

        for j in range(CAMERA_HEIGHT):
            for i in range(CAMERA_WIDTH):
                index = 3 * (i + j * CAMERA_WIDTH)
                red_rgb555 = self.rgb565[counter] & 0xF8
                green_rgb555 = ((self.rgb565[counter] & 0x07) << 5) & 0xFF
                counter += 1
                green_rgb555 += ((self.rgb565[counter] & 0xE0) >> 3)
                blue_rgb555 = ((self.rgb565[counter] & 0x1F) << 3) & 0xFF
                counter += 1
                self.bgr888[index] = blue_rgb555
                self.bgr888[index + 1] = green_rgb555
                self.bgr888[index + 2] = red_rgb555

    def __save_bmp_image(self, filename):
        width = self.camera_width
        height = self.camera_height
        image = self.bgr888
        filesize = 54 + 3 * width * height
        # print("filesize = " + str(filesize))
        bmpfileheader = bytearray(14)
        bmpfileheader[0] = ord('B')
        bmpfileheader[1] = ord('M')
        bmpfileheader[2] = filesize & 0xFF
        bmpfileheader[3] = (filesize >> 8) & 0xFF
        bmpfileheader[4] = (filesize >> 16) & 0xFF
        bmpfileheader[5] = (filesize >> 24) & 0xFF
        bmpfileheader[6] = 0
        bmpfileheader[7] = 0
        bmpfileheader[8] = 0
        bmpfileheader[9] = 0
        bmpfileheader[10] = 54
        bmpfileheader[11] = 0
        bmpfileheader[12] = 0
        bmpfileheader[13] = 0

        bmpinfoheader = bytearray(40)
        bmpinfoheader[0] = 40
        bmpinfoheader[1] = 0
        bmpinfoheader[2] = 0
        bmpinfoheader[3] = 0
        bmpinfoheader[4] = width & 0xFF
        bmpinfoheader[5] = (width >> 8) & 0xFF
        bmpinfoheader[6] = (width >> 16) & 0xFF
        bmpinfoheader[7] = (width >> 24) & 0xFF
        bmpinfoheader[8] = height & 0xFF
        bmpinfoheader[9] = (height >> 8) & 0xFF
        bmpinfoheader[10] = (height >> 16) & 0xFF
        bmpinfoheader[11] = (height >> 24) & 0xFF
        bmpinfoheader[12] = 1
        bmpinfoheader[13] = 0
        bmpinfoheader[14] = 24
        bmpinfoheader[15] = 0

        bmppad = bytearray(3)
        with open(filename, 'wb') as file:
            file.write(bmpfileheader)
            file.write(bmpinfoheader)
            for i in range(height):
                file.write(image[(width * (height - i - 1) * 3)                                 :(width * (height - i - 1) * 3) + (3 * width)])
                file.write(bmppad[0:((4 - (width * 3) % 4) % 4)])

    def init_camera(self, save_image_folder=None, camera_rate=1):
        if not save_image_folder:
            save_image_folder = './'

        self.my_filename_current_image = save_image_folder + \
            '/'+self.get_id()+'_image_video.bmp'
        print(self.my_filename_current_image)
        print('camera enable')
        self.command[1] = self.command[1] | 1

    def disable_camera(self):
        # Force last bit to 0
        self.command[1] = self.command[1] & 0xFE

    def get_camera(self):
        if self.camera_updated:
            if self.my_filename_current_image:
                self.__rgb565_to_bgr888()
                self.__save_bmp_image(self.my_filename_current_image)

            self.camera_updated = False

        self.red, self.green, self.blue = [], [], []
        for i in range(self.camera_height * self.camera_width):
            self.red.append(self.bgr888[3 * i + 2])
            self.green.append(self.bgr888[3 * i + 1])
            self.blue.append(self.bgr888[3 * i])

        return self.red, self.green, self.blue

    def take_picture(self):
        if self.my_filename_current_image:
            # removing the last 4 character of my_filename_current_image
            # because we removing the file format to put it back to the end
            self.__save_bmp_image(
                self.my_filename_current_image[:-4] + f"{self.counter_img:0>4}" + '.bmp')
            self.counter_img += 1

    def live_camera(self, live_time=None):
        if not self.has_start_stream:
            # time setting
            self.start_time = time.time()
            self.has_start_stream = True

        # refresh time
        self.current_time = time.time()

        if live_time is None or (self.current_time - self.start_time) < live_time:
            # refresh robot communication
            self.get_camera()
        else:
            self.disable_camera()

    #### start ####
    #    SOUND  #
    # Music will start again each time you send its corresponding number command #
    ##############

    def play_mario(self):
        self.command[20] = 0x01
        self.go_on()
        self.command[20] = 0x00

    def play_underworld(self):
        self.command[20] = 0x02
        self.go_on()
        self.command[20] = 0x00

    def play_star_wars(self):
        self.command[20] = 0x04
        self.go_on()
        self.command[20] = 0x00

    def stop_sound(self):
        self.command[20] = 0x20
        self.go_on()
        self.command[20] = 0x00

    def play_sound(self, sound_number):
        switcher = {
            1: self.play_mario,
            2: self.play_underworld,
            3: self.play_star_wars
        }

        func = switcher.get(sound_number, self.stop_sound)
        func()

        self.command[20] = 0x00

    ####  END ####
    #    SOUND   #
    ##############

    def clean_up(self):
        if self.sock != 0:
            self.disable_camera()
            self.disable_all_led()
            self.disable_sensors()
            self.disable_front_led()
            self.disable_body_led()

            for _ in range(50):
                self.set_speed(0, 0)
                self.go_on()

            self.sock.close()
        print('Robot cleaned')


##########################
## CONSTANTS FOR WEBOTS ##
##########################

"""
# Uncomment if you want to use Webot specific communication
COM_CHANNEL = 1
MSG_NONE = 'ZZZ'
MSG_LENGTH = 4
"""


class __WebotsEpuck(Epuck):

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

        """
        # To uncomment if you want to use Webot specific communication
         
        self.emitter = self.robot.getEmitter('emitter')
        self.receiver = self.robot.getReceiver('receiver')
        self.emitter.setChannel(1)
        self.receiver.setChannel(1)
        self.receiver.enable(TIME_STEP)
        """

    def go_on(self):
        super().go_on()
        self.robot.step(TIME_STEP)

        # count step of the robot on Webots
        if self.left_motor.getVelocity() > 0:
            self.left_motor_counter += 1
        elif self.left_motor.getVelocity() < 0:
            self.left_motor_counter -= 1

        if self.right_motor.getVelocity() > 0:
            self.right_motor_counter += 1
        elif self.right_motor.getVelocity() < 0:
            self.right_motor_counter -= 1

        return True

    def get_id(self):
        return self.robot.getName()

    def get_ip(self):
        return socket.gethostname()

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

    def get_motors_steps(self):
        return [self.left_motor_counter, self.right_motor_counter]

    #################
    #       LED      #
    #################

    # LEDS are initiated when creation of the instance of the robot

    def toggle_led(self, led_position, red=None, green=None, blue=None):

        if led_position in range(LED_COUNT):

            if led_position % 2 == 0:

                if red or green or blue:
                    print(f'LED{led_position} is not RGB')

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
                                    f'color {color[i]} is not between 0 and 100')

                else:
                    self.led[led_position].set(0xFF0000)

        else:
            print(
                f'invalid led position: {led_position}. Accepts 0 <= x <= 7. LEDs unchanged.')

    def disable_led(self, led_position):
        if led_position not in range(LED_COUNT):
            print(
                f"invalid led position: {led_position}. Accepts 0 <= x <= 7. LED stays ON.")

        self.led[led_position].set(0)

    def enable_body_led(self):
        self.led[8].set(1)

    def disable_body_led(self):
        self.led[8].set(0)

    def enable_front_led(self):
        self.led[9].set(1)

    def disable_front_led(self):
        self.led[9].set(0)

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

    def get_prox(self):

        try:
            prox_values = [self.ps[i].getValue()
                           for i in range(PROX_SENSORS_COUNT)]
        except:
            print('Did you forget to my_robot.init_sensors() ?')
            return

        return prox_values

    def init_lights(self):
        lsNames = [
            'ls0', 'ls1', 'ls2', 'ls3',
            'ls4', 'ls5', 'ls6', 'ls7'
        ]
        for i in range(PROX_SENSORS_COUNT):
            self.ls.append(self.robot.getDevice(lsNames[i]))
            self.ls[i].enable(TIME_STEP)

    def get_lights(self):
        try:
            ls_values = [self.ls[i].getValue()
                         for i in range(PROX_SENSORS_COUNT)]
            return ls_values
        except:
            print('Did you my_robot.init_lights() ?')

    def get_lights_calibrated(self):
        # no calibration in simulation: calibrate_lights() is equivalent to get_lights()
        return self.get_lights()

    def init_ground(self):
        gsNames = [
            'gs0', 'gs1', 'gs2'
        ]
        for i in range(GROUND_SENSORS_COUNT):
            self.gs.append(self.robot.getDevice(gsNames[i]))
            self.gs[i].enable(TIME_STEP)

    def get_ground(self):
        try:
            ground_values = [self.gs[i].getValue()
                             for i in range(GROUND_SENSORS_COUNT)]

        except:
            print('Robot must add ground sensors to simulation and/or must init_ground()')
            return

        return ground_values


    def get_accelerometer_axes(self):
        # round values to integers for homogeniety with real robot
        round_values = [round(i) for i in self.accelerometer.getValues()]
        return round_values

    def get_acceleration(self):
        [x,y,z] = self.get_accelerometer_axes
        return sqrt(x**2 + y**2 + z**2)

    def get_gyro_axes(self):
        # round values to integers for homogeniety with real robot
        round_values = [round(i) for i in self.gyro.getValues()]
        return round_values

    def get_temp(self):
        print('no temperature on Webots')

    def get_tof(self):
        return self.tof.getValue()

 

    #################
    #     VIDEO     #
    #################
    # Need to init_camera before calling other methods

    def init_camera(self, save_image_folder=None, camera_rate=1):
        if not save_image_folder:
            save_image_folder = './'

        self.save_image_folder = save_image_folder
        self.camera.enable(TIME_STEP*camera_rate)

    def disable_camera(self):
        self.camera.disable()

    # https://www.cyberbotics.com/doc/reference/camera?tab-language=python
    def take_picture(self):
        try:
            save_as = self.save_image_folder + '/image'+ f"{self.counter_img:0>4}" +'.jpg'
            self.camera.saveImage(save_as, 100)  # 100 for best quality
            self.counter_img += 1
        except Exception as e:
            print(e)

    def live_camera_webots(self, live_time=None):
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

    def live_camera(self):
        print('Not necessary to call the live_camera method on Webots.')

    #################
    #       MUSIC   #
    #################

    def play_mario(self):
        pass

    def play_underworld(self):
        pass

    def play_star_wars(self):
        pass

    def stop_sound(self):
        print('Cannot play music on Webots')

    def play_sound(self, sound_number):
        print('Cannot play music on Webots')

    #################
    # COMMUNICATION #
    #################
    # Communication is initiated during creation of instance of the robot

    """
    # To uncomment if you want to use Webot specific communication
    # send message to other epucks.
    # It can only send strings
    def send_msg(self, msg):
        
        if isinstance(msg, str):
            bmsg = str.encode(msg)
            self.emitter.send(bmsg)

        else:
            print('Error : Emitter can only send string')

        
    def has_receive_msg(self):
        return self.receiver.getQueueLength() > 0
        
    def receive_msg(self):
        if self.has_receive_msg():
            bmsg = self.receiver.getData()
            msg = bmsg.decode()
            self.receiver.nextPacket()
            return msg

        return None
    """

    def clean_up(self):
        for _ in range(50):
            self.set_speed(0, 0)
            self.go_on()
        print('Robot cleaned')
