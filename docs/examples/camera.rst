Camera
================

Getting started with the Camera

Goals 
--------

* Here, you will learn how to use the camera of the e-puck
* You will learn these functions : **get_camera()**, **take_picture()**, **live_camera()**
* You will briefly learn how to display images with the provided GUI

Get Red, Green, Blue Arrays
-----------------------------

Use the function **get_camera()** to get the rgb two dimensions tables

See the code below:

.. code-block:: python

    from unifr_api_epuck import wrapper
    import numpy as np 

    robot = wrapper.get_robot()

    my_working_directory = ''
    robot.init_camera(my_working_directory)

    while robot.go_on():
        colors = np.array(robot.get_camera())
        [r,g,b] = colors

        # get values of the pixel at position (3,5)
        ## with pixels in 2D
        print(colors[0][3][5],colors[1][3][5],colors[2][3][5])

        ## with individual rgb arrays in 2D
        print(r[3][5],g[3][5],b[3][5])

        ## with flatten the arrays
        print(r.flatten()[161],g.flatten()[161],b.flatten()[161])


Take a Picture
-----------------

Use the function **take_picture()** to save the current image.

Each picture will automatically have an unique name file on a single run.


.. warning::   
    A new run will overwrite previous images


.. code-block:: python

    from unifr_api_epuck import wrapper

    robot = wrapper.get_robot()

    my_working_directory = ''   #working directory where the picture will be saved
    robot.init_camera(my_working_directory)
    robot.sleep(1)              #give time to the robot to do a good initiation

    #take 10 pictures
    for _ in range(10):
        robot.go_on()           #go to next step
        robot.take_picture()    #save the picture 


Stream the images
--------------------

Use the function **live_camera()** to stream the images of the robot with the GUI

.. note::
    More information to launch the GUI in the Graphic User Interface section


.. code-block:: python

    from unifr_api_epuck import wrapper

    robot = wrapper.get_robot()

    my_working_directory = '/Users/THEMACBOOK/Desktop/images'
    robot.init_camera(my_working_directory)
    robot.sleep(1)

    while robot.go_on():
        robot.live_camera() #call it in each step

