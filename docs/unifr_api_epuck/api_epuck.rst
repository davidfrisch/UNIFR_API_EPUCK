api_epuck
------------


About
========
The api_epuck file lets you get an instance of an e-puck robot.


Code
========

.. automodule:: unifr_api_epuck.api_epuck
    :members:
    :member-order: bysource
    

Examples
==========

* To get an instance of a real Epuck with its ip address:

.. code-block:: python

    from unifr_api_epuck import api_epuck 

    my_robot = api_epuck.get_robot('192.168.43.125')


* To get an instance of a simulated e-puck in Webots:

.. code-block:: python

    from unifr_api_epuck import api_epuck

    my_robot = api_epuck.get_robot()




* Get an instance of epuck from the pi-puck with the ip address of the PiPuck (soon available)

.. code-block:: python

    from unifr_api_epuck import api_epuck

    #ip address of the pi-puck
    my_robot = api_epuck.get_robot('192.168.43.11', is_pipuck = True)

