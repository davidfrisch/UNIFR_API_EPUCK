Global Constants  
------------------

The following constants are available by calling it with its instance.

.. code-block:: python

   from unifr_api_epuck import wrapper

Following constants are available :

.. code-block:: python

   robot = wrapper.get_robot()

   robot.MAX_SPEED = 7.536

   robot.NBR_CALIB = 50
   robot.OFFSET_CALIB = 5


   robot.LED_COUNT_ROBOT = 8


   robot.PROX_SENSORS_COUNT = 8
   robot.PROX_RIGHT_FRONT = 0
   robot.PROX_RIGHT_FRONT_DIAG = 1
   robot.PROX_RIGHT_SIDE = 2
   robot.PROX_RIGHT_BACK = 3
   robot.PROX_LEFT_BACK = 4
   robot.PROX_LEFT_SIDE = 5
   robot.PROX_LEFT_FRONT_DIAG = 6
   robot.PROX_LEFT_FRONT = 7

   robot.GROUND_SENSORS_COUNT = 3
   robot.GS_LEFT = 0
   robot.GS_CENTER = 1
   robot.GS_RIGHT = 2

   robot.MAX_MESSAGE = 30



