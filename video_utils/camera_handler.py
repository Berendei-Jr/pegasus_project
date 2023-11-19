import cv2
import time
from video_utils.hardware_utils import write_frames_to_disk

FRAMERATE = 10
PRERECORD_TIME = 3
POSTRECORD_TIME = 3

PRERECORD_STATE = -1
MOTION_STATE = 0
POSTRECORD_STATE = 1

class CameraHandler:
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture("/home/hellcat/Downloads/111.mp4")
        #self.cap = cv2.VideoCapture(0); # видео поток с веб камеры
        self.load_config()
        self.enable_motion_detection = True
        self.enable_face_id = False
        self.enable_metadata = False
        self.enable_subtitles = False
        self.last_frame_update_time = time.time()
        self.frame_time = 1/FRAMERATE
        self.prerecord_frames_number = PRERECORD_TIME//self.frame_time
        self.postrecord_frames_number = POSTRECORD_TIME//self.frame_time
        self.prerecord_frames = []
        self.motion_frames = []
        self.postrecord_frames = []
        self.motion_detected = False
        self.record_state = PRERECORD_STATE

        ret, self.current_frame = self.cap.read()
        if not ret:
            raise BufferError('Unable to read frame')

        self.current_show_frame = self.current_frame
        self.prerecord_frames.append(self.current_show_frame)

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def load_config(self):
        pass

    def set_options(self, motion_detection = False, face_id = False,
                    metadata = False, subtitles = False) -> bool:
        self.enable_motion_detection = motion_detection
        self.enable_face_id = face_id
        self.enable_metadata = metadata
        self.enable_subtitles = subtitles

    def get_frame(self):
        if not self.cap.isOpened():
            raise BufferError('Unable to read frame')

        cur_time = time.time()
        if cur_time - self.last_frame_update_time < self.frame_time:
            return self.current_show_frame

        self.last_frame_update_time = cur_time
        ret, new_frame = self.cap.read()
        if not ret:
            raise BufferError('Unable to read frame')

        if self.enable_motion_detection:
            frame_for_show, self.motion_detected,  = self.__motion_detection(new_frame)
        else:
            frame_for_show = new_frame
    
        if self.enable_motion_detection:
            print(f'PRE: {len(self.prerecord_frames)}\nMOT: {len(self.motion_frames)}\nPOST: {len(self.postrecord_frames)}\n')
            if self.motion_detected:
                if self.record_state == PRERECORD_STATE:
                    self.record_state = MOTION_STATE
                    self.motion_frames.append(frame_for_show)
                elif self.record_state == POSTRECORD_STATE:
                    self.record_state = MOTION_STATE
                    for frame in self.postrecord_frames:
                        self.motion_frames.append(frame)
                    self.postrecord_frames.clear()
                self.motion_frames.append(frame_for_show)
            else:
                if self.record_state == PRERECORD_STATE:
                    if len(self.prerecord_frames)  == self.prerecord_frames_number:
                        self.prerecord_frames.pop(0)
                    self.prerecord_frames.append(frame_for_show)
                elif self.record_state == MOTION_STATE:
                    self.record_state = POSTRECORD_STATE
                    self.postrecord_frames.append(frame_for_show)
                else:
                    self.postrecord_frames.append(frame_for_show)
                    if len(self.postrecord_frames) == self.postrecord_frames_number:
                        write_frames_to_disk(prerecord_frames = self.prerecord_frames,
                                             record_frames=  self.motion_frames,
                                             postrecord_frames = self.postrecord_frames,
                                             framerate = FRAMERATE)
                        self.prerecord_frames.clear()
                        self.motion_frames.clear()
                        self.postrecord_frames.clear()
                        self.record_state = PRERECORD_STATE

        frame_for_show = cv2.cvtColor(frame_for_show, cv2.COLOR_BGR2RGB)
        self.current_show_frame = frame_for_show
        self.current_frame = new_frame
        return frame_for_show

    def __motion_detection(self, new_frame):
        frame_for_show = self.current_frame.copy()
        diff = cv2.absdiff(self.current_frame, new_frame) # нахождение разницы двух кадров, которая проявляется лишь при изменении одного из них, т.е. с этого момента наша программа реагирует на любое движение.
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # перевод кадров в черно-белую градацию
        blur = cv2.GaussianBlur(gray, (5, 5), 0) # фильтрация лишних контуров
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY) # метод для выделения кромки объекта белым цветом
        dilated = cv2.dilate(thresh, None, iterations = 3) # данный метод противоположен методу erosion(), т.е. эрозии объекта, и расширяет выделенную на предыдущем этапе область

        сontours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # нахождение массива контурных точек

        motion_detected = False
        if len(сontours) < 8:
            for contour in сontours:
                (x, y, w, h) = cv2.boundingRect(contour) # преобразование массива из предыдущего этапа в кортеж из четырех координат

                # метод contourArea() по заданным contour точкам, здесь кортежу, вычисляет площадь зафиксированного объекта в каждый момент времени, это можно проверить
                #print(cv2.contourArea(contour))
            
                if cv2.contourArea(contour) < 700: # условие при котором площадь выделенного объекта меньше 700 px
                    continue

                motion_detected = True
                cv2.rectangle(frame_for_show, (x, y), (x+w, y+h), (0, 255, 0), 2) # получение прямоугольника из точек кортежа
                #cv2.putText(frame_for_show, "Status: {}".format("Dvigenie"), (10, 20),
                #            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA) # вставляем текст
        cv2.putText(frame_for_show, "Time: {}".format(str(time.time())), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA) # вставляем текст
            #cv2.drawContours(frame1, сontours, -1, (0, 255, 0), 2) также можно было просто нарисовать контур объекта
        return frame_for_show, motion_detected
