import socket, time, sys
from multiprocessing.managers import SyncManager
from multiprocessing import Lock

SyncManager.register("syncdict")
SyncManager.register("lock")

def start_manager_gui(ip_addr):
    """
    To start the manager from GUI for communication between the Epucks.
    :param ip_addr: ip_address of where to create host communication.
    """
    manager = EpuckCommunicationManager(True, ip_addr)
    success = manager.start()
    if not success:
        sys.exit(1)


def get_available_clients(connected_dict):
    list_clients = []
    for client, client_is_alive in connected_dict.items():
        if client_is_alive:
            list_clients += [client]

    return list_clients


def start_life_manager(host_ip):
    is_online = 1
    time_fail = time.time() + 3

    #create a socket to network
    try:
        while not (is_online == 0):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            is_online = sock.connect_ex((host_ip, 50000))

            if time_fail < time.time():
                print('No communication for life_points manager. Not connected to host manager.')

                if not host_ip:
                    print(
                        'Please create a GUI host by executing on your terminal: `python3 -m unifr_api_epuck`')

                # exit method
                return
    except:
        return

    # connecting to host manager
    is_connect = False
    lock = None
    syncdict = None

    while not is_connect:
        try:
            # connect to host ip
            manager = SyncManager((host_ip, 50000), authkey=b"abc")
            manager.connect()
            print('life manager connected to host IP!')
            # get shared dictionnary of host
            lock = manager.lock()
            syncdict =  manager.syncdict()
            if lock and syncdict:
                is_connect = True
        except Exception as e:
            print(e)
            

    host_alive = True
    start_time = time.time()
    last_timestamp = start_time
    thresh_time = start_time
    
    #loop until exit program
    while host_alive:
        try:

            if last_timestamp + 10 < time.time():
                last_timestamp = time.time()

                is_locked = lock.acquire(timeout=1)
                if is_locked:
                    tmp_dict = syncdict.copy()
                    tmp_connect_dict = tmp_dict['connected']
                    
                    number_alive = 0
                    for epuck, epuck_is_alive in tmp_connect_dict.items():
                        #has_start = True
                        if epuck_is_alive:
                            number_alive += 1
                            epuck_is_alive = False 
                        else:
                            tmp_dict[epuck] = []

                        tmp_dict['connected'][epuck] = epuck_is_alive
                        
                    if thresh_time + 10*60 < time.time():
                        thresh_time = time.time()
                        if number_alive == 0:
                            host_alive = False
                            print('host turn off')

        
                    syncdict.update(tmp_dict)
                    lock.release()
                    time.sleep(0.2)

        except Exception as e:
            print(e)

class EpuckCommunicationManager(SyncManager):
    """Singleton that host the communication between the robots.
    .. note:: An instance is created when a robot call init_communication() in the API Controller EPucks
    """

    def __init__(self, is_gui, ip_addr='localhost'):
        """
        :param ip_addr: ip_address of where to create host communication. (default : localhost)
        """
        
        self.ip_addr = ip_addr
        self.syncdict = {'connected':{}}
        self.lock = Lock()
        self.is_gui = is_gui
       

    def start(self):
        "start the host communication"
       
        try:    
            #check if port ised
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            is_online = sock.connect_ex((self.ip_addr, 50000))
        
            if is_online == 0:
                print('already online')
                
            else: 

                SyncManager.register("syncdict", self.get_dict)
                SyncManager.register("lock", self.get_lock) 
                
                self.manager = SyncManager((self.ip_addr, 50000), authkey=b"abc") 
                self.manager.start()
            
                start_life_manager(self.ip_addr)

            sock.settimeout(None)
        except OSError:
            print('Server already online')
            
            
        except Exception as e:
            return False

        return True  

    def get_dict(self):
        return self.syncdict

    def get_lock(self):
        return self.lock

    
def main(host_ip='localhost'):
    manager = EpuckCommunicationManager(False, host_ip)
    manager.start()
