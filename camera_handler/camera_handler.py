import cv2

class CameraHandler:
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture("/home/hellcat/workspace/pegasus_project/images/IMG_2026.MP4")
        #self.cap = cv2.VideoCapture(0); # видео поток с веб камеры
        self.load_config()
        self.enable_motion_detection = False
        self.enable_face_id = False
        ret, self.old_frame = self.cap.read()
        if not ret:
            raise BufferError('Unable to read frame')

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def load_config(self):
        pass

    def set_options(self, motion_detection = False, face_id = False) -> bool:
        self.enable_motion_detection = motion_detection
        self.enable_face_id = face_id

    def get_frame(self):
        if not self.cap.isOpened():
            raise BufferError('Unable to read frame')

        ret, new_frame = self.cap.read()
        if not ret:
            raise BufferError('Unable to read frame')
        if self.enable_motion_detection:
            new_frame = self.__motion_detection(new_frame)
        new_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2RGB)
        return new_frame

    def __motion_detection(self, new_frame):
        frame_for_show = self.old_frame.copy()
        diff = cv2.absdiff(self.old_frame, new_frame) # нахождение разницы двух кадров, которая проявляется лишь при изменении одного из них, т.е. с этого момента наша программа реагирует на любое движение.
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # перевод кадров в черно-белую градацию
        blur = cv2.GaussianBlur(gray, (5, 5), 0) # фильтрация лишних контуров
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY) # метод для выделения кромки объекта белым цветом
        dilated = cv2.dilate(thresh, None, iterations = 3) # данный метод противоположен методу erosion(), т.е. эрозии объекта, и расширяет выделенную на предыдущем этапе область
        
        сontours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # нахождение массива контурных точек

        for contour in сontours:
            (x, y, w, h) = cv2.boundingRect(contour) # преобразование массива из предыдущего этапа в кортеж из четырех координат
        
            # метод contourArea() по заданным contour точкам, здесь кортежу, вычисляет площадь зафиксированного объекта в каждый момент времени, это можно проверить
            print(cv2.contourArea(contour))
        
            if cv2.contourArea(contour) < 700: # условие при котором площадь выделенного объекта меньше 700 px
                continue
            cv2.rectangle(frame_for_show, (x, y), (x+w, y+h), (0, 255, 0), 2) # получение прямоугольника из точек кортежа
            cv2.putText(frame_for_show, "Status: {}".format("Dvigenie"), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA) # вставляем текст
        
        #cv2.drawContours(frame1, сontours, -1, (0, 255, 0), 2) также можно было просто нарисовать контур объекта
    
        self.old_frame = new_frame
        return frame_for_show
