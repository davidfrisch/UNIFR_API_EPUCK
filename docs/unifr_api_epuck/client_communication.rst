Client Communication
------------------------

Example
========

This example shows how to use the client communication. The code below uses the wrapper to create an instance of a client communication to be able to send messages to the robots.

.. code-block:: python3

    from unifr_api_epuck import wrapper
    
    my_computer = wrapper.get_client('computer_192.168.112.24')
    my_computer.init_client_communication('192.168.112.24')

   

Code
=====
.. automodule:: unifr_api_epuck.communication.client_communication
    :members:
    :inherited-members:
    :member-order: bysource


