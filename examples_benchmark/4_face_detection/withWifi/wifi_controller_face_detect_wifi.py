from unifr_api_epuck_test import wrapper
import os, time, json
import cv2 as cv


def get_diff(face, image_dim):
    (pos_face_x, pos_face_y, width, _)= face
    pos_face_x += width/2
    
    pos_center_y, pos_center_x = image_dim.shape[0]/2, image_dim.shape[1]/2
    
    diff_x =  pos_center_x - pos_face_x 
    diff_y =  pos_center_y - pos_face_y

    return diff_x, diff_y

#ip address of the Raspberrypi
def main():
    data = {
        'start_time':[],
        'exchange_data_with_image':[],
        'take_image':[],
        'process_image':[]
        }

    start_time = time.time()
    r = wrapper.get_robot('192.168.105.240')
    r.init_camera('.')
    r.go_on()
    data['start_time']+=[time.time()-start_time]

   

    timer = time.time()
    while timer + 50 > time.time():
        start_time = time.time()
        r.go_on()
        data['exchange_data_with_image']+=[time.time()-start_time]

        r.take_picture('wifi_pic.bmp')
        data['take_image']+=[time.time()-start_time]

        print('start detecting')
        #give time to read to last image
        start_time = time.time()
        original_image = cv.imread('wifi_pic.bmp', cv.IMREAD_UNCHANGED)
        grayscage_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)
        face_cascade = cv.CascadeClassifier("../haarcascade_frontalface_default.xml")
        detected_faces = face_cascade.detectMultiScale(grayscage_image, 1.3)
        data['process_image'] += [time.time() - start_time]

        print('finish detecting')

        #print(grayscage_image.shape)
        if len(detected_faces)>0:
            print('face detected')
            diff_x, _ = get_diff(detected_faces[0], grayscage_image)
            print(diff_x)
            if diff_x < -10:
                r.set_speed(0.5,-0.5)
            elif diff_x > 10:
                r.set_speed(-0.5,0.5)
            else:
                r.set_speed(0)

        
        #give time to move according the feedback
        r.sleep(0.5)
        r.set_speed(0)
        r.go_on()

    print('finish')
    with open('results_wifi_solo_face_detection.txt', 'w') as json_file:
        json.dump(data, json_file)
        print('results sent sucessfully')
        r.send_msg('finish')

        
if __name__ == "__main__":
    main()


