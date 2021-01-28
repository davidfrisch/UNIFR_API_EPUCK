from .epuck_webots import WebotsEpuck 
from .epuck_wifi import WifiEpuck
from .epuck_pipuck import PiPuckEpuck


def get_robot(ip_addr=None, is_pipuck = False):
    """
    Get EPUCK instance

    .. note::
        Leave the parameters empty if you will be using Webots

    :params ip_addr: ip address of the EPUCK.
    :returns: instance of the EPUCK
    """

    if is_pipuck:
        #IP address of the rasberry PI
        return __get_robot_pipuck(ip_addr)

    if ip_addr != None:
        return __get_robot_wifi(ip_addr)

    return __get_robot_webot()


def __get_robot_wifi(ip_addr):
    """
    Return an Real Robot Epuck instance
    """
    print('initiating connection with ' + str(ip_addr))

    return WifiEpuck(ip_addr)


def __get_robot_webot():
    """
    Return a simulation Epuck instance
    """
    try:
        return WebotsEpuck()

    except ModuleNotFoundError:
        print(
            '\033[91m'+'You did not enter an IP address, Please launch the script from Webots.'+'\033[0m')
        print(
            '\033[91m'+'If you use a Pi-Puck, please put True in first parameter'+'\033[0m')

def __get_robot_pipuck(ip_addr):
    """
    Return a Real Robot Pi-puck instance
    """
    print('initiating connection with Pi-puck')
    return PiPuckEpuck(ip_addr)

def __robot_setup(ip_addr=None, main_loop=None, is_pipuck=False):
    """
    make possible tu run multiple robot with one 

    .. note:: 
        Leave empty the main_loop if you will be using a jupyter notebook.

    :params ip_addr: ip address of the EPUCK.
    :params main_loop: Robot code instructions during execution.
    """

    if not main_loop and ip_addr:
        rob = get_robot(ip_addr, main_loop=None, is_pipuck=is_pipuck)
        return rob

    if ip_addr:
        #Wifi robot instance
        rob = get_robot(ip_addr)
        main_loop(rob)

    elif main_loop:
        if is_pipuck:
            #PiPuck instance
            rob = get_robot(is_pipuck=True)
        else:
            #Webots instance
            rob = get_robot()

        main_loop(rob)

    else:
        print('No instance of robot created.')
