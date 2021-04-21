from PIL import Image, ImageStat
import math
import cv2
import logging

def find_correct_exposure(cap,min_brightness=100,max_brightness=125, max_iter=1000, verbose = False):
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
            exposure+=1
            cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            n_iter+=1
            if verbose: 
                logging.info(f'Iteration {n_iter-1} - Brightness: {brightness}. Increased exposure to {exposure}')
        elif brightness >= max_brightness:
            exposure-=1
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