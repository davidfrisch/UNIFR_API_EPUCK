from .epuck import Epuck
import struct
import socket
import sys
import time
import logging
import numpy as np
from .models.helper import non_max_suppression,plot_detection
from .models.yolo import attempt_load
import torch
import os
import cv2
import signal


###############
#  Detection  #
###############

#Needed for the detection
#the model is the network with can be build with initiate_model()
#it needs some path to the weights file
#and the model itself is passed as global variable, so they can enable/disable the camera when needed without rebuilding the network

model = None
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.insert(0, __location__)

#The Object returned when looking for detection
class Detected:
    def __init__(self, x_center, y_center,width,height,confidence,label):
        self.x_center = x_center
        self.y_center = y_center
        self.width = width
        self.height = height
        self.confidence = confidence
        self.label = label

    def __str__(self):
        return f'x_center: {self.x_center}, y_center: {self.y_center}, width: {self.width}, height: {self.height}, confidence: {self.confidence}, label: {self.label}'


#The ColorDetected returned when looking for color detection
class ColorDetected:
    def __init__(self, x_center = 0, y_center = 0,width = 0, height = 0, area = 0, label = 'none'):
        self.x_center = x_center
        self.y_center = y_center
        self.width = width
        self.height = height
        self.area = area
        self.label = label
        
    def __str__(self):
        return f'x_center: {self.x_center}, y_center: {self.y_center}, width: {self.width}, height: {self.height}, area: {self.area}, label: {self.label}'



###############

