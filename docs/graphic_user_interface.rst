Graphic User Interface
============================

Index
------

1. :ref:`Home GUI Epuck<Home GUI Epuck>`
2. :ref:`Communication Manager Epuck<Communication Manager Epuck>`
3. :ref:`Camera Epuck<Camera Epuck>`


Home GUI Epuck
-----------------

To start the main GUI from the pip unifr_api_epuck package please run the following in your terminal.

.. code-block:: shell

    python -m unifr_api_epuck

.. image:: res/gui_img_main.png
    :width: 400
    :alt: Picture of the main GUI Epuck
    

1. This is the entry point to create or join a host communication manager where Epucks can communicate between them.

    * If no host manager is created and you insert localhost (or empty field), the GUI will create a host manager such that the robots can communicate between them. 

    * If a host manager already exists, insert the IP address of where the host manager is running to join and monitor the pending messages.

    .. note::  
        It is strongly recommended to create the host manager from the GUI. This will give much more stability for communication between the robots.


2.  This is the entry point to stream the camera of an E-puck.
    
    2.1 Insert the ip address of the robot to stream.

    2.2 Locate the folder where the images are saved from the robot.

    .. note:: 

        * To use this feature, the E-puck must be communicating with the same computer that is streaming the computer

        * This should be the same path as init_camera(`path`) of the Epuck 

    .. tip::

        First define the location from the GUi and then copy/paste the path into the init_camera() method in your  controller code of the Epuck.


Also note that the GUI will create a json file to save your last 5 inputs in each field such that you don't have to insert them each time your launching the GUI 😉



Communication Manager Epuck
------------------------------

.. image:: res/gui_img_comm.png
    :width: 400
    :alt: Picture of the GUI communication between the Epucks

In this window, you will be able to monitor how many pending messages the E-pucks have.

If an epuck lose the communication with the host, then the robot will disapear from the list and all its pending messages will be erased.

Camera Epuck
--------------

.. image:: res/gui_img_cam.png
    :width: 400
    :alt: Picture of the GUI camera of the Epucks

* You can move the slider to adjust the refresh rate of the stream
* You can take a picture of the steam and it will save it on the same directory specified before.



