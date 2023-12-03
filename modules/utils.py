import os
import logging
import subprocess
from pathlib import Path

import cv2
import pyexiv2

def save_custom_event_video(frames: list, framerate: int, event_name: str) -> str:
    dir_name = f'{os.getcwd()}/videos/{event_name}'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    else:
        i = 1
        while os.path.exists(dir_name + f'({i})'):
            i += 1
        dir_name = dir_name + f'({i})'
        os.makedirs(dir_name)

    height, width, layers = frames[0].shape
    size = (width,height)
    write_video_to_disk(frames, dir_name, framerate, size, event_name)
    return dir_name

def save_video_with_motion_detection(prerecord_frames: list, record_frames: list,
                                     postrecord_frames: list, framerate: int,
                                     dir_name: str):
    os.makedirs(dir_name)

    full_video_frames = []
    for frame in prerecord_frames:
        full_video_frames.append(frame)
    for frame in record_frames:
        full_video_frames.append(frame)
    for frame in postrecord_frames:
        full_video_frames.append(frame)

    height, width, layers = full_video_frames[0].shape
    size = (width,height)
    write_video_to_disk(full_video_frames, dir_name, framerate, size)

def add_metadata(dir_name: str, camera_type: str, trigger: str, video_title = '-'):
    comment = f'Camera type: {camera_type}\nTrigger: {trigger}'
    for root, dirs, files in os.walk(dir_name, topdown=False):
        for file in files:
            filename = os.path.join(root, file)
            if file.endswith('jpg'):
                image = pyexiv2.Image(filename)

                image.modify_exif({
                    'Exif.Image.ImageDescription': comment
                })
                image.close()
            elif file.endswith('mp4'):
                old_video_name = Path(file).stem
                new_video_name = os.path.join(root, f'{old_video_name}_with_metadata.mp4')
                subprocess.call(['ffmpeg', '-i', filename, '-c', 'copy', '-movflags',
                                 'use_metadata_tags', '-map_metadata', '0', '-metadata',
                                 f'title={video_title}\n{comment}', '-metadata', f'comment={comment}',
                                 new_video_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.remove(filename)
            else:
                logging.error(f'Unknown file type: {filename}')
                return

        logging.info(f'Metadata for folder {dir_name} has been written')

def write_video_to_disk(frames: list, dir_name: str, framerate: int, size: tuple, video_name = 'video'):
    video_name = f'{dir_name}/{video_name}.mp4'
    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), framerate, size)

    for frame in frames:
        out.write(frame)
    out.release()

    i = 0
    for frame in frames:
        cv2.imwrite('{}_{}.{}'.format(f'{dir_name}/frame', str(i), 'jpg'), frame)
        i += 1
    logging.info(f'{video_name} saved to disk')


