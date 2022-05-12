Client Communication
------------------------

Example
========

This example shows how to use the client communication. The code below uses the wrapper to create an instance of a client communication to be able to send messages to the robots.

.. code-block:: python3

    my_computer = wrapper.get_client(client_id='MyUniqueName', host_ip='http://127.0.0.1:8000')

    while(True):
        if(my_computer.has_receive_msg()):
            msg = my_computer.receive_msg()
            print(msg)

Code
=====
.. automodule:: unifr_api_epuck.communication.socket_client_communication
    :members:
    :inherited-members:
    :member-order: bysource


