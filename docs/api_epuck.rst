API Epuck 
=================

About 
------
This is the main file to control the Epuck

code structure :

Epuck (Parent class)
   __DirectEpuck (Child class)

   __WebotsEpuck (Child class)

Table Of Contents
********************

* :ref:`Constants<Constants>`
* :py:meth:`Motors<api_epuck.Epuck.set_speed>`
* :py:meth:`LED<api_epuck.Epuck.toggle_led>`
* :py:meth:`Proximity Sensors<api_epuck.Epuck.init_sensors>`
* :py:meth:`Ground Sensors<api_epuck.Epuck.init_ground>`
* :py:meth:`Camera<api_epuck.Epuck.init_camera>`
* :py:meth:`Communication<api_epuck.Epuck.init_communication>`
* :py:meth:`Time Of Flight<api_epuck.Epuck.get_tof>`
* :py:meth:`Ambient Light Sensors<api_epuck.Epuck.init_lights>`
* :py:meth:`Gyroscope<api_epuck.Epuck.get_gyro>`
* :py:meth:`Accelerometer<api_epuck.Epuck.get_accelerometer>`
* :py:meth:`Microphones<api_epuck.Epuck.get_microphones>`
* :py:meth:`Magnetometer<api_epuck.Epuck.get_magnetometer>`
* :py:meth:`Play Sound<api_epuck.Epuck.play_sound>`


Constants
----------
.. code-block:: python

   #Equivalent constants for Webots and In Real Life (IRL) robots 
   
   TIME_STEP = 64

   MAX_SPEED = 6.9
   NBR_CALIB = 50

   LED_COUNT = 8

   OFFSET_CALIB = 5

   CAMERA_WIDTH = 160
   CAMERA_HEIGHT = 120

   PROX_SENSORS_COUNT = 8

   PROX_RIGHT_FRONT = 0
   PROX_RIGHT_FRONT_DIAG = 1
   PROX_RIGHT_SIDE = 2
   PROX_RIGHT_BACK = 3
   PROX_LEFT_BACK = 4
   PROX_LEFT_SIDE = 5
   PROX_LEFT_FRONT_DIAG = 6
   PROX_LEFT_FRONT = 7

   GROUND_SENSORS_COUNT = 3
   GS_LEFT = 0
   GS_CENTER = 1
   GS_RIGHT = 2

   MAX_MESSAGE = 30




Code
------

.. automodule:: api_epuck
   :members:
   :undoc-members:
   :show-inheritance:


* :ref:`Constants<Constants>`
* :py:meth:`Motors<api_epuck.Epuck.set_speed>`
* :py:meth:`LED<api_epuck.Epuck.toggle_led>`
* :py:meth:`Proximity Sensors<api_epuck.Epuck.init_sensors>`
* :py:meth:`Ground Sensors<api_epuck.Epuck.init_ground>`
* :py:meth:`Camera<api_epuck.Epuck.init_camera>`
* :py:meth:`Communication<api_epuck.Epuck.init_communication>`
* :py:meth:`Time Of Flight<api_epuck.Epuck.get_tof>`
* :py:meth:`Ambient Light Sensors<api_epuck.Epuck.init_lights>`
* :py:meth:`Gyroscope<api_epuck.Epuck.get_gyro>`
* :py:meth:`Accelerometer<api_epuck.Epuck.get_accelerometer>`
* :py:meth:`Microphones<api_epuck.Epuck.get_microphones>`
* :py:meth:`Magnetometer<api_epuck.Epuck.get_magnetometer>`
* :py:meth:`Play Sound<api_epuck.Epuck.play_sound>`






