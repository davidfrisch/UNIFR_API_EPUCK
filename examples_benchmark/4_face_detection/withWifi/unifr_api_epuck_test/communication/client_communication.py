#################
# COMMUNICATION #
#################
from multiprocessing.managers import SyncManager
import socket
import time, sys

SyncManager.register("syncdict")
SyncManager.register("lock")

class ClientCommunication:

    def __init__(self, ip_addr):
        # var for identification
        self.ip_addr = ip_addr
        self.id = 'computer_'+ip_addr.replace('.', '_')
        
        self.host = None
        self.manager = None

        self.MAX_MESSAGE = 30

       
    def get_id(self):    
        return self.id

    def init_client_communication(self, host_ip='localhost'):
        """
        .. warning:: The host should be created first before calling this method. (ref. Examples/Communication)
        """
       
        is_online = 1

        time_fail = time.time() + 10
        while is_online != 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            is_online = sock.connect_ex((host_ip, 50000))
            if time_fail < time.time():
                print('No communication for ' + self.get_id() +
                        '. Not connected to host manager.')
                if not host_ip:
                    print(
                        'Please create a GUI host by executing in your terminal: `python3 -m unifr_api_epuck`')

                # exit method
                self.clean_up()
                sys.exit(1)

        # connecting to host manager
        is_connect = False
        while not is_connect:
            try:
                # connect to host ip
                self.manager = SyncManager((host_ip, 50000), authkey=b"abc")
                self.manager.connect()
                print('CONNECT to host IP!')
                is_connect = True

                # get shared dictionnary of host
                self.lock = self.manager.lock()
                self.syncdict = self.manager.syncdict()

                self.lock.acquire(timeout=5)
                # adding its own id in the dictionnary and life points 
                tmp_dict = self.syncdict.copy()
                tmp_dict[self.get_id()] = []
                tmp_dict['connected'][self.get_id()] = True
                
                self.syncdict.update(tmp_dict)
                self.lock.release()

            except Exception as e:
                print(e)
                print('error in init_communication')
                print(self.get_id() + ' lost connection with host manager messages.')
                self.clean_up()
                sys.exit(1)

    def get_available_epucks(self):
        """
        Puts a message in queue to other robots
        :param msg: any 
        """
        # strictly subjective value to avoid overload

        if self.manager:
            try:
                self.lock.acquire(timeout=5)
                # we can only iterate on a copy
                current_dict = self.syncdict.copy()
                current_connected_list = [key for key in current_dict['connected'].keys()]

                self.lock.release()

                #remove computers clients from the list
                for key in current_connected_list:
                    if 'computer' in key:
                        current_connected_list.remove(key)
                
                return current_connected_list

                

            except Exception as e:
                print('error in get available epuck')
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')
 

    def stay_alive(self):
        """
        Keeps the host aware that the epuck is alive
        """
        if self.manager:
            try:
                self.lock.acquire(timeout=5)
                # must make a copy to get value from key
                current_dict = self.syncdict.copy()
                current_dict['connected'][self.get_id()] = True
                self.syncdict.update(current_dict)
                self.lock.release()
                
            except Exception as e:
                print('error in stay alive')
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


    def send_msg_to(self, dest, msg):
        if self.manager:
            try:
                self.lock.acquire(timeout=5)
                # we can only iterate on a copy
                current_dict = self.syncdict.copy()
                epuck_mailbox = current_dict[dest]
                epuck_mailbox.append(msg)
               
                # update the dictionnary
                current_dict.update({dest: epuck_mailbox})
              
                self.syncdict.update(current_dict)
                self.lock.release()

            except Exception as e:
                print('error in send_msg_to')                
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')

    
    def send_msg_all(self, msg):
        """
        Puts a message in queue to other robots
        :param msg: any 
        """
        # strictly subjective value to avoid overload
        if self.manager:
            try:
                self.lock.acquire(timeout=5)
                # we can only iterate on a copy
                current_dict = self.syncdict.copy()
                for epuck, epuck_mailbox in current_dict.items():

                    if epuck != self.get_id() and epuck != 'connected':

                        if len(epuck_mailbox) < self.MAX_MESSAGE and current_dict['connected'][epuck]:
                            epuck_mailbox.append(msg)

                        # update the dictionnary
                        current_dict.update({epuck: epuck_mailbox})

                self.syncdict.update(current_dict)
                self.lock.release()

            except Exception as e:
                print('error in send_msg_all')
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


    def has_receive_msg(self):
        """
        :returns: True if the robot has pending messages in his queue otherwise False.
        """
        if self.manager:
            try:
                self.lock.acquire(timeout=5)

                # must make a copy if we want to acces via key
                current_dict = self.syncdict.copy()
                epuck_array = current_dict[self.get_id()]

                # Check if array is empty
                has_msg = len(epuck_array) > 0
                self.lock.release()

                return has_msg

            except Exception as e:
                print('error in has_receive_msg')                
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


    def receive_msg(self):
        """
        Get next message from the robot queue otherwise returns None.
        """
        if self.manager:

            try:
                if self.has_receive_msg():
                    self.lock.acquire(timeout=5)
                    # must make a copy to get value from key
                    current_dict = self.syncdict.copy()
                    recv_mess = current_dict[self.get_id()].pop(0)
                    self.syncdict.update(
                        {self.get_id(): current_dict[self.get_id()]})
                    self.lock.release()
                    return recv_mess
         
            except Exception as e:
                print('error in receive_msg')                
                print(e)
                print(self.get_id() + ' lost connection with host manager messages.')


        return None

    def clean_up(self):pass