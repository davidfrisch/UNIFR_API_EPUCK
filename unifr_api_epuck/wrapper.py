from .epuck.epuck_webots import WebotsEpuck 
from .epuck.epuck_wifi import WifiEpuck

def get_robot(ip_addr=None, is_pipuck = False):
    """
    Get the instance of an e-puck

    .. note::
        Leave the parameters empty if you will be using Webots

    :params ip_addr: ip address of the e-puck
    :params is_pipuck: boolean

    :returns: instance of the e-puck
    """

    if is_pipuck:
        #IP address of the rasberry PI
        return __get_robot_pipuck(ip_addr)

    if ip_addr != None:
        return __get_robot_wifi(ip_addr)

    return __get_robot_webot()


def __get_robot_wifi(ip_addr):
    """
    Return the instance of a real e-puck instance
    """
    print('initiating connection with ' + str(ip_addr))

    return WifiEpuck(ip_addr)


def __get_robot_webot():
    """
    Return the instance of a simulated e-puck 
    """
    try:
        return WebotsEpuck()

    except ModuleNotFoundError:
        print(
            '\033[91m'+'You did not enter an IP address, Please launch the script from Webots.'+'\033[0m')
        print(
            '\033[91m'+'If you use a Pi-Puck, please put True in second parameter'+'\033[0m')

def __get_robot_pipuck(ip_addr):
    """
    Return the instance of real e-puck with a Pi-puck 
    """
    from .epuck.pi_puck.epuck_pipuck import PiPuckEpuck

    print('Initiating connection with Pi-puck')
    return PiPuckEpuck(ip_addr)


