from PIL import Image, ImageStat
import math
import cv2
import logging
import numpy as np
from timelapse.utils import calculate_brightness, calculate_sharpness

class CameraProperties:

    def __init__(self,width=1280, height=720, autofocus=0, exposure=None, focus=None):      
        self.width = width
        self.height = height
        self.autofocus = autofocus
        self.exposure = exposure
        self.focus = focus
        self.cap = None
        self.MAX_EXPOSURE = 2047
        self.MIN_EXPOSURE = 3

    def init_camera(self):    
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.exposure is not None:
            cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        cap.set(cv2.CAP_PROP_AUTOFOCUS, self.autofocus)
        if self.focus is not None:
            cap.set(cv2.CAP_PROP_FOCUS, self.focus)
        return Camera(cap)

    def find_correct_exposure(self, min_brightness=100, max_brightness=125, max_iter=1000, factor = 1.05):
        exposure_fixed = False
        logging.info(f'Starting find_correct exposure, current exposure: {self.exposure}')
        n_iter=0
        prev_exposures = [self.exposure]
        while not exposure_fixed:
            camera = self.init_camera()
            ret,frame = camera.capture()
            brightness = calculate_brightness(frame)
            if brightness <= min_brightness:
                self.exposure = np.min([self.MAX_EXPOSURE, np.ceil([self.exposure*factor])])
                n_iter+=1
                logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Increased exposure to {self.exposure}')
            elif brightness >= max_brightness:
                self.exposure = np.max([self.MIN_EXPOSURE, np.floor([self.exposure/factor])])
                n_iter+=1
                logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Decreased exposure to {self.exposure}')
            elif n_iter>max_iter:
                logging.info(f'Iteration {n_iter} - Limit exceeded - Brightness: {brightness}. Exposure was {self.exposure}')
                exposure_fixed=True
            else:
                logging.info(f'Iteration {n_iter} - Acceptable exposure reached - Brightness: {brightness}. Exposure was {self.exposure}')
                exposure_fixed=True
            if self.exposure == self.MIN_EXPOSURE or self.exposure == self.MAX_EXPOSURE:
                exposure_fixed=True
                logging.info(f'Iteration {n_iter-1} - Exposure limit reached - Brightness: {brightness}. Exposure was {self.exposure}')

            # check if stuck in loop
            MAX = 5 # best to keep at odd number
            prev_exposures.append(self.exposure)
            if len(prev_exposures)>MAX:
                prev_exposures.pop()
            if len(np.unique(prev_exposures))<=2 and len(prev_exposures)>=MAX:
                logging.info(f'Iteration {n_iter-1} - Stuck in a loop, terminating. - Brightness: {brightness}. Exposure was {self.exposure}')
                exposure_fixed = True

            camera.close()


    def find_best_focus(self):
        """
        Try to find the best focus by doing a grid search, each time decreasing the step-size in the grid.
        """
        logging.info('Finding the optimal focus.')
        
        sharpness_dict = dict()
        for focus in range(0,230,25):
            self.focus = focus
            camera = self.init_camera()
            ret,frame = camera.capture()
            sharpness_dict[self.focus] = calculate_sharpness(frame)
            camera.close()
        best_focus_1 = max(sharpness_dict, key=sharpness_dict.get)
        logging.info('Iteration 1: Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))


        sharpness_dict = dict()
        for focus in range(np.max([0,best_focus_1-15]),np.min([250,best_focus_1+20]),5):
            self.focus = focus
            camera = self.init_camera()
            ret,frame = camera.capture()
            sharpness_dict[self.focus] = calculate_sharpness(frame)
            camera.close()
        best_focus_2 = max(sharpness_dict, key=sharpness_dict.get)
        logging.info('Iteration 2: Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))


        sharpness_dict = dict()
        for focus in range(np.max([0,best_focus_2-10]),np.min([250,best_focus_2+12]),2):
            self.focus = focus
            camera = self.init_camera()
            ret,frame = camera.capture()
            sharpness_dict[self.focus] = calculate_sharpness(frame)
            camera.close()
        best_focus_3 = max(sharpness_dict, key=sharpness_dict.get)
        logging.info('Iteration 3: Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))

        logging.info(f'Best focus at {best_focus_3}, {sharpness_dict[best_focus_3]}')
        self.focus = best_focus_3



class Camera:

    def __init__(self,cap):
        self.cap = cap

    def get_properties(self):
        properties = {
            3: 'CAP_PROP_FRAME_WIDTH',
            4: 'CAP_PROP_FRAME_HEIGHT',
            15:'CV_CAP_PROP_EXPOSURE',
            28:'CV_CAP_PROP_FOCUS',
            39: 'CV_CAP_PROP_AUTOFOCUS'
        }
        return {value : self.cap.get(key) for key,value in properties.items()}

    def capture(self):
        return self.cap.read()

    def close(self):
        self.cap.release()
        self.cap=None
        cv2.destroyAllWindows()    