# https://github.com/yorkrobotlab/pi-puck/blob/master/python-library/
from .epuck import Epuck
from .constants import *
from .ft903 import FT903
from .epuck_pipuck_camera_configuration import main as main_cam_configuration
import sys
import struct
import subprocess
from smbus2 import SMBus, i2c_msg
from threading import Thread
import cv2

############################
## CONSTANTS FOR PI-Puck  ##
############################

ROBOT_I2C_CHANNEL = 4
PIPUCK_I2C_CHANNEL = 3

ROBOT_ADDR = 0x1F
LED_COUNT_PIPUCK = 3
GRAVITY_MPU9250 = 16384 # To be defined...1 g for 16 bits accelerometer
AK8963_XOUT_L = 0x03 # data
MPU9250_ADDRESS_AD1_0 = 0x68  # Device address when AD1 = 0
MPU9250_ADDRESS_AD1_1 = 0x69
TOF_VL53L0X_ADDRESS = 0x29
INT_STATUS = 0x3A
ACCEL_XOUT_H = 0x3B
TEMP_OUT_H = 0x41
GYRO_XOUT_H = 0x43
GYRO_CONFIG = 0x1B
SMPLRT_DIV = 0x19
NUM_SAMPLES_CALIBRATION = 20


I2C_COMMAND_PACKET_SIZE = (19+1) # Data + checksum.
I2C_SENSORS_PACKET_SIZE = (46+1) # Data + checksum.
I2C_GROUND_SENSOR_ADDRESS = 0x60  # Device address


