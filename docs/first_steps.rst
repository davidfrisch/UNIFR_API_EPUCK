============
First Steps
============

Welcome to the UNIFR API e-puck's documentation. 

unifr_epi_epuck is a simple API wrapper that lets you control a real or simulated e-puck robot. 
Please find below the instructions to get started with the API using Python3.

Submitted by: David Roman Frischer

Supervisor: Dr. Julien Nembrini

github : https://github.com/davidfrisch/UNIFR_API_EPUCK

Requirements
--------------

*  Python3.x on your computer.
*  Webots or a real e-puck.


How To Start
-------------
1. How to install the package from your terminal.
    .. code-block:: shell

        $ pip install unifr_api_epuck


2. How to implement using Python.
    * To import the package:
    
    .. code-block:: python

        from unifr_api_epuck import api_epuck as ae
    
    * To create an instance of the robot:

    .. code-block:: python
    
        #leave None if you're using Webots. 
        #Put an IP address if you're using a real robot.
        MY_IP = None 
        r = ae.get_robot(MY_IP)

    * To control the robot by calling its actions:

    .. code-block:: python

        r.init_sensors() #initiates the sensors
        r.set_speed(-2, 2) #makes it turn around itself

        #infinite loop
        while r.go_on():
            prox_values = r.get_prox() #gets the values of the proximity sensors
            print(prox_values)

        r.clean_up() #makes a reset


3. To run the file, if you are:
    * In Real Life (IRL) run your Python file with the following command:
    
    .. code-block:: shell

        $ python3 my_controller_file.py 

    * In Webots : ⏯  press play 

4. Graphic User Interface
    * A GUI is available in the package. To start it, please run the following command:
        
    .. code-block:: shell

        $ python3 -m unifr_api_epuck


Example Code
--------------

| Q: What does it do ?
| A: The robot goes forward at a speed of 2, prints its proximitiy sensor values and streams images from its camera.

.. code-block:: python

    from unifr_api_epuck_test import api_epuck as ae
    import sys

    def main_loop(ip_addr):
        rob = ae.get_robot(ip_addr)
        rob.set_speed(2)        #sets the speed of the wheels

        rob.init_sensors()        #initiates the proximity sensor
        rob.init_camera('./')     #initiates the camera. It will save the image in './'

        #infinite loop
        while rob.go_on():
            rob.live_camera()     #live stream (you can watch the stream from the GUI !)
            print(rob.get_prox()) #prints the proximity sensor values on the terminal

            #inserts some more code here to control your robot

        rob.clean_up()

    if __name__ == "__main__":

        ip_addr = None

        """
        if arguments in the command line --> IRL
        leave empty if using Webots
        """

        if len(sys.argv) == 2:
            ip_addr = sys.argv[1]


        main_loop(ip_addr)



Sources
---------

Wifi Protocol between Robot <--> computer
    https://www.gctronic.com/doc/index.php?title=e-puck2_PC_side_development#WiFi_2

    http://projects.gctronic.com/epuck2/complete.py
    
    https://github.com/nembrinj/epuckAPI/tree/master

Webots 
    https://www.cyberbotics.com/doc/reference/nodes-and-api-functions

Multiprocess
    https://docs.python.org/3/library/multiprocessing.html#multiprocessing.managers.SyncManager  

    https://stackoverflow.com/questions/2545961/how-to-synchronize-a-python-dict-with-multiprocessing

Socket errors
    https://docs.python.org/3/library/exceptions.html#OSError

Pi-Puck
    https://pi-puck.readthedocs.io/en/latest/
    
    https://github.com/yorkrobotlab/pi-puck
    
    https://github.com/gctronic/Pi-puck
        
    
