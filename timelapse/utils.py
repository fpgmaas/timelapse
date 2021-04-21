from PIL import Image, ImageStat
import math
import cv2
import logging
import numpy as np

def find_correct_exposure(cap,min_brightness=100,max_brightness=125, max_iter=1000, step = 5, verbose = False):
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    exposure_fixed = False
    exposure = cap.get(15)
    if verbose: 
        logging.info(f'Starting find_correct exposure, current exposure: {exposure}')
    n_iter=0
    while not exposure_fixed:
        ret,frame = cap.read()
        brightness = calculate_brightness(frame)
        if brightness <= min_brightness:
            exposure = np.min([2047, exposure+step])
            cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            n_iter+=1
            if verbose: 
                logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Increased exposure to {exposure}')
        elif brightness >= max_brightness:
            exposure = np.max([0, exposure-step])
            cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            n_iter+=1
            if verbose: 
                logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Decreased exposure to {exposure}')
        elif n_iter>max_iter:
            logging.info(f'Iteration {n_iter-1} - Limit exceeded - Brightness: {brightness}. Exposure was {exposure}')
            exposure_fixed=True
        else:
            logging.info(f'Iteration {n_iter-1} - Acceptable exposure reached - Brightness: {brightness}. Exposure was {exposure}')
            exposure_fixed=True
        if exposure == 0 or exposure == 2047:
            exposure_fixed=True
            logging.info(f'Iteration {n_iter-1} - Exposure limit reached - Brightness: {brightness}. Exposure was {exposure}')

    return cap, exposure, n_iter

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

def find_best_focus(cap):
    logging.info('Finding the optimal focus.')
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    sharpness_dict = dict()
    for focus in range(0,255,5):
        cap.set(cv2.CAP_PROP_FOCUS ,focus)
        ret,frame = cap.read()
        sharpness_dict[focus] = calculate_sharpness(frame)
    
    logging.info('Sharpness per focus value: ' + ', '.join([f'{k}:{round(v,1)}' for k, v in sharpness_dict.items()]))
    best_focus = max(sharpness_dict, key=sharpness_dict.get)
    logging.info(f'Best focus at {best_focus}, {sharpness_dict[best_focus]}')
    cap.set(cv2.CAP_PROP_FOCUS ,best_focus)
    return cap, best_focus

def get_properties(cap):
    properties = {
        10:'CV_CAP_PROP_BRIGHTNESS',
        11:'CV_CAP_PROP_CONTRAST',
        12:'CV_CAP_PROP_SATURATION',
        13:'CV_CAP_PROP_HUE',
        14:'CV_CAP_PROP_GAIN',
        15:'CV_CAP_PROP_EXPOSURE'
    }
    return {value : cap.get(key) for key,value in properties.items()}