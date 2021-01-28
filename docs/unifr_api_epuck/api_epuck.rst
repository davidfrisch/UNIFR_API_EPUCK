API_EPUCK
------------


About
========


Code
========
api_epuck let's you get an intance of an epuck robot

.. automodule:: unifr_api_epuck.api_epuck
    :members:
    

Examples
==========

* Get instance of a real epuck with its ip address of '192.168.43.125'

.. code-block:: python

    from unifr_api_epuck import api_epuck 

    my_robot = api_epuck.get_robot('192.168.43.125')


* Get instance of a webots epuck 

.. code-block:: python

    from unifr_api_epuck import api_epuck

    my_robot = api_epuck.get_robot()




* Get instance of epuck from the PiPuck with the ip address of the PiPuck (soon available)

.. code-block:: python

    from unifr_api_epuck import api_epuck

    #ip address of the pi-puck
    my_robot = api_epuck.get_robot('192.168.43.11')

