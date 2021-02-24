Wrapper
------------


About
========
The wrapper lets you get an instance of an e-puck robot.


Code
==========

.. automodule:: unifr_api_epuck.wrapper
    :members:
    :member-order: bysource
    

Examples
==========

* To get an instance of a real e-puck with its ip address:

.. code-block:: python

    from unifr_api_epuck import wrapper 

    my_robot = wrapper.get_robot('192.168.43.125')


* To get an instance of a simulated e-puck in Webots:

.. code-block:: python

    from unifr_api_epuck import wrapper

    my_robot = wrapper.get_robot()



* To get an instance of the e-puck from the pi-puck (soon available)

.. code-block:: python

    from unifr_api_epuck import wrapper

    #ip address of the pi-puck
    my_robot = wrapper.get_robot('192.168.43.11', is_pipuck = True)

