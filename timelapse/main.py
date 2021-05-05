import time
import cv2
import datetime as dt
from timelapse.utils import calculate_brightness, calculate_sharpness
from timelapse.camera import CameraProperties, Camera
from notify_run import Notify
notify = Notify()

import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='../timelapse.log', 
                    filemode='w', 
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logging.info('Started')

MIN_BRIGHTNESS = 90
MAX_BRIGHTNESS = 95

starttime = time.time()
notification_sent = False
properties = CameraProperties(width=1280, height=720, exposure=15)

while True:
    logging.info('New iteration ----------')
    try:
        properties.find_correct_exposure(90,95,1000)
        properties.find_best_focus()
        
        camera = properties.init_camera()
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        ret,frame = camera.capture()
        props_log = camera.get_properties()
        cv2.imwrite(f'../images/capture_{timestamp}.png',frame)
        camera.close()
        logging.info(f'capture_{timestamp}.png ')
        logging.info(f'exposure: {props_log["CV_CAP_PROP_EXPOSURE"]}, brightness: {calculate_brightness(frame):.2f}')
        logging.info(f'focus: {props_log["CV_CAP_PROP_FOCUS"]}, sharpness: {calculate_sharpness(frame):.2f}')
        logging.info(f'props: {props_log}\n\n')
        
    except Exception:
        logging.exception("Error while capturing images")
        if not notification_sent:
            notify.send('Timelapse has run into an error')
            notification_sent=True
        try:
            cap.release()
            cv2.destroyAllWindows()
        except:
            pass

        
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))