Detected class
----------------

To represent an object detected on the picture, the model use an object of the class "Detected", which is composed of:

* **x_center**
* **y_center** 

Both double, they represent the coordinates of the center of the bounding box. x is the horizontal position between 0 and 160, and y the vertical position between 0 and 120. The origin is on the top left corner of the image.

* **width**
* **height**

Both double again, they represent the size of the bounding box. Combined with the center above, it allows to determine the position of the detected object on the picture

* **Confidence**

A double between 0 and 1, which represents the confidence of the model about this prediction, 1 being the best

* **label**

If the user is using the default trained weights, then the label will contain a string representing the block (Red Block, Green Block, Blue Block, Black Block, Black Ball, Epuck), or it will contains the class number if some custom weights are used. 

The function **get_detection()** return a list of Detected Object, which contains between 0 and N items depending on the number of objects found on the picture, so the code usually looks like: 

.. code-block:: python

    img = np.array(robot.get_camera())
    detection = robot.get_detection(img)

    for item in detection:

        #do something with each object found
        if item.label == "Blue Block":

            #do something with the blue block