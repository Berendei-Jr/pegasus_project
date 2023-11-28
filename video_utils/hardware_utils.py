import os
import logging
import subprocess

import cv2
import pyexiv2

def write_frames_to_disk(prerecord_frames: list, record_frames: list,
                         postrecord_frames: list, framerate: int,
                         dir_name: str):
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
    video_name = f'{dir_name}/tmp.mp4'
    out = cv2.VideoWriter(video_name,cv2.VideoWriter_fourcc(*'mp4v'), framerate, size)

    for frame in full_video_frames:
        out.write(frame)
    out.release()

    i = 0
    for frame in full_video_frames:
        cv2.imwrite('{}_{}.{}'.format(f'{dir_name}/frame', str(i), 'jpg'), frame)
        i += 1
    logging.info(f'{video_name} saved to disk')

def add_metadata(dir_name: str, camera_type: str, trigger: str, video_title = '-'):
    comment = f'Camera type: {camera_type}\nTrigger: {trigger}'
    for root, dirs, files in os.walk(dir_name, topdown=False):
        for file in files:
            filename = os.path.join(root, file)
            video_name = os.path.join(root, 'video.mp4')
            if file.endswith('jpg'):
                image = pyexiv2.Image(filename)

                image.modify_exif({
                    'Exif.Image.ImageDescription': comment
                })
                image.close()
            elif file.endswith('mp4'):
                subprocess.call(['ffmpeg', '-i', filename, '-c', 'copy', '-movflags',
                                 'use_metadata_tags', '-map_metadata', '0', '-metadata',
                                 f'title={video_title}\n{comment}', '-metadata', f'comment={comment}',
                                 video_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                logging.error(f'Unknown file type: {filename}')
                return
        logging.info(f'Metadata for folder {dir_name} has been written')
