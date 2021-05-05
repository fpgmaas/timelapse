import cv2
import numpy as np
import glob

img_array = []
for filename in sorted(glob.glob(f'../images/*.png')):
    img = cv2.imread(filename)
    if not img is None:
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)


out = cv2.VideoWriter(f'../videos/project_15fps.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 15, size)
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()

out = cv2.VideoWriter(f'../videos/project_30fps.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 30, size)
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()