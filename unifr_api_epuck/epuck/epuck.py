from multiprocessing.managers import SyncManager
import socket
import time
from .constants import *
from math import sqrt, atan2, pi


SyncManager.register("syncdict")
SyncManager.register("lock")
SyncManager.register("shutdown")


class Epuck:
    """

    .. note:: These are variables properties to call 

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
        Initiates the robot

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

    def get_id(self):
        pass

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
       
        if speed > MAX_SPEED:
            return MAX_SPEED
        elif speed < -MAX_SPEED:
            return -MAX_SPEED

        return speed


    def enable_led(self, led_position, red=None, green=None, blue=None):
        """ 
        Turns ON led at led_position

        :param led_position: int
            value between 0 and 7 

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
        for i in range(LED_COUNT_ROBOT):
            self.enable_led(i)

    def disable_all_led(self):
        """
        Turns OFF all LED lights
        """
        for i in range(LED_COUNT_ROBOT):
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
        # init array for calibration values
        self.ps_err = [0 for _ in range(PROX_SENSORS_COUNT)]

        print(self.get_id() + ' start calibrating IR proximity')

        # enable light as witness
        self.enable_all_led()

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

        self.go_on()

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
        prox_corr = [0]*PROX_SENSORS_COUNT

        for i in range(PROX_SENSORS_COUNT):
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


    def init_camera(self, save_image_folder=None, camera_rate=1):
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
        Processes raw images from robot

        .. tip:: 
            when you combine the same position of three colour arrays, you get the value of a pixel
            
            #get pixel at position 10 of the image

            red, green, blue = robot.get_camera() \n
            pixel = [red[10], green[10], blue[10]] 

            

        
        :return arrays: [red],[green],[blue]
        """
        pass

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
                        'Please create a GUI host by executing in your terminal: `python3 -m unifr_api_epuck`')

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
        Keeps the host aware that the epuck is alive
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
        Puts a message in queue to other robots

        :param msg: any 
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
        """
        :returns: True if the robot has pending messages in his queue.
        """
        self.__stay_alive()
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
        Gets next message from the robot queue.

        :returns recv_mess: any 
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