class WifiEpuck(Epuck):

    def __init__(self, ip_addr):

        super().__init__(ip_addr)
        """
        A class used to represent a robot Real Robot.

        :param ip_addr: str - The IP address of the e-puck
        """

        ######################
        ## CONSTANTS FOR Real Robot ##
        ######################
        # For TCP communication
        self.COMMAND_PACKET_SIZE = 21
        self.HEADER_PACKET_SIZE = 1
        self.SENSORS_PACKET_SIZE = 104
        self.IMAGE_PACKET_SIZE = 160 * 120 * 2  # Max buffer size = widthxheightx2
        self.MAX_NUM_CONN_TRIALS = 5
        self.TCP_PORT = 1000  # This is fixed.


        # communication Robot <-> Computer
        self.__sock = 0
        self.__command = bytearray([0] * self.COMMAND_PACKET_SIZE)
 

        # camera init specific for Real Robot
        self.__camera_width = 160
        self.__camera_height = 120
        self.__rgb565 = [0 for _ in range(self.IMAGE_PACKET_SIZE)]
        self.__bgr888 = bytearray([0] * self.__camera_width*self.__camera_height*3*2)  # 160x120x3x2
        self.__camera_updated = False
        self.__my_filename_current_image = ''
        self.__save_image_folder='.'
        self.__counter_img = 0
        self.__counter_detec_img = 0
        self.__counter_colordetec_img = 0


        # start communication with computer
        self.__tcp_init()
        self.__init_command()

        signal.signal(signal.SIGINT, self.__stopcontroller_handler)   

        print("Robot initialized")

    
    def __tcp_init(self):
        """
            Initiate the TCP communication between the robot and host computer.
            prints "connected to x.x.x.x" once connection succeed
            :raises socket.timeout: This exception is raised when a timeout occurs on a socket
            :raises socket.OSError: This exception is raised when a system function returns a system-related error Exception
        """
        trials = 0
        ip_address = self.ip_addr
        print("Try to connect to " + ip_address +
              ":" + str(self.TCP_PORT) + " (TCP)")
        while trials < self.MAX_NUM_CONN_TRIALS:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__sock.settimeout(10)  # non-blocking socket
            try:
                self.__sock.connect((ip_address, self.TCP_PORT))
            except socket.timeout as err:
                self.__sock.close()
                logging.error("Timeout error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            except socket.OSError as err:
                self.__sock.close()
                logging.error("OS error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            except Exception as err:
                self.__sock.close()
                logging.error("General error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            break

        if trials == self.MAX_NUM_CONN_TRIALS:
            print("Can't connect to " + ip_address)
            return

        print("Connected to " + ip_address)
        print("\r\n")       


    def __init_command(self):
        """
        Initial command packet that is send to the e-puck once the first connection succeeded.
        """
        # Init the array containing the commands to be sent to the robot.
        self.__command[0] = 0x80  # Packet id for settings actuators
        self.__command[1] = 2  # Request: only sensors enabled
        self.__command[2] = 0  # Settings: set motors speed
        self.__command[3] = 0  # left motor LSB
        self.__command[4] = 0  # left motor MSB
        self.__command[5] = 0  # right motor LSB
        self.__command[6] = 0  # right motor MSB
        self.__command[7] = 0  # lEDs
        self.__command[8] = 0  # LED2 red
        self.__command[9] = 0  # LED2 green
        self.__command[10] = 0  # LED2 blue
        self.__command[11] = 0  # LED4 red
        self.__command[12] = 0  # LED4 green
        self.__command[13] = 0  # LED4 blue
        self.__command[14] = 0  # LED6 red
        self.__command[15] = 0  # LED6 green
        self.__command[16] = 0  # LED6 blue
        self.__command[17] = 0  # LED8 red
        self.__command[18] = 0  # LED8 green
        self.__command[19] = 0  # LED8 blue
        self.__command[20] = 0  # speaker

        self.go_on()
        print('Battery left :'+ str(self.get_battery_level()))

    def get_id(self):
        """
        :returns: The ip address (replace the dots with underscores e.g: x_x_x_x)
        """
        return self.id

    def set_id(self, new_id):
        return super().set_id(new_id)

    def get_ip(self):
        """
        :returns: The IP address of the e-puck
        """
        return self.ip_addr

    #####################################################
    ## COMMUNICATION METHODS between robot and master  ##
    #####################################################

    def __send_to_robot(self):
        """
        Send a new packet from the computer to the robot
        """
        byte_send = 0

        # loop until all fragments of the packet has been sent
        while byte_send < self.COMMAND_PACKET_SIZE:
            sent = self.__sock.send(self.__command[byte_send:])
            if sent == 0:
                raise RuntimeError("Send to e-puck error")

            byte_send = byte_send + sent

        # stop calibration
        self.__command[2] = 0

    def __receive_part_from_robot(self, msg_len):
        """
        Receive a new packet from the robot to the computer
        """

        # receiving data in fragments
        chunks = []
        bytes_recd = 0
        try:
            while bytes_recd < msg_len:
                # old code
                #chunk = self.__sock.recv(min(msg_len - bytes_recd, 2048))
                #if chunk == b'':
                #    raise RuntimeError("socket connection broken")
            
                trials = 0
                chunk = b''
                while chunk == b'':
                    trials += 1
                    chunk = self.__sock.recv(min(msg_len - bytes_recd, 2048))
                    if chunk == b'' and trials == self.MAX_NUM_CONN_TRIALS:
                        raise RuntimeError("socket connection broken")
                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)
            return b''.join(chunks)
        except:
            print('\033[91m'+'Lost connection of : ' +
                  str(self.get_ip())+'\033[0m')
            sys.exit(1)

    def __receive_from_robot(self):
        """
        Receives the packet from the robot
        
        :returns: True if no problem occured
        """
        # depending of the header, we know what data we receive
        header = self.__receive_part_from_robot(self.HEADER_PACKET_SIZE)

        # camera information
        if header == bytearray([1]):
            self.__rgb565 = self.__receive_part_from_robot(self.IMAGE_PACKET_SIZE)
            self.__camera_updated = True

        # sensors information
        elif header == bytearray([2]):
            self.sensors = self.__receive_part_from_robot(self.SENSORS_PACKET_SIZE)

        # no information
        else:
            return False

        return True

    def go_on(self):
        """
        * Sends and receives commands between computer and robot.

        :returns: True (if no problem occurs)
        """
        super().go_on()
        # check return is a boolean to say if all went ok.
        self.__send_to_robot()
        check_return = self.__receive_from_robot()


        return check_return

    def sleep(self, duration):
        return super().sleep(duration)

    def get_battery_level(self):
        """
        Gets robot's battery level.
        """
        battery_level = struct.unpack("H", struct.pack("<BB", self.sensors[83], self.sensors[84]))[0]
        return battery_level

   
    def __set_speed_left(self, speed_left):
        """
        Set the speed of the left motor of the robot
        
        :param speed_left: speed of left wheel 
        """
        speed_left = int(self.bounded_speed(speed_left))

        # get the two's complement for neg values
        if speed_left < 0:
            speed_left = speed_left & 0xFFFF

        self.__command[3] = speed_left & 0xFF  # LSByte
        self.__command[4] = speed_left >> 8  # MSByte

    def __set_speed_right(self, speed_right):
        """
        Set speed of the right motor of the robot

        :param speed_right: right wheel speed
        """
        # *100 offset with Webots
        speed_right = int(self.bounded_speed(speed_right))

        # get the two's complement for neg values
        if speed_right < 0:
            speed_right = speed_right & 0xFFFF

        self.__command[5] = speed_right & 0xFF  # LSByte
        self.__command[6] = speed_right >> 8  # MSByte

    def set_speed(self, speed_left, speed_right=None):
        # robot goes staight if user only put one speed
        if speed_right is None:
            speed_right = speed_left

        self.__set_speed_left(speed_left)
        self.__set_speed_right(speed_right)

    def get_speed(self):
        right_speed = self.__command[5]*self.MAX_SPEED/self.MAX_SPEED_IRL
        left_speed = self.__command[6]*self.MAX_SPEED/self.MAX_SPEED_IRL

        return [left_speed, right_speed]
    
    
    def bounded_speed(self, speed):
        #bounded speed is based on Webots maximums
        new_speed = super().bounded_speed(speed)
        new_speed *=self.MAX_SPEED_IRL/self.MAX_SPEED
        return new_speed

    def get_motors_steps(self):
        """
        Gets number of steps of the wheels

        :returns: [left_wheel, right_wheel]
        :rtype: [int,int]
        """ 
        left_steps = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[79], self.sensors[80]))[0]
        right_steps = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[81], self.sensors[82]))[0]
        return [left_steps, right_steps]

    #### begin ###
    #    LED     #
    ##############

    def enable_led(self, led_position, red=None, green=None, blue=None):
        if led_position in range(self.LED_COUNT_ROBOT):
            # LEDs in even position are not RGB
            
            if led_position % 2 == 0:

                if red or green or blue:
                    print('LED '+ str(led_position) + ' is not RGB')

                self.__command[7] = self.__command[7] | 1 << (led_position//2)

            else:
                # led_position corresponding to the position in the self.__command packet
                led_position = (led_position-1)*3//2 + 8
                
                # if RGB is not specified, we process it like a LED with no RGB
                if red != None and green != None and blue != None:

                    # lambda function to check if r,g,b are between 0 and 100
                    def between(color_val): return 0 <= color_val <= 100
                    in_rgb_range_values = list(
                        map(between, (red, green, blue)))

                    if all(in_rgb_range_values):
                        self.__command[led_position] = red
                        self.__command[led_position+1] = green
                        self.__command[led_position+2] = blue
                    else:
                        # Inform what happend
                        for i in range(3):
                            color = {0: 'red', 1: 'green', 2: 'blue'}
                            if not in_rgb_range_values[i]:
                                print(
                                    'color ' + color[i] + ' is not between 0 and 100')

                else:

                    self.__command[led_position] = 15 & 0xFF  # red
                    self.__command[led_position+1] = 0  # greeen
                    self.__command[led_position+2] = 0  # blue

        else:
            print(
                'invalid led position: '+ str(led_position) + '. Accepts 0 <= x <= 7. LED stays unchange.')

    def disable_led(self, led_position):
        if led_position in range(self.LED_COUNT_ROBOT):

            if led_position % 2 == 0:
                led_position //= 2

                # mask will shift the correct bit in the byte for LEDs
                mask = ~(1 << led_position)
                self.__command[7] = self.__command[7] & mask

            else:

                # led_position corresponding to the position in the self.__command packet
                led_position = (led_position-1)*3//2 + 8

                self.__command[led_position] = 0x00
                self.__command[led_position+1] = 0x00
                self.__command[led_position+2] = 0x00

        else:
            print(
                'invalid led position: ' + str(led_position) + '. Accepts 0 <= x <= 7. LED stays ON.')

    def enable_all_led(self):
        return super().enable_all_led()

    def disable_all_led(self):
        return super().disable_all_led()

    def enable_body_led(self):
        # Shift 1 to the position of the current LED (binary representation),
        # then bitwise OR it with current byte LEDs
        self.__command[7] = self.__command[7] | 1 << 4

    def disable_body_led(self):
        mask = ~(1 << 4)
        self.__command[7] = self.__command[7] & mask

    def enable_front_led(self):
        self.__command[7] = self.__command[7] | 1 << 5

    def disable_front_led(self):
        mask = ~(1 << 5)
        self.__command[7] = self.__command[7] & mask

    ##### END ####
    #    LED     #
    ##############
    #################
    #   SENSORS     #
    #################

    def init_sensors(self):
        self.__command[1] = self.__command[1] | (1 << 1)
        # start sensor calibration, with the intern calibration
        #self.__command[2] = 1
        # custom calibration
        self.__command[2] = 0 

    def disable_sensors(self):
        # put the second bit to last at 0
        self.__command[1] = self.__command[1] & 0xFD


    def get_prox(self):
        # 2 byte per sensor, odd position is LSB and even position is MSB
        prox_values = [struct.unpack(
            "H", struct.pack("<BB", self.sensors[37+2*i], self.sensors[38+2*i]))[0] for i in range(self.PROX_SENSORS_COUNT)]

        return prox_values

    def calibrate_prox(self):
        return super().calibrate_prox()

    def get_calibrate_prox(self):
        return super().get_calibrate_prox()

    def init_tof(self):
        pass

    def get_tof(self): 
        return struct.unpack("h", struct.pack("<BB", self.sensors[69], self.sensors[70]))[0]

    def disable_tof(self):
        return super().disable_tof()

    def init_ground(self):
        """
        No need for real robots.
        """
        pass

    def get_ground(self): 

        ground_values = [struct.unpack(
            "H", struct.pack("<BB", self.sensors[90+2*i], self.sensors[91+2*i]))[0] for i in range(self.GROUND_SENSORS_COUNT)]

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
        gyro_x = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[18], self.sensors[19]))[0]
        gyro_y = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[20], self.sensors[21]))[0]
        gyro_z = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[22], self.sensors[23]))[0]
        return [gyro_x, gyro_y, gyro_z]

    def get_accelerometer_axes(self): 
        axe_x = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[0], self.sensors[1]))[0]
        axe_y = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[2], self.sensors[3]))[0]
        axe_z = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[4], self.sensors[5]))[0]
        return [axe_x, axe_y, axe_z]

    def get_acceleration(self): 
        return struct.unpack("f", struct.pack("<BBBB", self.sensors[6], self.sensors[7], self.sensors[8], self.sensors[9]))[0]

    def get_orientation(self): 
        return struct.unpack("f", struct.pack("<BBBB", self.sensors[10], self.sensors[11], self.sensors[12], self.sensors[13]))[0]

    def get_inclination(self): 
        return struct.unpack("f", struct.pack("<BBBB", self.sensors[14], self.sensors[15], self.sensors[16], self.sensors[17]))[0]


    def get_roll(self):
        return super().get_roll()

    def get_pitch(self):
        return super().get_pitch()


    # return front, right, back. left microphones
    def get_microphones(self):
        """
           Gets microphones' intensity 

        .. note:: 
            Mic volume: between 0 and 4095

        .. image:: ../res/micro_img.png
            :width: 300
            :alt: add the Node

        :returns: [front, right, back, left]
        :rtype: array of int
        """ 
        front = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[77], self.sensors[78]))[0]
        right = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[71], self.sensors[72]))[0]
        back = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[75], self.sensors[76]))[0]
        left = struct.unpack("<h", struct.pack(
            "<BB", self.sensors[73], self.sensors[74]))[0]

        return [front, right, back, left]


    def get_temperature(self):
        """
        Gets the temperature from the robot

        :returns: temperature
        :rtype: int (degree Celsius)
        """ 
        return struct.unpack("b", struct.pack("<B", self.sensors[36]))[0]


