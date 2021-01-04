API Epuck 
=================

About 
------
This is the main file to control the Epuck


Epuck
   __DirectEpuck

   __WebotsEpuck

Parent Epuck class only for communication, common methods and variables and communication purposes. 

Children __DirectEpuck and __WebotsEpuck hidden class which inherate from Epuck class.


Constants
----------
.. code-block:: python

   #Equivalent constants for Webots and In Real Life (IRL) robots 

   MAX_SPEED = 6.9
   NBR_CALIB = 50

   LED_COUNT = 8

   OFFSET_CALIB = 5

   CAMERA_WIDTH = 160
   CAMERA_HEIGHT = 120
   CAMERA_RATE = 8

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


Code
------

.. automodule:: api_epuck
   :members:
   :undoc-members:
   :show-inheritance:
