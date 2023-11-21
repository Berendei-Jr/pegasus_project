'''
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QTimer)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QSlider)
from . resources_rc import *
'''

import sys
import os
import logging
import json

from modules import *
from widgets import *
from video_utils.camera_handler import CameraHandler

os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # SET AS GLOBAL WIDGETS
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        Settings.ENABLE_CUSTOM_TITLE_BAR = False

        # APP NAME
        title = "Pegasus"
        description = "Security cameras dashboard"
        logo = QPixmap('./images/images/image.png')
        self.logo = logo.scaled(58, 58, Qt.KeepAspectRatio)
        widgets.logoLabel.setPixmap(self.logo)

        self.darkTheme = True

        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        UIFunctions.uiDefinitions(self)

        # BUTTONS CLICK
        widgets.pushButtonOpenCamera.clicked.connect(self.open_camera_dashboard)

        widgets.pushButtonDashboard.clicked.connect(self.buttonClick)
        widgets.pushButtonHome.clicked.connect(self.buttonClick)
        widgets.pushButtonSettings.clicked.connect(self.buttonClick)
        widgets.pushButtonTheme.clicked.connect(self.buttonClick)
        widgets.pushButtonExit.clicked.connect(self.buttonClick)
        widgets.pushButtonLoadConfig.clicked.connect(self.buttonClick)
        widgets.pushButtonSaveConfig.clicked.connect(self.buttonClick)
        widgets.pushButtonApply.clicked.connect(self.buttonClick)
        widgets.pushButtonOpenCFG.clicked.connect(self.buttonClick)

        widgets.horizontalSliderFramerate.valueChanged.connect(self.sliderFramerateUpdate)
        widgets.horizontalSliderPrerecord.valueChanged.connect(self.sliderPrerecordUpdate)
        widgets.horizontalSliderPostrecord.valueChanged.connect(self.sliderPostrecordUpdate)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # SHOW APPdirectory=os.getcwd()
        self.show()

        # SET HOME PAGE AND SELECT MENU
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.pushButtonHome.setStyleSheet(UIFunctions.selectMenu(widgets.pushButtonHome.styleSheet()))

        self.frame_update_timer = QTimer()
        self.frame_update_timer.timeout.connect(self.update_frame)
        self.cameraHandler = CameraHandler()
        self.set_settings_window()

    def open_camera_dashboard(self) -> None:
        widgets.pushButtonDashboard.click()

    def update_frame(self) -> None:
        try:
            frame = self.cameraHandler.get_frame()
        except BufferError as error:
            logging.error(error)
            sys.exit(1)
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        pixmap = QPixmap.fromImage(QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888))
        pixmap = pixmap.scaled(widgets.videoLabel.width(), widgets.videoLabel.height(), Qt.KeepAspectRatio)
        widgets.videoLabel.setPixmap(pixmap)

    def set_settings_window(self) -> None:
        new_options = self.cameraHandler.get_options()
        widgets.buttonMotionDetection.setChecked(bool(new_options['motion_detection']))
        if new_options['face_id']:
            widgets.buttonFaceID.setChecked(True)
        if new_options['metadata']:
            widgets.buttonMetadata.setChecked(True)
        if new_options['subtitles']:
            widgets.buttonTitles.setChecked(True)

    # BUTTONS CLICK
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pushButtonHome":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "pushButtonSettings":
            widgets.stackedWidget.setCurrentWidget(widgets.settings)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "pushButtonDashboard":
            widgets.stackedWidget.setCurrentWidget(widgets.video_page) # SET PAGE
            self.frame_update_timer.start(40)
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        elif btnName == "pushButtonTheme":
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            newTheme = 'themes/py_dracula_light.qss' if self.darkTheme else 'themes/py_dracula_dark.qss'
            self.darkTheme = not self.darkTheme
            UIFunctions.theme(self, newTheme, True)
            #AppFunctions.setThemeHack(self)

        elif btnName == "pushButtonApply":
            self.cameraHandler.set_options({
                'motion_detection': widgets.buttonMotionDetection.isChecked(),
                'face_id': widgets.buttonFaceID.isChecked(),
                'metadata': widgets.buttonMetadata.isChecked(),
                'subtitles': widgets.buttonTitles.isChecked()
            }, update=True)

        elif btnName == "pushButtonOpenCFG":
            config_file = str(QFileDialog.getOpenFileName(self,
                                               caption='Select config file',
                                               dir = os.getcwd(),
                                               filter='*.json')[0])
            if not config_file:
                return

            widgets.lineEditCFG.setText(config_file)

        elif btnName == "pushButtonLoadConfig":
            config_path = widgets.lineEditCFG.text()
            if not self.cameraHandler.load_config(config_path):
                QMessageBox.warning(self, 'Note', 'Invalid config path')
                return
            self.set_settings_window()

        elif btnName == "pushButtonSaveConfig":
            widgets.pushButtonApply.click()
            options = self.cameraHandler.get_options()
            config_name = f'{os.getcwd()}/config.json'
            with open(config_name, 'w', encoding='utf-8') as f:
                json.dump(options, f, ensure_ascii=False, indent=4)

            logging.info(f'Saved config {config_name}')

        if btnName == "pushButtonExit":
            sys.exit(0)

    def sliderFramerateUpdate(self, value):
        widgets.labelFramerate.setText(f'Framerate: {value} fps')
    
    def sliderPrerecordUpdate(self, value):
        widgets.labelPrerecord.setText(f'Prerecord time: {value}s')

    def sliderPostrecordUpdate(self, value):
        widgets.labelPostrecord.setText(f'Postrecord time: {value}s')

    # RESIZE EVENTS
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    def mousePressEvent(self, event):
        pass
        # SET DRAG POS WINDOW
       # self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        #if event.buttons() == Qt.LeftButton:
        #    print('Mouse click: LEFT CLICK')
        #if event.buttons() == Qt.RightButton:
        #    print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(message)s')

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
