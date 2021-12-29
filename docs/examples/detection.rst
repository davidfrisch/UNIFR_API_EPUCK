Detection
================

Using the object detection capabilities of the robot

Goals 
--------

* Here, you will learn how to use the implemented YOLO algorithm to recognize objects
* You will learn these functions : **get_detection()**, **save_detection()**, **live_detection()**
* You will briefly learn how to display images with the provided GUI

Detected class
----------------

To represent an object detected on the picture, the model use an object of the class "Detected", which is composed of:

* **x_center**
* **y_center** 

Both double, they represent the coordinates of the center of the bounding box

* **width**
* **height**

Both double again, they represent the size of the bounding box. Combined with the center above, it allows to determine the position of the detected object on the picture

* **Confidence**

A double between 0 and 1, which represents the confidence of the model about this prediction, 1 being the best

* **label**

If the user is using the default trained weights, then the label will contain a string representing the block (Red Block, Green Block, Blue Block, Black Block, Black Ball, Epuck), or it will contains the class number if some custom weights are used. 


Get the detection
------------------

Use the function **get_detection(img)** where we give the RGB array obtained from **get_camera()** as input 

The output will be a list of "Detected" objects, from 0 to N objects detected on the picture.

See the code below:

.. code-block:: python

    from unifr_api_epuck import wrapper
    import numpy as np 

    robot = wrapper.get_robot()

    my_working_directory = ''
    robot.init_camera(my_working_directory)
    robot.initiate_model()

    while robot.go_on():
        
        img = np.array(robot.get_camera())  
        detection = robot.get_detection(img)
        
        #check all the detected objects on that picture
        for object in detection:
            if object.label == "Epuck":
                robot.enable_all_led()


Take a Picture with the bounding boxes drawn
--------------------------------------------

Use the function **save_detection(filename)** to save the current image with the bounding boxes.

Each picture will automatically have an unique name file on a single run, or it can be set arbitrarly with the filename parameter


.. warning::   
    A new run will overwrite previous images


.. code-block:: python

    from unifr_api_epuck import wrapper

    robot = wrapper.get_robot()
    robot.initiate_model()

    my_working_directory = ''   #working directory where the picture will be saved
    robot.init_camera(my_working_directory)
    robot.sleep(1)              #give time to the robot to do a good initiation

    counter = 0

    #take 10 pictures
    while robot.go_on() and counter < 10:
        
        robot.save_detection()    #save the picture 
        counter += 1


Stream the images with annotations
----------------------------------

Use the function **live_detection()** to stream the images of the robot with the GUI, with the annotated images

.. note::
    More information to launch the GUI in the Graphic User Interface section


.. code-block:: python

    from unifr_api_epuck import wrapper

    robot = wrapper.get_robot()
    robot.initiate_model()

    my_working_directory = '/Users/THEMACBOOK/Desktop/images'
    robot.init_camera(my_working_directory)
    robot.sleep(1)

    while robot.go_on():
        robot.live_detection() #call it in each step

