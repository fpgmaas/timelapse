from PIL import Image, ImageStat
import math
import cv2
import logging
import numpy as np

def find_correct_exposure(properties,min_brightness=100,max_brightness=125, max_iter=1000, step = 5):
    exposure_fixed = False
    exposure = properties['CV_CAP_PROP_EXPOSURE']
    MAX_EXPOSURE = 2047
    MIN_EXPOSURE = 3

    logging.info(f'Starting find_correct exposure, current exposure: {exposure}')
    n_iter=0
    while not exposure_fixed:
        cap = init_cap_dict(properties)
        ret,frame = cap.read()
        brightness = calculate_brightness(frame)
        if brightness <= min_brightness:
            exposure = np.min([MAX_EXPOSURE, exposure+step])
            properties['CV_CAP_PROP_EXPOSURE'] = exposure
            n_iter+=1
            logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Increased exposure to {exposure}')
        elif brightness >= max_brightness:
            exposure = np.max([MIN_EXPOSURE, exposure-step])
            properties['CV_CAP_PROP_EXPOSURE'] = exposure
            n_iter+=1
            logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Decreased exposure to {exposure}')
        elif n_iter>max_iter:
            logging.info(f'Iteration {n_iter-1} - Limit exceeded - Brightness: {brightness}. Exposure was {exposure}')
            exposure_fixed=True
        else:
            logging.info(f'Iteration {n_iter-1} - Acceptable exposure reached - Brightness: {brightness}. Exposure was {exposure}')
            exposure_fixed=True
        if exposure == MIN_EXPOSURE or exposure == MAX_EXPOSURE:
            exposure_fixed=True
            logging.info(f'Iteration {n_iter-1} - Exposure limit reached - Brightness: {brightness}. Exposure was {exposure}')
        end_cap(cap)

    return properties, n_iter

def calculate_brightness(image_array):
    """
    from https://stackoverflow.com/a/3498247/8037249
    """
    pil_image = Image.fromarray(image_array)
    stat = ImageStat.Stat(pil_image)
    r,g,b = stat.mean
    return math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))

def calculate_sharpness(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def find_best_focus(properties):
    logging.info('Finding the optimal focus.')
    sharpness_dict = dict()
    for focus in range(0,230,5):
        properties['CV_CAP_PROP_FOCUS'] = focus
        cap = init_cap_dict(properties)
        ret,frame = cap.read()
        sharpness_dict[focus] = calculate_sharpness(frame)
        end_cap(cap)
    
    logging.info('Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))
    best_focus = max(sharpness_dict, key=sharpness_dict.get)
    logging.info(f'Best focus at {best_focus}, {sharpness_dict[best_focus]}')
    properties['CV_CAP_PROP_FOCUS'] = best_focus
    return properties

def get_properties(cap):
    properties = {
        3: 'CAP_PROP_FRAME_WIDTH',
        4: 'CAP_PROP_FRAME_HEIGHT',
        15:'CV_CAP_PROP_EXPOSURE',
        28:'CV_CAP_PROP_FOCUS',
        39: 'CV_CAP_PROP_AUTOFOCUS'
    }
    return {value : cap.get(key) for key,value in properties.items()}

def init_cap_dict(properties):
    return init_cap(
        width = properties['CAP_PROP_FRAME_WIDTH'],
        height = properties['CAP_PROP_FRAME_HEIGHT'],
        exposure = properties['CV_CAP_PROP_EXPOSURE'],
        focus = properties['CV_CAP_PROP_FOCUS'],
        autofocus = properties['CV_CAP_PROP_AUTOFOCUS']
    )

def init_cap(width=1280, height=720, autofocus=0, exposure=None, focus=None):      
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if exposure is not None:
        cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, autofocus)
    if focus is not None:
        cap.set(cv2.CAP_PROP_FOCUS, focus)
    return cap

def end_cap(cap):
    cap.release()
    cv2.destroyAllWindows()