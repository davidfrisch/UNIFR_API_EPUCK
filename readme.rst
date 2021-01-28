============
README
============

link to read the docs : https://unifr-api-epuck.chack.app/index.html

Welcome to the UNIFR API EPUCK's github. 
Please find below the instructions to get started with the API.

Submitted by: David Frischer

Supervisor: Dr. Julien Nembrini

Requirements
--------------

*  Python3.x on your computer.
*  Webots or a real E-puck 


How To Start
-------------
1. How to install the package from your terminal
    .. code-block:: shell

        pip install unifr_api_epuck


2. How to implement a controller/python file
    * Import package
    
    .. code-block:: python

        from unifr_api_epuck import api_epuck as ae
    
    * Create the the instance of the robot 

    .. code-block:: python
    
        MY_IP = None #leave None if using Webots, put IP address if using real robot
        r = ae.get_robot(MY_IP)

    * control the robot by calling its possilble actions 

    .. code-block:: python

        r.init_sensors() #init the sensors
        r.set_speed(-2, 2) #make it turn around himself

        #infinite loop
        while r.go_on():
            prox_values = r.get_prox() #get the proximity values
            print(prox_values)

        r.clean_up() #make a fresh clean_up


3. If you are:
    * In Real Life (IRL) run your python file in your CLI
    
    .. code-block:: shell

        $ python3 my_controller_file.py 

    * In Webots : ⏯  press play 

4. Graphic User Interface
    * A GUI is available in the pip package. To run it, please run the following command:
        
    .. code-block:: shell

        $ python3 -m unifr_api_epuck


Example Code
--------------

| Q: What does it do ?
| A: The Robot goes forward at a speed of 2, print its proximitors values and stream from its camera.

.. code-block:: python

    from unifr_api_epuck_test import api_epuck as ae
    import sys

    def main_loop(ip_addr):
        rob = ae.get_robot(ip_addr)
        rob.set_speed(2)        #speed of the wheels

        rob.init_sensors()        #init the sensors for the proxies
        rob.init_camera('./')     #save image in current directory

        #infinite loop
        while rob.go_on():
            rob.live_camera()     #live stream (you can watch the stream from the GUI !)
            print(rob.get_prox()) #print the proximities values on the console

            #insert some more code here to control rob (your robot)



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
        
    
