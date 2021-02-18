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