class PiPuckEpuck(Epuck):

    def __init__(self, ip_addr):
        #TOF sensor reading 
        if not ip_addr:
            print('Attention, no IP address is defines for the Pi-Puck. \n'+
                    'Will not initiate communication with others if needed.')
        super().__init__(ip_addr)
        """
        A class used to represent a robot Real Robot.
        :param ip_addr: str - The IP address of the Epuck
        """
        # communication Robot <-> Rasberry Pi
        # communication Pipuck <--> Rasberry Pi
        self.robot_i2c_bus = None
        self.pipuck_i2c_bus = None

        # camera init specific for Real Robot
        self.camera = None
        self.camera_width = CAMERA_WIDTH
        self.camera_height = CAMERA_HEIGHT
        self.counter_img = 0
        self.camera_updated = False
        self.my_filename_current_image = ''

        #robot propeties
        self.i2c_command = bytearray([0] * I2C_COMMAND_PACKET_SIZE)
        self.sensors_data = bytearray([0] * I2C_SENSORS_PACKET_SIZE)
        self.prox_ir = [0]*8
        self.tof = None
        self.mic = [0]*4
        self.mot_steps = [0]*2

        
        ##imu 
        self.imu_addr = MPU9250_ADDRESS_AD1_0
        self.accData = bytearray([0] * 6)
        self.gyroData = bytearray([0] * 6)
        self.temperatureData = 0
        self.accOffset = [0] * 3
        self.gyroValue = [0] * 3
        self.gyroOffset = [0] * 3

        #camera
        self.stream_has_start = False
        self.stream_thread = None

        #microphone of PIPUCK
        self.start_time_record = None
        self.counter_sound = 0

       
        # start communication with pi-puck
        try:
            self.robot_i2c_bus = SMBus(ROBOT_I2C_CHANNEL)
            self.pipuck_i2c_bus = SMBus(PIPUCK_I2C_CHANNEL)
            self.__init_command()
            self.start_time = time.time()
        except Exception as e:
            print('Cannot connect with pi-puck. \nReason: '+ str(e))
            sys.exit(1)
        
        # Pipuck propeties
        ## capable of LEDs, ¿ micro and speaker ?
        self.ft903 = FT903(self.pipuck_i2c_bus)
       

   
    def __init_command(self):
        # Init the array containing the commands to be sent to the robot from pi-puck 
        #TODO Check.
        self.i2c_command[0] = 0		    # Left speed
        self.i2c_command[1] = 0         #
        self.i2c_command[2] = 0		    # Right speed
        self.i2c_command[3] = 0         
        self.i2c_command[4] = 0 		# Speaker sound
        self.i2c_command[5] = 0x0 	    # LED0, LED2, LED4, LED6 on/off flag
        self.i2c_command[6] = 0 		# LED1 red
        self.i2c_command[7] = 0		    # LED1 green
        self.i2c_command[8] = 0		    # LED1 blue
        self.i2c_command[9] = 0 		# LED3 red
        self.i2c_command[10] = 0		# LED3 green
        self.i2c_command[11] = 0		# LED3 blue
        self.i2c_command[12] = 0 	    # LED5 red
        self.i2c_command[13] = 0		# LED5 green
        self.i2c_command[14] = 0		# LED5 blue
        self.i2c_command[15] = 0        # LED7 red
        self.i2c_command[16] = 0		# LED7 green
        self.i2c_command[17] = 0		# LED7 blue
        self.i2c_command[18] = 0 		# Settings.

   

    # The chip has two alternative addresses based on the AD1 pin.
    def mpu9250_change_addr(self):
        if(self.imu_addr == MPU9250_ADDRESS_AD1_0):
            self.imu_addr = MPU9250_ADDRESS_AD1_1
        else:
            self.imu_addr = MPU9250_ADDRESS_AD1_0

    def get_id(self):
        return 'raspberry_'+ self.get_ip().replace('.','_')
        

    def get_ip(self):
        return self.ip_addr

    #############################
    ## COMMUNICATION METHODS   ##
    #############################

    def read_register(self, address, reg, count):
        data = None
        try:			
            # Read a block of 'count' bytes from address 'address', with an offset of 'reg'
            data = self.robot_i2c_bus.read_i2c_block_data(address, reg, count)
        except:
            print("read error")
            return None

        return data

    def write_reg_mpu9250(self, reg, data):
        trials = 0
        
        while trials < 2:
            try:
                self.robot_i2c_bus.write_i2c_block_data(self.imu_addr, reg, data)
            except:
                trials += 1
                self.mpu9250_change_addr()
                continue
            break
            
        if trials == 2:
            print("write error")
            return -1
        
        return 0

    def read_reg_mpu9250(self, reg, count):
        trials = 0
        data = None
        
        while trials < 2:
            try:			
                data = self.robot_i2c_bus.read_i2c_block_data(self.imu_addr, reg, count)
                #print(data)
            except:
                #print("trial = " + str(trials))
                trials += 1
                self.mpu9250_change_addr()
                continue
            break
        
        if trials == 2:
            print("read error")
            return None

        return data
 
    def go_on(self):
        #checksum before sending to the robot 
        checksum = 0
        for i in range(I2C_COMMAND_PACKET_SIZE-1):
            checksum ^= self.i2c_command[i]		
        self.i2c_command[I2C_COMMAND_PACKET_SIZE-1] = checksum

      
        #update sensors data and send to robot
        try:
            #send to robot
            write = i2c_msg.write(ROBOT_ADDR, self.i2c_command)

              #update accelartor data
            if self.accData:
                self.accData = self.read_reg_mpu9250(ACCEL_XOUT_H, 6)

            #update gyro data
            if self.gyroData:
                self.gyroData = self.read_reg_mpu9250(GYRO_XOUT_H, 6)
            
            #receive from robot
            read = i2c_msg.read(ROBOT_ADDR, I2C_SENSORS_PACKET_SIZE)
            self.robot_i2c_bus.i2c_rdwr(write, read)
            self.sensors_data = list(read)
        except Exception as e:
            self.set_speed(0)
            print(e)
            print('Program stopped')
            sys.exit(1)

       
        # Communication frequency @ 20 Hz.
        self.time_diff = time.time() - self.start_time
        
        if self.time_diff < 0.050 : 
            time.sleep(0.050 - self.time_diff)

        self.start_time = time.time()

        #check sum to be check once arrived from the robot
        checksum = 0
        for i in range(I2C_SENSORS_PACKET_SIZE - 1):
            checksum ^= self.sensors_data[i]

        #Should pass this if condition in each loop-
        if  checksum == self.sensors_data[I2C_SENSORS_PACKET_SIZE - 1]:
            return True

        print("wrong checksum ({0:#x} != {0:#x})\r\n".format(self.sensors_data[I2C_COMMAND_PACKET_SIZE - 1], checksum))
        return False

    def __set_speed_left(self, speed_left):
        speed_left = int(super().bounded_speed(speed_left)*100)

        # get the two's complement for neg values
        if speed_left < 0:
            speed_left = speed_left & 0xFFFF

        self.i2c_command[0] = speed_left & 0xFF  # LSByte
        self.i2c_command[1] = speed_left >> 8  # MSByte

    def __set_speed_right(self, speed_right):

        # *100 offset with Webots
        speed_right = int(super().bounded_speed(speed_right)*100)

        # get the two's complement for neg values
        if speed_right < 0:
            speed_right = speed_right & 0xFFFF

        self.i2c_command[2] = speed_right & 0xFF  # LSByte
        self.i2c_command[3] = speed_right >> 8  # MSByte

    def set_speed(self, speed_left, speed_right=None):
        # robot goes staight if user only put one speed
        if speed_right is None:
            speed_right = speed_left

        self.__set_speed_left(speed_left)
        self.__set_speed_right(speed_right)

    def get_speed(self):
        #TODO maybe use registers data instead of local data
        right_speed = (self.wifi_command[0] + self.wifi_command[1]*256)/100  # offset of 100 with Webots
        left_speed = (self.wifi_command[2] + self.wifi_command[3]*256)/100

        return [left_speed, right_speed]


    def get_motors_steps(self):
        #retrieve steps of robot
        for i in range(2):
            self.mot_steps[i] = self.sensors_data[41+i*2+1]*256 + self.sensors_data[41+i*2]
        
        return self.mot_steps

    def toggle_led(self, led_position, red=None, green=None, blue=None):
        if led_position in range(LED_COUNT_ROBOT):
            # LEDs in even position are not RGB
            if led_position % 2 == 0:

                if red or green or blue:
                    print('LED '+ led_position + ' is not RGB')

                self.i2c_command[5] = self.i2c_command[5] | 1 << (led_position//2)

            else:
                # led_position corresponding to the position in the self.i2c_command packet
                led_position = (led_position-1)*3//2 + 6

                # if RGB is not specified, we process it like a LED with no RGB
                if red != None and green != None and blue != None:

                    # lambda function to check if r,g,b are between 0 and 100
                    def between(color_val): return 0 <= color_val <= 100
                    in_rgb_range_values = list(
                        map(between, (red, green, blue)))

                    if all(in_rgb_range_values):
                        self.i2c_command[led_position] = red
                        self.i2c_command[led_position+1] = green
                        self.i2c_command[led_position+2] = blue
                    else:
                        # Inform what happend
                        for i in range(3):
                            color = {0: 'red', 1: 'green', 2: 'blue'}
                            if not in_rgb_range_values[i]:
                                print('color ' + color[i] + 'is not between 0 and 100')

                else:

                    self.i2c_command[led_position] = 15 & 0xFF  # red
                    self.i2c_command[led_position+1] = 0  # greeen
                    self.i2c_command[led_position+2] = 0  # blue

        elif led_position in range(8, 8+LED_COUNT_PIPUCK):
            led_position -= 8
            #color = str(red + green*256 + blue*256**2)
            print('hello')

            total_color = 0
            i = 0
            #int to 3bit
            for color in [red, green, blue]:
                if color > 0:
                    total_color += 2**i
                i+=1
            self.ft903.write_data_8(led_position, total_color)

    def disable_led(self, led_position):
        if led_position in range(LED_COUNT_ROBOT):

            if led_position % 2 == 0:
                led_position //= 2

                # mask will shift the correct bit in the byte for LEDs
                mask = ~(1 << led_position)
                self.i2c_command[5] = self.i2c_command[5] & mask

            else:

                # led_position corresponding to the position in the self.i2c_command packet
                led_position = (led_position-1)*3//2 + 6

                self.i2c_command[led_position] = 0x00
                self.i2c_command[led_position+1] = 0x00
                self.i2c_command[led_position+2] = 0x00

        else:
            print('invalid led position: ' + led_position + '. Accepts 0 <= x <= 7. LED stays ON.')
        

    ##### END ####
    #    LED     #
    ##############

    def get_prox(self):
        # 2 byte per sensor, odd position is LSB and even position is MSB
        # Equivalent way to compute as the wifi Epuck
        #retrieve prox data
        for i in range(PROX_SENSORS_COUNT):
                 #prox i    = MSB * 256                    + LSB
            self.prox_ir[i] = self.sensors_data[i*2+1]*256 + self.sensors_data[i*2]

        return self.prox_ir


   
    def get_ground(self):
        ground_data= self.read_register(I2C_GROUND_SENSOR_ADDRESS, 0, 6)
        ground_value = [0] * GROUND_SENSORS_COUNT

        ground_value[0] = (ground_data[1] + (ground_data[0]<<8))
        ground_value[1] = (ground_data[3] + (ground_data[2]<<8))
        ground_value[2] = (ground_data[5] + (ground_data[4]<<8))

        return ground_value

    def calibrate_gyro(self):
        self.toggle_all_led()
        samplesCount = 0
        gyroSum = [0 for _ in range(3)]
        # reset and send configuration first?
        for i in range(NUM_SAMPLES_CALIBRATION):
            self.gyroData = self.read_reg_mpu9250(GYRO_XOUT_H, 6)
            if(self.gyroData != None):
                gyroSum[0] += struct.unpack("<h", struct.pack("<BB", self.gyroData[1], self.gyroData[0]))[0]
                gyroSum[1] += struct.unpack("<h", struct.pack("<BB", self.gyroData[3], self.gyroData[2]))[0]
                gyroSum[2] += struct.unpack("<h", struct.pack("<BB", self.gyroData[5], self.gyroData[4]))[0]
                samplesCount += 1
                #print("gyro sums: x={0:>+6d}, y={1:>+6d}, z={2:>+6d} (samples={3:>3d})".format(gyroSum[0], gyroSum[1], gyroSum[2], samplesCount))
            time.sleep(0.050)
        self.gyroOffset[0] = int(gyroSum[0]/samplesCount)
        self.gyroOffset[1] = int(gyroSum[1]/samplesCount)
        self.gyroOffset[2] = int(gyroSum[2]/samplesCount)
        print("gyro offsets: x={0:>+5d}, y={1:>+5d}, z={2:>+5d} (samples={3:>3d})\n".format(self.gyroOffset[0], self.gyroOffset[1], self.gyroOffset[2], samplesCount))
        self.disable_all_led()
    
    def get_gyro_axes(self):
        gyroValue = [0 for _ in range(3)]
        gyroValue[0] = struct.unpack("<h", struct.pack("<BB", self.gyroData[1], self.gyroData[0]))[0] - self.gyroOffset[0]
        gyroValue[1] = struct.unpack("<h", struct.pack("<BB", self.gyroData[3], self.gyroData[2]))[0] - self.gyroOffset[1]
        gyroValue[2] = struct.unpack("<h", struct.pack("<BB", self.gyroData[5], self.gyroData[4]))[0] - self.gyroOffset[2]
        
        return gyroValue

    def calibrate_accelerometer(self):
        self.toggle_all_led()
        accSum = [0 for _ in range(3)]
        samplesCount = 0
        # reset and send configuration first?
        for i in range(NUM_SAMPLES_CALIBRATION):
            self.accData = self.read_reg_mpu9250(ACCEL_XOUT_H, 6)
            if(self.accData != None):
                accSum[0] += struct.unpack("<h", struct.pack("<BB", self.accData[1], self.accData[0]))[0]
                accSum[1] += struct.unpack("<h", struct.pack("<BB", self.accData[3], self.accData[2]))[0]
                accSum[2] += struct.unpack("<h", struct.pack("<BB", self.accData[5], self.accData[4]))[0] - GRAVITY_MPU9250 #!!!
                samplesCount += 1
                #print("acc sums: x={0:>+6d}, y={1:>+6d}, z={2:>+6d} (samples={3:>3d})\n".format(accSum[0], accSum[1], accSum[2], samplesCount))
            time.sleep(0.050)
        self.accOffset[0] = int(accSum[0]/samplesCount)
        self.accOffset[1] = int(accSum[1]/samplesCount)
        self.accOffset[2] = int(accSum[2]/samplesCount)
        self.disable_all_led()
        print("acc offsets: x={0:>+5d}, y={1:>+5d}, z={2:>+5d} (samples={3:>3d})\n".format(self.accOffset[0], self.accOffset[1], self.accOffset[2], samplesCount))

    
    def get_accelerometer(self):
        pass

    def get_accelerometer_axes(self):
        self.accData = self.read_reg_mpu9250(ACCEL_XOUT_H, 6)
        accValue = [0 for x in range(3)]
        accValue[0] = struct.unpack("<h", struct.pack("<BB", self.accData[1], self.accData[0]))[0] - self.accOffset[0]
        accValue[1] = struct.unpack("<h", struct.pack("<BB", self.accData[3], self.accData[2]))[0] - self.accOffset[1]
        accValue[2] = struct.unpack("<h", struct.pack("<BB", self.accData[5], self.accData[4]))[0] - self.accOffset[2]

        return accValue

    def get_temperature(self):
        #TODO
        pass

    #TODO pip3 install git+https://github.com/gctronic/VL53L0X_rasp_python
    def init_tof(self):
        """
        It is required to have the VL53L0X pacakage to be able to use the TOF sensor.
        """
        import VL53L0X as VL53L0X

        self.tof = VL53L0X.VL53L0X(i2c_bus=ROBOT_I2C_CHANNEL, i2c_address=TOF_VL53L0X_ADDRESS)
        self.tof.open()

        self.tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)
        timing = self.tof.get_timing()
        if timing < 20000:
            timing = 20000
        print("Timing %d ms" % (timing/1000))
    
    def get_tof(self):
        try:
            return self.tof.get_distance()
        except:
            print('You must call robot.init_tof(), to get values from the TOF sensors')

    def disable_tof(self):
        self.tof.stop_ranging()
        self.tof.close()

    def init_camera(self, save_image_folder=None, camera_rate=1):
        cam_init_thread = Thread(target=main_cam_configuration, args=())
        cam_init_thread.start()
        cam_init_thread.join()
        self.camera = cv2.VideoCapture(0)

    def disable_camera(self):
        self.camera.release()
        

    def get_camera(self):
        self.red, self.green, self.blue = [],[],[]
        success, frame = self.camera.read()
        if success:
            for i in range(CAMERA_WIDTH):
                for j in range(CAMERA_HEIGHT):
                    #BGR pixel with OPENCV
                    self.blue.append(frame[i][j][0])
                    self.red.append(frame[i][j][1])
                    self.green.append(frame[i][j][2])

            return self.red, self.green, self.blue
        return None,None,None

    def get_camera_read(self):
        """ 
            get camera.read() of openCV
        """
        return self.camera.read()

    def take_picture(self):
        start = time.time()
        ret, frame = self.camera.read()
        self.counter_img += 1
        cv2.imwrite(self.get_id()+"_image{0:04d}.jpg".format(self.counter_img), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        
        # Grabbing frequency @ 5 Hz.
        self.time_diff_cam = time.time() - start
        if self.time_diff_cam < 0.2:
            time.sleep(0.2 - self.time_diff_cam);


    # return front, right, back. left microphones
    #TODO To check array positions
    def get_microphones(self):
        #retrieve microphones data
        for i in range(4):
            #To be tested
            #self.mic[i] = struct.unpack("<h", struct.pack("<BB", sensor[i], sensor[i+1]))[0]
            self.mic[i] = self.sensors_data[32+i*2+1]*256+self.ensors_data[32+i*2]

        return self.mic

    def record_sound(self, duration):
        #stop the robot for recording
        left_speed, right_speed = self.get_speed()
        self.set_speed(0)
        self.go_on()

        #start recording
        rate = '16000'
        self.counter_sound += 1
        filename = "record{0:04d}".format(self.counter_sound)+"_from_"+self.get_id()+".wav"
        subprocess.run('arecord -Dmic_mono -c1 -r'+rate+' -fS32_LE -twav -d'+str(duration) +' '+filename)

        #retrieve speed
        self.set_speed(left_speed, right_speed)
        self.go_on()


    # TODO to be tested, seems funny for [4] = 0
    def play_mario(self):
        self.i2c_command[4] = 0
        

    def play_underworld(self):
        self.i2c_command[4] = 1
        

    def play_star_wars(self):
        self.i2c_command[4] = 2
        

    def clean_up(self):
        self.set_speed(0)
        if self.tof != None:
            self.disable_tof()

        for _ in range(10):
            self.go_on()