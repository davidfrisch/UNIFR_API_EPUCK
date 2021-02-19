api_epuck
------------


About
========
The api_epuck file lets you get an intance of an Epuck robot


Code
========

.. automodule:: unifr_api_epuck.api_epuck
    :members:
    :member-order: bysource
    

Examples
==========

* Get an instance of a real Epuck with its ip address. 
  e.g: IP is 192.168.43.125

.. code-block:: python

    from unifr_api_epuck import api_epuck 

    my_robot = api_epuck.get_robot('192.168.43.125')


* Get an instance of a simulated Epuck in Webots

.. code-block:: python

    from unifr_api_epuck import api_epuck

    my_robot = api_epuck.get_robot()




* Get an instance of epuck from the PiPuck with the ip address of the PiPuck (soon available)

.. code-block:: python

    from unifr_api_epuck import api_epuck

    #ip address of the pi-puck
    my_robot = api_epuck.get_robot('192.168.43.11', is_pipuck = True)

