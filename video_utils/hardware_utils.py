import os
import logging
from datetime import datetime

import cv2

def write_frames_to_disk(prerecord_frames: list, record_frames: list,
                         postrecord_frames: list, framerate = int):
    dir_name = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    os.mkdir(dir_name)

    full_video_frames = []
    for frame in prerecord_frames:
        full_video_frames.append(frame)
    for frame in record_frames:
        full_video_frames.append(frame)
    for frame in postrecord_frames:
        full_video_frames.append(frame)

    height, width, layers = full_video_frames[0].shape
    size = (width,height)
    video_name = f'{dir_name}/video.avi'
    out = cv2.VideoWriter(video_name,cv2.VideoWriter_fourcc(*'DIVX'), framerate, size)

    for frame in full_video_frames:
        out.write(frame)
    out.release()

    i = 0
    for frame in full_video_frames:
        cv2.imwrite('{}_{}.{}'.format(f'{dir_name}/frame', str(i), 'jpg'), frame)
        i += 1
    logging.info(f'{video_name} saved to disk')
