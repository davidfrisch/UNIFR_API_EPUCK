import socket, time
from multiprocessing.managers import SyncManager
from multiprocessing import Lock

MAX_COMM_LIFE_PTS = 100
WARNING_COMM_LIFE_TIME = 90
DAMAGE_PTS = 20
DEATH = 0

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
    manager.start()

def get_available_epucks(connected_dict):
    list_epucks = []
    for epuck, life_points in connected_dict.items():
        if life_points > 0:
            list_epucks += [epuck]

    return list_epucks


def start_life_manager(host_ip):
    is_online = 1

    time_fail = time.time() + 10
    while not (is_online == 0):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        is_online = sock.connect_ex((host_ip, 50000))
        if time_fail < time.time():
            print('No communication for life_points manager. Not connected to host manager.')

            if not host_ip:
                print(
                    'Please create a GUI host by executing on your terminal: `python3 -m unifr_api_epuck`')

            # exit method
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
            pass

    has_start = False
    alive = True
    
    while alive:
        lock.acquire()
        tmp_dict = syncdict.copy()

        if has_start and len(get_available_epucks(tmp_dict['connected'])) < 1 :
            alive = False

        old_dict = tmp_dict['connected']
        for epuck, life_pts in old_dict.items():
            
            has_start = True
            print(life_pts)

            if life_pts > DEATH:
                new_life_pts = life_pts - DAMAGE_PTS
                if life_pts > MAX_COMM_LIFE_PTS:
                    new_life_pts = MAX_COMM_LIFE_PTS   

            else:
                new_life_pts = 0
                tmp_dict[epuck] = []

            tmp_dict['connected'][epuck] = new_life_pts
            

           
        syncdict.update(tmp_dict)
        lock.release()
        time.sleep(1)

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
        #check if port ised
       
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        is_online = sock.connect_ex((self.ip_addr, 50000))
        
        #print('host communication ip address is: '+ self.ip_addr )
        
        try:    
            if is_online == 0:
                print('already online')
                
            else: 

                SyncManager.register("syncdict", self.get_dict)
                SyncManager.register("lock", self.get_lock) 
                
                self.manager = SyncManager((self.ip_addr, 50000), authkey=b"abc") 
                self.manager.start()
            
                start_life_manager(self.ip_addr)
           
                

        except OSError:
            print('Server already online')
            
        except Exception as e:
            print(e)


    def get_dict(self):
        return self.syncdict

    def get_lock(self):
        return self.lock

    
def main_hec(host_ip='localhost'):
    manager = EpuckCommunicationManager(False, host_ip)
    manager.start()

if __name__ == "__main__":
    host_ip = 'localhost'
    main_hec(host_ip)
    