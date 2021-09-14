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
        'exchange_data':[],
        'take_image':[],
        'process_image':[]
        }

    start_time = time.time()
    r = wrapper.get_robot('192.168.50.89', is_pipuck=True)
    cam_width = 640
    cam_height = 480
    size = (cam_width,cam_height)
    r.init_camera('.')
    r.go_on()
    data['start_time']+=[time.time()-start_time]

   

    timer = time.time()
    CENTER_TOLERANCE = round(10 * cam_width / 160)
    while timer + 60 > time.time():
        start_time = time.time()
        r.go_on()
        data['exchange_data']+=[time.time()-start_time]

        print('start detecting')
        #give time to read to last image
        start_time = time.time()
        r.take_picture('pi_pic.jpg')
        data['take_image']+=[time.time()-start_time]

        start_time = time.time()
        original_image = cv.imread('pi_pic.jpg', cv.IMREAD_UNCHANGED)
        grayscage_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)
        face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")
        detected_faces = face_cascade.detectMultiScale(grayscage_image, 1.3)
        data['process_image'] += [time.time() - start_time]

        print('finish detecting')

        
        if len(detected_faces)>0:
            print('face detected')
            diff_x, _ = get_diff(detected_faces[0], grayscage_image)
            print(diff_x)
            if diff_x < -CENTER_TOLERANCE:
                r.set_speed(0.5,-0.5)
            elif diff_x > CENTER_TOLERANCE:
                r.set_speed(-0.5,0.5)
            else:
                r.set_speed(0)
        #give time to move according the feedback
        r.sleep(1)
        r.set_speed(0)
        r.go_on()

    print('finish')
    with open('640480_results_pi_solo_face_detection.txt', 'w') as json_file:
        json.dump(data, json_file)
        time.sleep(1)
        print('results sent sucessfully')
        os.system('scp "%s" "%s:%s"' % ('640480_results_pi_solo_face_detection.txt', 'THEMACBOOK@192.168.224.24', '/Users/THEMACBOOK/Desktop'))
        

        
if __name__ == "__main__":
    main()



