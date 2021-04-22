from PIL import Image, ImageStat
import math
import cv2
import logging
import numpy as np

def find_correct_exposure(properties,min_brightness=100,max_brightness=125, max_iter=1000, factor = 1.05):
    exposure_fixed = False
    exposure = properties['CV_CAP_PROP_EXPOSURE']
    MAX_EXPOSURE = 2047
    MIN_EXPOSURE = 3

    logging.info(f'Starting find_correct exposure, current exposure: {exposure}')
    n_iter=0
    prev_exposure = 9999
    while not exposure_fixed:
        cap = init_cap_dict(properties)
        ret,frame = cap.read()
        brightness = calculate_brightness(frame)
        if brightness <= min_brightness:
            exposure = np.min([MAX_EXPOSURE, np.ceil([exposure*factor])])
            properties['CV_CAP_PROP_EXPOSURE'] = exposure
            n_iter+=1
            logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Increased exposure to {exposure}')
        elif brightness >= max_brightness:
            exposure = np.max([MIN_EXPOSURE, np.floor([exposure/factor])])
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
        if exposure == prev_exposure:
            exposure_fixed=True
            logging.info(f'Iteration {n_iter-1} - Exposure same as previous exposure, terminating. - Brightness: {brightness}. Exposure was {exposure}')
        else:
            prev_exposure = exposure

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
    """
    Try to find the best focus by doing a grid search, each time decreasing the step-size in the grid.
    """
    logging.info('Finding the optimal focus.')
    
    sharpness_dict = dict()
    for focus in range(0,230,25):
        properties['CV_CAP_PROP_FOCUS'] = focus
        cap = init_cap_dict(properties)
        ret,frame = cap.read()
        sharpness_dict[focus] = calculate_sharpness(frame)
        end_cap(cap)
    best_1 = max(sharpness_dict, key=sharpness_dict.get)
    logging.info('Iteration 1: Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))


    sharpness_dict = dict()
    for focus in range(np.max([0,best_1-15]),np.min([250,best_1+20]),5):
        properties['CV_CAP_PROP_FOCUS'] = focus
        cap = init_cap_dict(properties)
        ret,frame = cap.read()
        sharpness_dict[focus] = calculate_sharpness(frame)
        end_cap(cap)
    best_2 = max(sharpness_dict, key=sharpness_dict.get)
    logging.info('Iteration 2: Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))


    sharpness_dict = dict()
    for focus in range(np.max([0,best_2-10]),np.min([250,best_2+12]),2):
        properties['CV_CAP_PROP_FOCUS'] = focus
        cap = init_cap_dict(properties)
        ret,frame = cap.read()
        sharpness_dict[focus] = calculate_sharpness(frame)
        end_cap(cap)
    best_3 = max(sharpness_dict, key=sharpness_dict.get)
    logging.info('Iteration 3: Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))

    logging.info(f'Best focus at {best_3}, {sharpness_dict[best_3]}')
    properties['CV_CAP_PROP_FOCUS'] = best_3
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
        width = properties['CV_CAP_PROP_FRAME_WIDTH'],
        height = properties['CV_CAP_PROP_FRAME_HEIGHT'],
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