#https://students.iitk.ac.in/roboclub/2017/12/21/Beginners-Guide-to-IMU.html#:~:text=it%20a%20try!-,Gyroscope,in%20roll%2C%20pitch%20and%20yaw.    
# definition of roll and pitch https://www.youtube.com/watch?v=5IkPWZjUQlw
    
    def get_tv_remote(self):
        """
        Get data from tv remote received by the robot.

        toggle: alternatively 1 or 0
        address: address in the remote
        data: output from the remote

        returns: toggle, address, data
        """ 
        toggle = struct.unpack("b", struct.pack("<B", self.sensors[86]))[0]
        addr = struct.unpack("b", struct.pack("<B", self.sensors[87]))[0]
        data = struct.unpack("b", struct.pack("<B", self.sensors[88]))[0]

        return [toggle, addr, data]



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
        for j in range(self.__camera_height):
            for i in range(self.__camera_width):
                index = 3 * (i + j * self.__camera_width)
                red = self.__rgb565[counter]&0xF8
                green = ((self.__rgb565[counter]&0x07) << 5) & 0xFF
                counter += 1
                green += ((self.__rgb565[counter]&0xE0) >> 3)
                blue = ((self.__rgb565[counter]&0x1F) << 3) & 0xFF
                counter += 1
                self.__bgr888[index] = blue
                self.__bgr888[index + 1] = green
                self.__bgr888[index + 2] = red

    def __save_bmp_image(self, filename):
        width = self.__camera_width
        height = self.__camera_height
        image = self.__bgr888
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
                file.write(image[(width * (height - i - 1) * 3):(width * (height - i - 1) * 3) + (3 * width)])
                file.write(bmppad[0:((4 - (width * 3) % 4) % 4)])

    def init_camera(self, new_image_folder=None, size=(None, None)):
        super().init_camera()
        if size != (None, None):
                print('Only sizable for pipuck')
                
        if new_image_folder:
            self.__save_image_folder = new_image_folder

        self.__my_filename_current_image = self.__save_image_folder + \
            '/'+self.get_id()+'_image_video.bmp'
        # print(self.__my_filename_current_image)
        # print('camera enable')
        self.__command[1] = self.__command[1] | 1

    def disable_camera(self):
        # Set last bit to 0
        super().disable_camera()
        self.__command[1] = self.__command[1] & 0xFE

    def get_camera(self):
        if self.__camera_updated:
            if self.__my_filename_current_image:
                self.__rgb565_to_bgr888()

            self.__camera_updated = False

        #take r,g,b
        red = self.__bgr888[2::3][:self.__camera_width*self.__camera_height]
        green = self.__bgr888[1::3][:self.__camera_width*self.__camera_height]
        blue = self.__bgr888[0::3][:self.__camera_width*self.__camera_height]

        #resize 1dim to array of 2dim  
        red = np.array(red).reshape(self.__camera_height, self.__camera_width)
        green = np.array(green).reshape(self.__camera_height, self.__camera_width)
        blue = np.array(blue).reshape(self.__camera_height, self.__camera_width)

        return [red, green, blue]

    def take_picture(self, filename = None):
        """
        Takes a picture and saves it in defined image folder from :py:meth:`init_camera<unifr_api_epuck.epuck_wifi.WifiEpuck.init_camera>`
        """
        if self.__my_filename_current_image:
            if not filename:
                self.__rgb565_to_bgr888()
                # removing the last 4 character of my_filename_current_image
                # because we add the counter in picture name
                counter = '{:04d}'.format(self.__counter_img)
                self.__save_bmp_image(
                    self.__my_filename_current_image[:-10] + counter + '.bmp')
                self.__counter_img += 1
            else:
                if not '.bmp' in filename:
                    filename+='.bmp'

                self.__rgb565_to_bgr888()
                # removing the last 4 character of my_filename_current_image
                # because we add the counter in picture name
                self.__save_bmp_image(self.__save_image_folder+'/'+filename)

    def live_camera(self, duration=None):
        if not self.has_start_stream:
            # time setting
            self.start_time = time.time()
            self.has_start_stream = True

        # refresh time
        self.current_time = time.time()

        if duration is None or (self.current_time - self.start_time) < duration:
            # refresh robot communication
            self.get_camera()
            self.__save_bmp_image(self.__my_filename_current_image)
            if self.ClientCommunication:
                with open(self.__my_filename_current_image, 'rb') as f:
                    image_data = f.read()
                self.ClientCommunication.stream_img(image_data) 
          
        else:
            self.disable_camera()

    #### start ####
    #    MUSIC  #
    # Music will start again each time you send its corresponding number command #
    ##############

    def play_sound(self, sound_number):
        """
        Plays the corresponded music of the sound_number

        .. warning:: 
            Only works with real robots

        0. Plays main Mario's theme
        1. Plays underworld Mario's theme
        2. Plays Star Wars theme

        :param sound_number: int - (between 0 and 2)
        """
        switcher = {
            1: self.play_mario,
            2: self.play_underworld,
            3: self.play_star_wars
        }

        func = switcher.get(sound_number, self.stop_sound)
        func()

        self.__command[20] = 0x00

    def play_mario(self):
        self.__command[20] = 0x01
        self.go_on()
        self.__command[20] = 0x00

    def play_underworld(self):
        self.__command[20] = 0x02
        self.go_on()
        self.__command[20] = 0x00

    def play_star_wars(self):
        self.__command[20] = 0x04
        self.go_on()
        self.__command[20] = 0x00

    def stop_sound(self):
        self.__command[20] = 0x20
        self.go_on()
        self.__command[20] = 0x00
    ####  END ####
    #    SOUND   #
    ##############
    def init_client_communication(self, host_ip='localhost'):
        return super().init_client_communication(host_ip=host_ip)

    def send_msg(self, msg):
        return super().send_msg(msg)

    def receive_msg(self):
        return super().receive_msg()

    def has_receive_msg(self):
        return super().has_receive_msg()

    def __stopcontroller_handler(self, signum, frame):
        """
        Gracefully stops the controller of the robot
        """
        signal.signal(signum, signal.SIG_IGN) # ignore additional signals
        print('leaning up  ...     ')
        self.clean_up()


    def clean_up(self):
        """
        Disables all and closes socket.
        """
        if self.__sock != 0:
            self.disable_camera()
            self.disable_all_led()
            self.disable_sensors()
            self.disable_front_led()
            self.disable_body_led()

            for _ in range(10):
                self.set_speed(0, 0)
                self.go_on()

            self.sleep(1)

            self.__sock.close()
            sys.exit(0)
        #print('Robot cleaned')


    ####################
    #    END DAVID     #
    ####################

    ####################
    #  START VINCENT   #
    ####################

    ####################
    #   DETECTION      #
    ####################

    #Call at the beginning of the session only
    def initiate_model(self,weights=None):

        global model

        # Initialize

        if weights is None:
            weights = os.path.join(__location__,'best.pt')
        device = 'cpu'        

        # Load model

        model = attempt_load(weights, map_location=device)  # load FP32 model
        print("model initialized, ready to use")


    def get_detection(self,img = None,conf_thresh = 0.9):
        """
        Analyze the picture passed as img
        
        :param img: the 120x160x3 array containing a picture returned by the function get_picture
        :param conf_thresh: an artifical threshold to limit the detections only to a certain confidence level
        :return: array of Detected objects
        .. warning:: 
            Only works with real robots
        """

        global model
        device = 'cpu'

        if model is None:
            print("You forgot to initialyse the network")
            return

        if img is None:
            print("Give a picture to analyse")
            return

        #add padding
        temp = np.zeros((3,8,160),dtype='uint8')
        img = np.append(img, temp, axis=1)

        # Run inference
        img = torch.from_numpy(img).to(device)
        img = img.float()  # uint8 to fp32
        img = img / 255.0  # 0 - 255 to 0.0 - 1.0

        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim

        #Use the model to predict 
        pred = model(img, augment=False, visualize=False)[0]
        pred = non_max_suppression(pred, 0.25, 0.45, None, False, max_det=1000)

        #Result processing (manipulating Pytorch tensor to numpy array of Object)
        [tensor_temp] = pred
        rep = []
        choices = {0: "Red Block", 1: "Black Block",2:"Black Ball",3:"Blue Block",4:"Epuck",5:"Green Block"}

        for det in tensor_temp:

            conf = det[4].item()

            #Added test, to remove all the low confidence predictions, according to the report
            if conf < conf_thresh:
                continue

            det = det.numpy()

            x = (det[0] + det[2]) / 2
            y = (det[1] + det[3]) / 2
            w = det[2] - det[0]
            h = det[3] - det[1]

            cls = choices.get(int(det[5]), int(det[5]))

            rep.append(Detected(x_center=x,y_center=y,width=w,height=h,confidence=conf,label=cls))

        return rep or []

    #Take a picture, analyse it and save the anotated picture in the defined image folder
    def save_detection(self,filename = None):
        """
        Save the annotated image either with a default name or the one given in filename
        :param filename: str under which the picture should be saved
        .. warning:: 
            Only works with real robots
        """

        #Take the picture
        img = self.get_camera()
        img = np.array(img)

        #Get the detection
        detection = self.get_detection(img,conf_thresh = 0.1)

        #Need some work on the picture to save it
        img_copy = img.transpose(1,2,0).astype(np.uint8).copy()
        bgr_img = cv2.cvtColor(img_copy, cv2.COLOR_RGB2BGR)

        #plot detection
        plot_detection(bgr_img,detection)

        if not filename:

            counter = '{:04d}'.format(self.__counter_detec_img)

            cv2.imwrite(self.__save_image_folder+'/'+self.get_id() +'_detected_image_'+ counter + '.bmp',bgr_img)

            self.__counter_detec_img += 1

        else:
            if not '.bmp' in filename:
                filename+='.bmp'

            cv2.imwrite(self.__save_image_folder+'/'+filename,bgr_img)

    def live_detection(self,duration=None):
        """
        Lets you stream the annotated image from the GUI
        The live_detection method needs to be called at each step.
        :param duration: int - duration of the stream. (default: until program ends)
        .. warning:: 
            Only works with real robots
        
        """

        if not self.has_start_stream:
            # time setting
            self.start_time = time.time()
            self.has_start_stream = True

        # refresh time
        self.current_time = time.time()

        if duration is None or (self.current_time - self.start_time) < duration:
            # refresh robot communication
            img = self.get_camera()
            img = np.array(img)

            detection = self.get_detection(img)

            img_copy = img.transpose(1,2,0).astype(np.uint8).copy()
            bgr_img = cv2.cvtColor(img_copy, cv2.COLOR_RGB2BGR)
            plot_detection(bgr_img,detection)

            #overwrite always the same picture
            cv2.imwrite(self.__save_image_folder+'/'+self.get_id()+'_image_video.bmp',bgr_img)
            save = self.__save_image_folder+'/'+self.get_id()+'_image_video.bmp'

            if self.ClientCommunication:
                with open(save,"rb") as f:
                    image_data = f.read()
                self.ClientCommunication.stream_img(image_data)

        else:
            self.disable_camera()
                    
                    
    ####################
    #    END VINCENT   #
    ####################

    ####################
    # COLOR DETECTION  #
    ####################
    

    def detect_color_masks(self,img, tol = 20, height = 50) :
        """
        Computes masks of primary colors R, G or B, black gray or white
        
        .. warning:: 
            Not currently used
            Only works with real robots
        """

        b,g,r = cv2.split(img)
        # change type to allow pixel operations 
        b = b.astype(np.int16)
        g = g.astype(np.int16)
        r = r.astype(np.int16)
        
        bg = b-g
        gr = g-r
        rb = r-b

        
        gray_mask = (abs(gr) <= 20) & (abs(rb) <= 20) | (abs(bg) <= 20) & (abs(rb) <= 20) | (abs(bg) <= 20) & (abs(gr) <= 20) | ((r>240) & (g >240) & (b > 240))       
        
        white_mask = ((r>200) & (g >200) & (b > 200))
        black_mask = (r+g+b < 400)

        # color masks
        red_mask = ~gray_mask & ((gr < -tol) & (rb > tol))    
        green_mask = ~gray_mask & ((bg < - tol) & (gr > tol)) 
        blue_mask = ~gray_mask & ((rb < -tol) & (bg > tol))

        # convert gray to white
        white_mask = white_mask | gray_mask

        # convert upper black pixels to white
        upper_black = np.full(img.shape[0:2],False)
        upper_black[0:height,:] = black_mask[0:height,:]
        
        white_mask = white_mask | upper_black
        black_mask[0:height,:] = False

        red_mask = red_mask & ~white_mask
        green_mask = green_mask & ~white_mask
        blue_mask = blue_mask & ~white_mask

        #black_mask = black_mask & ~white_mask

        return [red_mask, green_mask, blue_mask, black_mask, white_mask, gray_mask]
     
    def erosion(self,img, size = 2, shape = cv2.MORPH_RECT):
        #shape =  cv.MORPH_RECT
        #shape =  cv.MORPH_CROSS
        #shape =  cv.MORPH_ELLIPSE
        element = cv2.getStructuringElement(shape, (2 * size + 1, 2 * size + 1),(size, size))
        return  cv2.erode(img, element)

    def dilatation(self,img, size = 2, shape = cv2.MORPH_RECT):
        #shape =  cv.MORPH_RECT
        #shape =  cv.MORPH_CROSS
        #shape =  cv.MORPH_ELLIPSE
        element = cv2.getStructuringElement(shape, (2 * size + 1, 2 * size + 1),(size, size))
        return cv2.dilate(img, element)
     

    def mask_cleanup(self,mask) :

        mask = self.dilatation(mask,size=1)
        mask = self.erosion(mask,size=2) 
        mask = self.dilatation(mask,size=2)
        mask = self.erosion(mask,size=2) 

        #binary = dilatation(binary,size=3)
        #binary = erosion(binary)

        return mask

    def color_img_from_mask(self,mask,color,bg_color) :
        shp = mask.shape + (3,)
        img = np.zeros(shp, np.uint8)

        mask = mask.astype(np.uint8)

        mask = self.mask_cleanup(mask)
        
        # Fill image with color(set each pixel to color)
        img[:,:,:] = color

        img[~mask.astype(bool),:] = bg_color

        return img 
     

    def is_gray(self,r, g, b):
        """Checks if a pixel is gray, by Ali Gökkaya"""
        return ((abs(r-g) <= 20 and abs(r-b) <= 20) or 
                (abs(b-g) <= 20 and abs(b-r) <= 20) or
                (abs(r-g) <= 20 and abs(g-b) <= 20) or
                r > 240 and g > 240 and b > 240 )


    def color(self,r, g, b):
        """Detects the primary color the predominates in an rgb pixel, by Ali Gökkaya"""
        r = int(r)
        g = int(g)
        b = int(b)
        
        tol = 15
        
        if self.is_gray(r, g, b):
            if (r > 200 and g > 200 and b > 200):
                return 1  # Blanc
            elif ((r+g+b) < 400):
                return 2  # Noir
            else:
                return 1  # Gris
        else:
            if r > g + tol and r > b + tol:
                return 3  # Rouge
            elif g > r  + tol and g > b  + tol:
                return 4  # Vert
            elif b > r  + tol and b > g  + tol:
                return 5  # Bleu
            else:
                return 1  # Autre



    def detect_color_masks_alt(self,img) :
        """
        Computes masks of primary colors R, G or B, black gray or white, using non-optimal pixel-per-pixel comparison
        
        .. warning:: 
            Only works with real robots
        """

        array = np.array(img)
        rgb = np.empty((120,160))  # Crée un tableau vide pour stocker les valeurs RGB
            
        # Convertit les valeurs du tableau d'entrée en couleurs, by Ali Gökkaya
        for i in range(120):
            for j in range(160):
                rgb[i][j] = self.color(array[i][j][2], array[i][j][1], array[i][j][0])
                #if i < 50 and rgb[i][j] == 2:
                #    rgb[i][j] = 1
        #create masks according to rbg array
                    
        red_mask = (rgb == 3)
        green_mask = (rgb == 4)
        blue_mask = (rgb == 5)
        black_mask = (rgb == 2)
        white_mask = (rgb == 1)
        gray_mask = (rgb == 0)

        return [red_mask, green_mask, blue_mask, black_mask, white_mask, gray_mask]


    def find_contours(self,mask, img, min_area = 100, max_area = 20000, draw = False, rect_color=(0,0,255), label = None) :
        """
        Finds and filter contours on masks depending on the min_area.
        Returns a list of ColorDetected objects for each filtered contour
        .. warning:: 
            Only works with real robots
        
        """
        
        binary = mask.astype(np.uint8)*255

        binary = self.mask_cleanup(binary)

        # find contours
        contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # filter contours
        filtered_contours = []
        for c in contours :
            area = cv2.contourArea(c)
            if area > min_area and area < max_area :
                filtered_contours.append(c)

        img_copy = np.copy(img)
        
        # draw contours
        if draw : 
            cv2.drawContours(img_copy, filtered_contours, -1, (0,255,0), 1)

        objects = []
        for cnt in filtered_contours:
            rect = cv2.boundingRect(cnt)
            x,y,w,h = rect
            c_x = x + (w / 2)
            c_y = y + (h / 2)            
            cv2.rectangle(img_copy,(x,y),(x+w,y+h),rect_color,2)

            objects.append(ColorDetected(x_center=c_x, y_center=c_y, width=w, height=h, area=cv2.contourArea(cnt), label=label))

        return objects, img_copy






    def get_colordetection(self,img = None, min_area = 100, saveimg = False, savemasks = False, filename = None) :

        img_copy = img.transpose(1,2,0).astype(np.uint8).copy()
        bgr_img = cv2.cvtColor(img_copy, cv2.COLOR_RGB2BGR)
                
        cv2.imwrite('./img/feed.bmp',bgr_img)
        
        # TODO replace Ali's detection with opencv masks
        #masks = [r,g,b,k,w,j] = self.detect_color_masks(img, 15, 49)
        masks = [r,g,b,k,w,j] = self.detect_color_masks_alt(bgr_img)

        
        allcontours = []

        rect_colors = [(255,0,0),(0,255,0),(0,0,255),(0,0,0)]
        labels = ['Blue','Green','Red','Black']

        img_cont = bgr_img
        for i,m in enumerate([b,g,r,k]) :
            contours,img_cont = self.find_contours(m, img_cont, rect_color=rect_colors[i], label=labels[i], min_area=min_area)
            allcontours = allcontours + contours
            
        if not filename:
            filename = self.get_id()     
             
        if not '.bmp' in filename:
            filename+='.bmp'

        if saveimg :
            cv2.imwrite(self.__save_image_folder+'/'+'colordetection_'+filename,img_cont)

        if savemasks :

            colors_img = []
            out_colors = [(0,0,255),(0,255,0),(255,0,0),(0,0,0),(255,255,255),(150,150,150)]
            bg_colors = [(255,255,255),(255,255,255),(255,255,255),(255,255,255),(50,50,50),(255,255,255)]

            allmasks = np.zeros_like(bgr_img)
            for i,m in enumerate(masks):
                allmasks = allmasks + self.color_img_from_mask(m,out_colors[i],(0,0,0))

            cv2.imwrite(self.__save_image_folder+'/'+'colordetection_masks_'+filename,allmasks)

        return allcontours
        

    def save_colordetection(self,img = None, min_area = 100, savemasks = True, filename = None) :

        if not filename:
            counter = '{:04d}'.format(self.__counter_colordetec_img)
            self.__counter_colordetec_img += 1

            self.get_colordetection(img, min_area = min_area, saveimg = True, savemasks = savemasks, filename = self.get_id()+'_'+counter)

        else :
            self.get_colordetection(img, min_area = min_area, saveimg = True, savemasks = savemasks, filename = self.get_id())


    def live_colordetection(self,img = None, min_area = 100, savemasks = True) :
    
        if (not img) :
            img = self.get_camera()
            img = np.array(img)
            
        self.get_colordetection(img, min_area = min_area, saveimg = True, savemasks = savemasks, filename = self.get_id())

                
                
                
