#################
# COMMUNICATION #
#################
from multiprocessing.managers import SyncManager
import socket
import time, sys

SyncManager.register("syncdict")
SyncManager.register("lock")

class ClientCommunication:
    """
    Client Communication is a ready to go class that let you connect to the host communication of the package.
    """

    def __init__(self, client_id):
        # id for identification
        if ('.') in client_id:
            client_id = client_id.replace('.', '_')

        self.id = client_id
        
        self.host = None
        self.manager = None
        
        self.timeoutLock = 4
        self.MAX_MESSAGE = 30

       
    def get_id(self):
        """
        Get the id of the
        """
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

                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:
                    # adding its own id in the dictionnary 
                    tmp_dict = self.syncdict.copy()
                    tmp_dict[self.get_id()] = []
                    tmp_dict['connected'][self.get_id()] = True
                    
                    self.syncdict.update(tmp_dict)
                    self.lock.release()

           
            except Exception as e:
                print('error in init communication')
                print(e)
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
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:
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
                    
    

    def stay_alive(self):
        """
        Keeps the host aware that the epuck is alive
        """
        if self.manager:

            try:
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:# must make a copy to get value from key
                    current_dict = self.syncdict.copy()
                    current_dict['connected'][self.get_id()] = True
                    self.syncdict.update(current_dict)

                    self.lock.release()
                
            except Exception as e:
                print('error in stay alive')
                print(e)
                    


    def send_msg_to(self, dest_client_id, msg):
        """
        Send a message to a specific id client
        """
        if self.manager:
            try:
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:
                    # we can only iterate on a copy
                    current_dict = self.syncdict.copy()
                    epuck_mailbox = current_dict[dest_client_id]
                    epuck_mailbox.append(msg)
                
                    # update the dictionnary
                    current_dict.update({dest_client_id: epuck_mailbox})

                    # stay alive
                    current_dict['connected'][self.get_id()] = True
                    self.syncdict.update(current_dict)

                    self.lock.release()

            except Exception as e:
                print('error in send_msg_to')                
                print(e)
                    

    
    def send_msg(self, msg):
        """
        Puts a message in queue to all the robots except itself
        :param msg: any 
        """
        # strictly subjective value to avoid overload
        if self.manager:
            try:
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                # we can only iterate on a copy
                
                if is_locked:
                    current_dict = self.syncdict.copy()
                    for epuck, epuck_mailbox in current_dict.items():

                        if epuck != self.get_id() and epuck != 'connected':

                            if len(epuck_mailbox) < self.MAX_MESSAGE and current_dict['connected'][epuck]:
                                epuck_mailbox.append(msg)

                                # update the dictionnary
                                current_dict.update({epuck: epuck_mailbox})

                    # stay alive
                    current_dict['connected'][self.get_id()] = True

                    self.syncdict.update(current_dict)
                    self.lock.release()

            except Exception as e:
                print('error in send_msg')
                print(e)
                    


    def has_receive_msg(self):
        """
        :returns: True if the robot has pending messages in his queue otherwise False.
        """
        if self.manager:
            try:
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:
                    # must make a copy if we want to acces via key
                    current_dict = self.syncdict.copy()
                    epuck_array = current_dict[self.get_id()]

                    # Check if array is empty
                    has_msg = len(epuck_array) > 0

                    # stay alive
                    current_dict['connected'][self.get_id()] = True
                    self.syncdict.update(current_dict)
                
                    self.lock.release()

                    return has_msg

            except Exception as e:
                print('error in has_receive_msg')                
                print(e)
                    


    def receive_msg(self):
        """
        Get next message from the robots queue otherwise returns None.
        """
        if self.manager:
            recv_mess = None

            try:
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:
                    current_dict = self.syncdict.copy()

                    if len(current_dict[self.get_id()]) > 0:
                        recv_mess = current_dict[self.get_id()].pop(0)
                        current_dict.update(
                            {self.get_id(): current_dict[self.get_id()]})

                    # stay alive
                    current_dict['connected'][self.get_id()] = True
                    self.syncdict.update(current_dict)

                    self.lock.release()
                
         
            except Exception as e:
                print('error in receive_msg')                
                print(e)
                    

            
            return recv_mess

        return None

    def clean_msg(self):
        """
        Deletes all its pending messages
        """
        if self.manager:
            try:
                is_locked = self.lock.acquire(timeout=self.timeoutLock)
                
                if is_locked:
                    # we can only iterate on a copy
                    current_dict = self.syncdict.copy()
                    
                
                    # update the dictionnary
                    current_dict.update({self.get_id(): []})

                    # stay alive
                    current_dict['connected'][self.get_id()] = True
                    self.syncdict.update(current_dict)

                    self.lock.release()

            except Exception as e:
                print('error in send_msg_to')                
                print(e)
                    

    def clean_up(self):pass