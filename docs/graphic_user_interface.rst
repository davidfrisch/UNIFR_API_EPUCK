Graphic User Interface
============================


Main E-PUCK GUI Window
----------------------------

To start the main GUI from the unifr_api_epuck package, please run the following command in your terminal.

.. code-block:: shell

    $ python3 -m unifr_api_epuck

.. image:: res/gui_img_main.png
    :width: 400
    :alt: Picture of the main GUI Epuck
    
The Main E-PUCK GUI is capable to start a server hosting for the communication between the robots and/or start streaming the camera of an epuck.

The window is split in to two parts:

1. The first part is for creating or joining the communication.

    Two scenarios are possible :

    * If no hosting exists: you can create one by inserting the computer IP address in the input field.

    * If a host already exists: insert the IP address of the host to join and monitor the situation.

2.  The second part is to stream the camera of an E-puck.
    
    2.1 Insert the ip address of the robot to stream.

    2.2 Locate the folder where the pictures are saved from the robot.

    .. note:: 

        * To use this feature, the E-puck must be run by the same computer that streams the camera.

        * This should be the same path as rob.init_camera(`path`) of the Epuck 

    .. tip::

        First define the location from the GUI and then copy/paste the path into the init_camera(`path`) method in the controller code of the robot.


Also note that the GUI will create a .json file to save your inputs such that you don't have to insert them each time your launching the GUI. 😉



Monitor Host Communication
------------------------------

.. image:: res/gui_img_comm.png
    :width: 400
    :alt: Picture of the GUI communication between the Epucks

In this window, you will be able to :
 
* Monitor how many pending messages the E-pucks have.
* Send messages to robots.

If a robot lose the communication with the host, then it will disapear from the list and all its pending messages will be remove.


Camera Epuck
--------------

.. image:: res/gui_img_cam.png
    :width: 400
    :alt: Picture of the GUI camera of the Epucks

* You can move the slider to adjust the refresh rate of the stream.
* You can take a picture of the steam and it will save it on the same directory specified before.
* Copy/Paste the directory link 


