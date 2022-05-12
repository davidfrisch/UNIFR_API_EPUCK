from unifr_api_epuck import wrapper

my_computer = wrapper.get_client(client_id='MyUniqueName', host_ip='http://127.0.0.1:8000')

while(True):
    if(my_computer.has_receive_msg()):
        msg = my_computer.receive_msg()
        print(msg)
        
  