import socket, time, sys
from multiprocessing.managers import SyncManager
from multiprocessing import Lock

SyncManager.register("syncdict")
SyncManager.register("lock")

def start_manager(ip_addr):
    """
    To start the manager for communication between the Epucks.
    :param ip_addr: ip_address of where to create host communication.
    """
    manager = EpuckCommunicationManager(False, ip_addr)
    manager.start()
    


def start_manager_gui(ip_addr):
    """
    To start the manager from GUI for communication between the Epucks.
    :param ip_addr: ip_address of where to create host communication.
    """
    manager = EpuckCommunicationManager(True, ip_addr)
    success = manager.start()
    if not success:
        sys.exit(1)


def get_available_epucks(connected_dict):
    list_epucks = []
    for epuck, epuck_is_alive in connected_dict.items():
        if epuck_is_alive:
            list_epucks += [epuck]

    return list_epucks


def start_life_manager(host_ip):
    is_online = 1
    time_fail = time.time() + 3

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

    # connecting to host manage
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
            

    #has_start = False
    host_alive = True
    start_time = time.time()
    last_timestamp = start_time
    while host_alive:
        try:
            lock.acquire(timeout=1)
            tmp_dict = syncdict.copy()
            tmp_connect_dict = tmp_dict['connected']

            # automatically turn off host.
            #if has_start and len(get_available_epucks(tmp_connect_dict)) < 1 and last_timestamp + 600 < time.time():
            #    host_alive = False
                
            if last_timestamp + 5 < time.time():
                for epuck, epuck_is_alive in tmp_connect_dict.items():
                    #has_start = True
                    if epuck_is_alive:
                        epuck_is_alive = False 
                    else:
                        tmp_dict[epuck] = []

                    tmp_dict['connected'][epuck] = epuck_is_alive
                
                last_timestamp = time.time()
  
            syncdict.update(tmp_dict)
            lock.release()
            time.sleep(0.1)

        except Exception as e:
            print(e)

class EpuckCommunicationManager(SyncManager):
    """Singleton that host the communication between the robots.
    .. note:: An instance is created when a robot call init_communication() in the API Controller EPucks
    """

    def __init__(self, is_gui, ip_addr='localhost'):
        """
        :params ip_addr: ip_address of where to create host communication. (default : localhost)
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


if __name__ == "__main__":   
    start_manager('localhost') 