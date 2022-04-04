#################
# COMMUNICATION #
#################
import socketio
from queue import Queue
import time

class SocketClientCommunication:

    """
    Client Communication is a ready to go class that let you connect to the host communication of the package.
    """
    sio = socketio.Client()
    
    
    def __init__(self, client_id, host_ip='http://127.0.0.1:8000'):
        # id for identification

        if ('.') in client_id:
            client_id = client_id.replace('.', '_')

        self.id = client_id
        self.call_backs()
        try:
            if host_ip == 'localhost':
                host_ip = 'http://127.0.0.1:8000'
            self.sio.connect(host_ip)
        except Exception as e:
            print('No socket connection found')
            
        self.MAX_MESSAGE = 30
        self.box_message = Queue(self.MAX_MESSAGE)
        self.camera_delay = 1 # seconds
        self.last_time_send = time.time()

    def call_backs(self):
        @self.sio.event
        def connect():
            print('connected to socket server !')
            self.sio.emit('new_connection', {'new_robot': self.id})
    
        @self.sio.event
        def connect_error(err):
            print("socket connection abort!")

        @self.sio.event
        def who_is_alive():
            self.sio.emit('i_am_alive', {'id':self.id})

        @self.sio.event
        def broadcast(data):
            timestamp = int(time.time() * 1000)
            self.box_message.put(data)
            self.sio.emit('confirm_reception', {'timestamp':timestamp, 'id':self.id, 'msg': data, 'is_receiver': True })
            
        @self.sio.on(self.id+'_on_receive')
        def receive_private_message(data):
            print(data)
            timestamp = int(time.time() * 1000)
            self.box_message.put(data)
            self.sio.emit('confirm_reception', {'timestamp':timestamp, 'id':self.id, 'msg': data, 'is_receiver': True })


    def get_id(self):
        """
        Get the id of the
        """
        return self.id

    @sio.event
    def send_msg(self, msg):
            """
            :param msg: any 
            """
            self.sio.emit('broadcast', {'from':self.id, 'msg':msg})

    def get_available_epucks(self):
        """
        TODO To be implemented
        :param msg: any 
        """
        return None
                
    @sio.event
    def send_msg_to(self, dest_client_id, msg):
        """
        TODO Send a message to a specific id client
        """
        self.sio.emit('send_msg_to', {'from':self.id, 'to': dest_client_id, 'msg': msg})     


    def has_receive_msg(self):
        """
        TODO :returns: True if the robot has pending messages in his queue otherwise False.
        """
        return not self.box_message.empty()
                    

    def receive_msg(self):
        """
        TODO Get next message from the robots queue otherwise returns None.
        """
        return self.box_message.get(block=False)

    def clean_msg(self):
        """
        TODO Deletes all its pending messages
        """
        self.box_message = Queue(self.MAX_MESSAGE)
                    

    def stream_img(self, img):
        
        if self.camera_delay < time.time() - self.last_time_send:
            self.sio.emit('stream_img', {'id': self.get_id(), 'img': img}) 
            self.last_time_send = time.time()
        
        
    def send_init_camera(self):
        self.sio.emit('init_camera', {'id': self.get_id()})  
        
    def send_disable_camera(self):
        self.sio.emit('disable_camera', {'id': self.get_id()}) 
            