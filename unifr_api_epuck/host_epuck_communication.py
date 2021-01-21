import socket, os
from multiprocessing.managers import SyncManager
from multiprocessing import Lock


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

   

class EpuckCommunicationManager(SyncManager):
    """Singleton that host the communication between the robots.
    .. note:: An instance is created when a robot call init_communication() in the API Controller EPucks
    """

    def __init__(self, is_gui, ip_addr='localhost'):
        """
        :params ip_addr: ip_address of where to create host communication. (default : localhost)
        """
        
        self.ip_addr = ip_addr
        self.syncdict = {}
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
                

                #open Monitor in a MAIN PYTHON THREAD !
                if not self.is_gui:
                    os.system("python3 gui_epuck_communication.py " + self.ip_addr + " " + str(os.getpid()))
                    print('Shutting down host')

        except OSError:
            print('Server already online')
            
        except Exception as e:
            print(e)


    def get_dict(self):
        return self.syncdict

    def get_lock(self):
        return self.lock

if __name__ == "__main__":
    manager = EpuckCommunicationManager('localhost')
    manager.start()
    