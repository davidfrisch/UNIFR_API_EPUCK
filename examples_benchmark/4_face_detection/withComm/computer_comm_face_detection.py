import cv2 as cv
import time, json
from unifr_api_epuck_test import wrapper
import numpy as np

def get_diff(face , image_dim):
    (pos_face_x, pos_face_y, width, height)= face
    pos_face_x += width/2
    pos_face_y += height/2

    pos_center_y, pos_center_x = image_dim.shape[0]/2, image_dim.shape[1]/2
    
    diff_x =  pos_center_x - pos_face_x 
    diff_y =  pos_center_y - pos_face_y

    return diff_x, diff_y

def main():
    my_computer = wrapper.get_client('computer_192.168.224.24')
    my_computer.init_client_communication('192.168.224.24')
    while True:

        if my_computer.has_receive_msg():

            msg = my_computer.receive_msg()
            
            #epuck tells computer that its sending an image
            if msg == 'finish':
                print('program finish')
                break
            
            img = None
            if type(msg) is np.ndarray:
                img = msg
                #epuck tells computer that the image has been transfered
                print('image received')
                cv.imwrite('/Users/THEMACBOOK/Desktop/my_image.jpg', img)
                original_image = img
                grayscage_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)
                face_cascade = cv.CascadeClassifier("../haarcascade_frontalface_default.xml")
                detected_faces = face_cascade.detectMultiScale(grayscage_image, 1.3)
                print('finish detecting')
                epuck = my_computer.get_available_epucks()[0]

                if len(detected_faces)>0:
                    print('face detected')
                    diff_x, _ = get_diff(detected_faces[0], grayscage_image)
                    print(diff_x)
                    if diff_x < -10:
                        my_computer.send_msg_to(epuck, 'right')
                    elif diff_x > 10:
                        my_computer.send_msg_to(epuck, 'left')
                    else:
                        my_computer.send_msg_to(epuck, 'center')
                else:
                    my_computer.send_msg_to(epuck, 'nothing')
                    print('No face found in img')


                
  
  


if __name__ == "__main__":
    main()