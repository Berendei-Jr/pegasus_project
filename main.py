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
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QFileDialog)
from . resources_rc import *
'''

import sys
import os
import logging

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

    def open_camera_dashboard(self):
        widgets.pushButtonDashboard.click()

    def update_frame(self):
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

    # BUTTONS CLICK
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pushButtonHome":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "pushButtonSettings":
            widgets.stackedWidget.setCurrentWidget(widgets.settings)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "pushButtonDashboard":
            widgets.stackedWidget.setCurrentWidget(widgets.video_page) # SET PAGE
            self.frame_update_timer.start(40)
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "pushButtonTheme":
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            newTheme = 'themes/py_dracula_light.qss' if self.darkTheme else 'themes/py_dracula_dark.qss'
            self.darkTheme = not self.darkTheme
            UIFunctions.theme(self, newTheme, True)
            AppFunctions.setThemeHack(self)

        if btnName == "pushButtonApply":
            self.cameraHandler.set_options(motion_detection=widgets.buttonMotionDetection.isChecked(),
                                          face_id=widgets.buttonFaceID.isChecked(),
                                          metadata=widgets.buttonMetadata.isChecked(),
                                          subtitles=widgets.buttonTitles.isChecked())

        if btnName == "pushButtonOpenCFG":
            resp = QFileDialog.getOpenFileName(self, caption='Select config file')
            print(str(resp[0]))

        if btnName == "pushButtonExit":
            sys.exit(0)

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
