from .epuck import Epuck
from .models.helper import non_max_suppression,plot_detection
from .models.yolo import attempt_load
import struct
import socket
import sys
import time
import logging
import numpy as np
import torch
import os
import cv2


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


        # start communication with computer
        self.__tcp_init()
        self.__init_command()

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
                logging.error("Error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            except socket.OSError as err:
                self.__sock.close()
                logging.error("Error from " + ip_address + ":")
                logging.error(err)
                trials += 1
                continue
            except Exception as err:
                self.__sock.close()
                logging.error("Error from " + ip_address + ":")
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
                chunk = self.__sock.recv(min(msg_len - bytes_recd, 2048))
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

    def init_tof():
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

        if size != (None, None):
                print('Only sizable for pipuck')
                
        if new_image_folder:
            self.__save_image_folder = new_image_folder

        self.__my_filename_current_image = self.__save_image_folder + \
            '/'+self.get_id()+'_image_video.bmp'
        print(self.__my_filename_current_image)
        #print('camera enable')
        self.__command[1] = self.__command[1] | 1

    def disable_camera(self):
        # Set last bit to 0
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

            for _ in range(50):
                self.set_speed(0, 0)
                self.go_on()

            self.__sock.close()
        #print('Robot cleaned')

    
    

    ####################
    #    END DAVID     #
    ####################

    ####################
    #   DETECTION      #
    ####################
    
    #Call at the beginning of the session only
    def initiate_model(self,weights='best.pt'):
        global model
        
        # Initialize
        
        device = 'cpu'        
        weights = os.path.join(__location__, weights)
        
        # Load model
        
        model = attempt_load(weights, map_location=device)  # load FP32 model
        print("model initialized, ready to use")


    def get_detection(self,img = None):
        
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
        #img = torch.permute(img, (2, 0, 1)) #correct tensor shape
        
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
            
            det = det.numpy()

            x = (det[0] + det[2]) / 2
            y = (det[1] + det[3]) / 2
            w = det[2] - det[0]
            h = det[3] - det[1]
            
            conf = det[4]
            cls = choices.get(int(det[5]), 'default')
            
            rep.append(Detected(x_center=x,y_center=y,width=w,height=h,confidence=conf,label=cls))

        return rep

    #Take a picture, analyse it and save the anotated picture in the defined image folder
    def save_detection(self,filename = None):
        
        #Take the picture
        img = self.get_camera()
        img = np.array(img)

        #Get the detection
        detection = self.get_detection(img)

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

        else:
            self.disable_camera()
