============
README
============

link to read the docs : https://unifr-api-epuck.chack.app/index.html

Welcome to the UNIFR API EPUCK's documentation. 
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
    
    * Write some code in my_controller method with the instance of the robot in paramater.

    .. code-block:: python

        def my_controller(rob):
            #code here
            pass

    * In your main() method, call the my_controller method 

    .. code-block:: python

        def main():
            #ip_addresse_of_robot = None #if using Webots simulation
            ae.setup_robot(ip_addresse_of_robot, my_controller)


3. If you are:
    * In Real Life (IRL) run the following command in your terminal in the current directory
    
    .. code-block:: shell

        $ python3 my_controller_file.py [ip_adress_of_the_robot]

    * In Webots : ⏯  press play 

4. Graphic User Interface
    * A GUI is available in the pip package. To run it, please run the following command:
        
    .. code-block:: shell

        $ python -m unifr_api_epuck


Example Code
--------------

| Q: What does it do ?
| A: The Robot moves forward at a speed of 2, print its proximitors values and stream from its camera.

.. code-block:: python

    from unifr_api_epuck import api_epuck as ae
    import sys 

    def main_loop(rob):

        rob.set_speed(2)        #speed of the wheels 

        r.init_sensors()        #init the sensors for the proxies              
        rob.init_camera('./')   #save image in current directory

        #infinite loop 
        while rob.go_on():
            r.live_stream()     #live stream (you can watch the stream from the GUI !)
            print(r.get_prox()) #print the proximities values on the console

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
        
        ae.robot_setup(main_loop, ip_addr)  



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

        
    
