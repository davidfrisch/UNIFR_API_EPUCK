EPUCK (Abstract class)
------------------------

Table Of Contents
====================

* :ref:`Constants<Constants>`
* :py:meth:`Motors<unifr_api_epuck.epuck.Epuck.set_speed>`
* :py:meth:`LED<unifr_api_epuck.epuck.Epuck.toggle_led>`
* :py:meth:`Proximity Sensors<unifr_api_epuck.epuck.Epuck.init_sensors>`
* :py:meth:`Ground Sensors<unifr_api_epuck.epuck.Epuck.init_ground>`
* :py:meth:`Camera<unifr_api_epuck.epuck.Epuck.init_camera>`
* :py:meth:`Communication<unifr_api_epuck.epuck.Epuck.init_client_communication>`
* :py:meth:`Time Of Flight<unifr_api_epuck.epuck.Epuck.get_tof>`
* :py:meth:`Gyroscope<unifr_api_epuck.epuck.Epuck.get_gyro>`
* :py:meth:`Accelerometer<unifr_api_epuck.epuck.Epuck.get_accelerometer>`
* :py:meth:`Microphones<unifr_api_epuck.epuck.Epuck.get_microphones>`
* :py:meth:`Play Sound<unifr_api_epuck.epuck.Epuck.play_sound>`


Constants
===========
.. code-block:: python

   # Constants for any EPUCK.
   TIME_STEP = 64

   MAX_SPEED_WEBOTS = 7.536
   MAX_SPEED_IRL = 800     #In Real Life

   NBR_CALIB = 50

   LED_COUNT_ROBOT = 8

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
=====

.. automodule:: unifr_api_epuck.epuck
    :members:
    

