# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'process.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING! All changes made in this file will be lost!


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QImage
import sys
import cv2
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np

from PIL import Image, ImageChops
from PIL.ImageQt import ImageQt
import time
from scipy.interpolate import splrep, sproot
import pylinac
from pylinac import Starshot

# Uncomment when creating an executable file (exe)
from skimage.filters import thresholding


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    error_signal = pyqtSignal(str)  # Add an error signal

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        self.cameraIsOn = True 
        self.calThreadIsOn = False

        # Capture from raspberry pi camera
        cap = cv2.VideoCapture('http://169.254.119.136:8000/stream.mjpg')
        
        if not cap.isOpened():
            self.error_signal.emit("Failed to connect to the Raspberry Pi camera.")
            return

        self.current_sum = 0
        self.max_sum = 0
        self.frame_with_max_sum = None

        while self._run_flag:
            # Set the position of the next frame to be read
            ret, self.cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(self.cv_img)
                if self.cameraIsOn == False :
                    print("Waiting for the streaming data")

                else:
                    if self.calThreadIsOn == True:
                        
                        # Calculate the maximum pixel value of the frame
                        self.current_sum = np.sum(self.cv_img)

                        # Update max sum and corresponding frame if current sum is greater
                        if self.current_sum > self.max_sum:
                            self.max_sum = self.current_sum
                            self.frame_with_max_sum = self.cv_img                             
        # Shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class Ui_MainWindow(QWidget):        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Qt live streaming data")
        MainWindow.resize(860, 867)
        super().__init__()
        self.disply_width = 256
        self.display_height = 240         
        # Create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.LBL_TITLE = QtWidgets.QLabel(self.centralwidget)
        self.LBL_TITLE.setGeometry(QtCore.QRect(90, 30, 681, 51))
        self.LBL_TITLE.setObjectName("LBL_TITLE")
        self.CMB_GantryAngle = QtWidgets.QComboBox(self.centralwidget)
        self.CMB_GantryAngle.setGeometry(QtCore.QRect(148, 165, 67, 22))
        self.CMB_GantryAngle.setObjectName("CMB_GantryAngle")
        self.CMB_GantryAngle.addItem("")
        self.CMB_GantryAngle.addItem("")
        self.CMB_GantryAngle.addItem("")
        self.CMB_GantryAngle.addItem("")
        self.CMB_GantryAngle.addItem("")
        self.CMB_GantryAngle.addItem("")
        self.BTN_Connect = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Connect.setGeometry(QtCore.QRect(50, 130, 75, 31))
        self.BTN_Connect.setObjectName("BTN_Get_Line")
        self.BTN_Get_DR = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Get_DR.setGeometry(QtCore.QRect(223, 170, 75, 23)) 
        self.BTN_Get_DR.setObjectName("BTN_Get_DR")
        self.BTN_Get_Star = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Get_Star.setGeometry(QtCore.QRect(140, 140, 75, 23))
        self.BTN_Get_Star.setObjectName("BTN_Get_Star")
        self.BTN_Get_Laser = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Get_Laser.setGeometry(QtCore.QRect(223, 140, 75, 23))
        self.BTN_Get_Laser.setObjectName("BTN_Get_Laser")
        self.LBL_IMGAQ = QtWidgets.QLabel(self.centralwidget)
        self.LBL_IMGAQ.setGeometry(QtCore.QRect(140, 110, 161, 21))
        self.LBL_IMGAQ.setObjectName("LBL_IMGAQ")
        self.BTN_Apply_Laser = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Apply_Laser.setGeometry(QtCore.QRect(330, 140, 75, 23))
        self.BTN_Apply_Laser.setObjectName("BTN_Apply_Laser")
        self.BTN_Apply_DR = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Apply_DR.setGeometry(QtCore.QRect(330, 170, 75, 23))
        self.BTN_Apply_DR.setObjectName("BTN_Apply_DR")
        self.LBL_APISO = QtWidgets.QLabel(self.centralwidget)
        self.LBL_APISO.setGeometry(QtCore.QRect(310, 110, 111, 21))
        self.LBL_APISO.setObjectName("LBL_APISO")
        self.BTN_Analyzer = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Analyzer.setGeometry(QtCore.QRect(430, 160, 75, 31))
        self.BTN_Analyzer.setObjectName("BTN_Analyzer")
        self.GRP_Stream = QtWidgets.QGraphicsView(self.centralwidget)
        self.GRP_Stream.setGeometry(QtCore.QRect(520, 110, 266, 250))
        self.GRP_Stream.setObjectName("GRP_Stream")
        self.GRP_Starshot = QtWidgets.QGraphicsView(self.centralwidget)
        self.GRP_Starshot.setGeometry(QtCore.QRect(90, 400, 280, 280))
        self.GRP_Starshot.setObjectName("GRP_Star-shot")
        self.GRP_Analyzed = QtWidgets.QGraphicsView(self.centralwidget)
        self.GRP_Analyzed.setGeometry(QtCore.QRect(470, 400, 280, 280)) 
        self.GRP_Analyzed.setObjectName("GRP_Analyzed")
        self.LBL_Graph_stream = QtWidgets.QLabel(self.centralwidget)
        self.LBL_Graph_stream.setGeometry(QtCore.QRect(527, 90, 241, 21))
        self.LBL_Graph_stream.setObjectName("LBL_Graph_stream")
        self.LBL_Graph_starshot = QtWidgets.QLabel(self.centralwidget)
        self.LBL_Graph_starshot.setGeometry(QtCore.QRect(80, 380, 301, 21))
        self.LBL_Graph_starshot.setObjectName("LBL_Graph_starshot")
        self.LBL_Graph_analyzed = QtWidgets.QLabel(self.centralwidget)
        self.LBL_Graph_analyzed.setGeometry(QtCore.QRect(460, 380, 301, 21))
        self.LBL_Graph_analyzed.setObjectName("LBL_Graph_analyzed")
        self.TXT_Log = QtWidgets.QTextBrowser(self.centralwidget)
        self.TXT_Log.setGeometry(QtCore.QRect(87, 232, 381, 131))
        self.TXT_Log.setObjectName("TXT_Log")
        self.LBL_Log = QtWidgets.QLabel(self.centralwidget)
        self.LBL_Log.setGeometry(QtCore.QRect(90, 210, 51, 21))
        self.LBL_Log.setObjectName("LBL_Log")
        
        self.TBL_result = QtWidgets.QTableWidget(self.centralwidget)
        self.TBL_result.setGeometry(QtCore.QRect(270, 740, 501, 51))
        self.TBL_result.setRowCount(1)
        self.TBL_result.setColumnCount(3)
        self.TBL_result.setObjectName("TBL_result")
        item = QtWidgets.QTableWidgetItem()
        self.TBL_result.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TBL_result.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TBL_result.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.TBL_result.setHorizontalHeaderItem(2, item)
        self.TBL_result.horizontalHeader().setDefaultSectionSize(150)
        self.TBL_result.horizontalHeader().setMinimumSectionSize(20)
        self.TBL_result.verticalHeader().setDefaultSectionSize(20)
        self.TBL_result.verticalHeader().setMinimumSectionSize(20)
        
        self.Line_h1 = QtWidgets.QFrame(self.centralwidget)
        self.Line_h1.setGeometry(QtCore.QRect(47, 192, 461, 21))
        self.Line_h1.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.Line_h1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_h1.setObjectName("Line_h1")
        self.Line_h2 = QtWidgets.QFrame(self.centralwidget)
        self.Line_h2.setGeometry(QtCore.QRect(50, 360, 761, 21))
        self.Line_h2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.Line_h2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_h2.setObjectName("Line_h2")
        self.Line_v1 = QtWidgets.QFrame(self.centralwidget)
        self.Line_v1.setGeometry(QtCore.QRect(300, 110, 20, 91))
        self.Line_v1.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.Line_v1.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_v1.setObjectName("Line_v1")
        self.Line_v2 = QtWidgets.QFrame(self.centralwidget)
        self.Line_v2.setGeometry(QtCore.QRect(410, 110, 20, 91))
        self.Line_v2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.Line_v2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_v2.setObjectName("Line_v2")
        self.LBL_Result = QtWidgets.QLabel(self.centralwidget)
        self.LBL_Result.setGeometry(QtCore.QRect(230, 750, 51, 21))
        self.LBL_Result.setObjectName("LBL_Result")
        
        self.Line_h1_2 = QtWidgets.QFrame(self.centralwidget)
        self.Line_h1_2.setGeometry(QtCore.QRect(420, 140, 91, 21))
        self.Line_h1_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.Line_h1_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_h1_2.setObjectName("Line_h1_2")
        self.BTN_Merge = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Merge.setGeometry(QtCore.QRect(430, 110, 75, 31))
        self.BTN_Merge.setObjectName("BTN_Merge")
        self.Line_v2_2 = QtWidgets.QFrame(self.centralwidget)
        self.Line_v2_2.setGeometry(QtCore.QRect(500, 100, 20, 271))
        self.Line_v2_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.Line_v2_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_v2_2.setObjectName("Line_v2_2")
        self.Line_v1_2 = QtWidgets.QFrame(self.centralwidget)
        self.Line_v1_2.setGeometry(QtCore.QRect(120, 110, 20, 91))
        self.Line_v1_2.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.Line_v1_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.Line_v1_2.setObjectName("Line_v1_2")        
        self.BTN_Close = QtWidgets.QPushButton(self.centralwidget)
        self.BTN_Close.setGeometry(QtCore.QRect(50, 160, 75, 31))
        self.BTN_Close.setObjectName("BTN_Close")
        self.TXT_Result = QtWidgets.QTextBrowser(self.centralwidget)
        self.TXT_Result.setGeometry(QtCore.QRect(270, 700, 501, 141))
        self.TXT_Result.setObjectName("TXT_Result")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 860, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.laser_x = 0.
        self.laser_y = 0.
        self.dr_x = 0.
        self.dr_y = 0.
        
        self.scene_streaming = QtWidgets.QGraphicsScene(self.centralwidget)
        self.scene_starshot = QtWidgets.QGraphicsScene(self.centralwidget) 
        self.scene_analyzed = QtWidgets.QGraphicsScene(self.centralwidget)
        self.img_merged = Image.fromarray(np.zeros(shape=(10,10), dtype = np.int8))
        self.merged_laser = Image.fromarray(np.zeros(shape=(10,10), dtype = np.int8))
        self.blend_image = Image.fromarray(np.zeros(shape=(10,10), dtype = np.int8))   
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)        

    def retranslateUi(self, MainWindow):        
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Qt live streaming data"))
        self.LBL_TITLE.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600;\">Star-shot analyzer v3.0</span></p></body></html>"))
        self.CMB_GantryAngle.setItemText(0, _translate("MainWindow", "G240"))
        self.CMB_GantryAngle.setItemText(1, _translate("MainWindow", "G300"))
        self.CMB_GantryAngle.setItemText(2, _translate("MainWindow", "G000"))
        self.CMB_GantryAngle.setItemText(3, _translate("MainWindow", "G030"))
        self.CMB_GantryAngle.setItemText(4, _translate("MainWindow", "G090"))
        self.CMB_GantryAngle.setItemText(5, _translate("MainWindow", "G150"))
        self.BTN_Get_DR.setText(_translate("MainWindow", "Get DR"))
        self.BTN_Get_Star.setText(_translate("MainWindow", "Get starline"))
        self.BTN_Get_Laser.setText(_translate("MainWindow", "Get laser"))
        self.LBL_IMGAQ.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">image acquisition</p></body></html>"))
        self.BTN_Apply_Laser.setText(_translate("MainWindow", "Laser"))
        self.BTN_Apply_DR.setText(_translate("MainWindow", "DR"))
        self.LBL_APISO.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Apply isocenter</p></body></html>"))
        self.BTN_Analyzer.setText(_translate("MainWindow", "Analyze"))
        self.LBL_Graph_stream.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Streaming</p></body></html>"))
        self.LBL_Graph_starshot.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Star-shot</p></body></html>"))
        self.LBL_Graph_analyzed.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\">Analyzed image</p></body></html>"))

        self.LBL_Log.setText(_translate("MainWindow", "Log"))
        self.LBL_Result.setText(_translate("MainWindow", "Result"))
        self.BTN_Merge.setText(_translate("MainWindow", "Merge"))
        self.BTN_Connect.setText(_translate("MainWindow", "Connect"))
        self.BTN_Close.setText(_translate("MainWindow", "Close"))
        
        item = self.TBL_result.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Value"))
        item = self.TBL_result.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Min. circle radius"))
        item = self.TBL_result.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Diff: vs Laser"))
        item = self.TBL_result.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Diff: vs DR"))
        
        # Click the button
        self.BTN_Get_Star.clicked.connect(self.F_Get_Star)
        self.BTN_Get_Laser.clicked.connect(self.F_Get_Laser)
        self.BTN_Get_DR.clicked.connect(self.F_Get_DR)  
        self.BTN_Merge.clicked.connect(self.F_Merge)
        self.BTN_Apply_Laser.clicked.connect(self.F_Apply_Laser)
        self.BTN_Apply_DR.clicked.connect(self.F_Apply_DR)  
        self.BTN_Analyzer.clicked.connect(self.F_Analysis) 
        self.BTN_Connect.clicked.connect(self.F_Connect) 
        self.BTN_Close.clicked.connect(self.F_Close)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()


# Reference for realtime streaming of python pyqt app.        
# https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1


    @pyqtSlot(np.ndarray)
    def update_image_stream(self, cv_img):        
        """Updates GRP_Stream with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.scene_streaming.addItem(qt_img)
        self.GRP_Stream.setScene(self.scene_streaming)

    @pyqtSlot(np.ndarray)        
    def update_image_starshot(self, cv_img):
        """Updates GRP_Srarshot with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.scene_starshot.addItem(qt_img)
        
    @pyqtSlot(np.ndarray)
    def update_image_analyzed(self, cv_img):
        """Updates GRP_Analyzed with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.scene_analyzed.addItem(qt_img)  
        
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.AspectRatioMode.KeepAspectRatio)
        pixmap = QPixmap.fromImage(p)
        return QGraphicsPixmapItem(pixmap)    
      
    def F_Connect(self):              
        # Create the video capture thread
        self.thread = VideoThread()
        # Connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image_stream)
        # Connect the error signal to the error handling slot
        self.thread.error_signal.connect(self.display_connection_error)
        # Start the thread
        self.thread.start()

        self.TXT_Log.append("Connected to the IP address 169.254.119.136!\n")

    def display_connection_error(self, error_message):
        """Displays an error message when the connection fails."""
        self.TXT_Log.append(f"Error: {error_message}")        
                
    def F_Get_Star(self):
        tsec = time.time()
        filename = self.CMB_GantryAngle.currentText() + time.strftime("-%Y%m%d-%H%M%S", time.localtime(tsec)) 
        
        if self.BTN_Get_Star.text() == 'Get starline':
            self.BTN_Get_Star.setText('Stop')
            self.TXT_Log.append("Started recording the real-time streaming data!\n")  

            self.thread.cameraIsOn = True
            self.thread.calThreadIsOn = True            
            
            self.thread.current_sum = 0
            self.thread.max_sum = 0
            self.thread.frame_with_max_sum = None
            
        else:            
            self.BTN_Get_Star.setText('Get starline')    
            self.thread.cameraIsOn = False
            self.thread.calThreadIsOn = False              
                    
            selectedImg = self.thread.frame_with_max_sum;                    
            img = Image.fromarray(selectedImg) 

            w, h = img.size
            left = w/6
            right = 5*w/6
            upper = h/8
            lower = 7*h/8
            crop_img = img.crop([ left, upper, right, lower])
               
            default_file_name = filename[0:13]+ ".jpg"
            file = QtWidgets.QFileDialog.getSaveFileName(None, "Save merged image as", default_file_name, "JPEG files (*.jpg)")
            if file is not None:
                crop_img.save(file[0])
        
            self.TXT_Log.append("Extracted a still-shot " + filename[0:13] + "\n") 
            
    def F_Merge(self): 
        tsec = time.time()
        tname = time.strftime("%Y%m%d", time.localtime(tsec))
        
        file_path1 = QtWidgets.QFileDialog.getOpenFileNames(None, "Select Files", "./*.jpg")
    
        images = []
        for file_path in file_path1[0]:
            image = Image.open(file_path)
            images.append(image)

        merged_starshot = images[0]
        for ind_image in images[1:]:
            merged_starshot = ImageChops.add(merged_starshot, ind_image)

        merge_filename = "star-shot-" + tname + ".jpg"
        file = QtWidgets.QFileDialog.getSaveFileName(None, "Save merged image as",merge_filename, "JPEG files (*.jpg)") 

        if file is not None:
            merged_starshot.save(file[0])
 
        self.img_merged = merged_starshot
        w, h = merged_starshot.size
        resized_image = merged_starshot.resize((int(w/6), int(h/6)))
        img_starshot = ImageQt(resized_image)
        
        # Create a QPixmap object with an image
        pixmap = QPixmap.fromImage(img_starshot)
        
        # Add the QPixmap to the scene
        self.scene_starshot.addPixmap(pixmap)
        
        # Create a QGraphicsView
        self.GRP_Starshot.setScene(self.scene_starshot)

        self.TXT_Log.append("Acquired a star-shot image!\n")                    
        
    def F_Get_Laser(self):
        tsec = time.time()
        tname = time.strftime("%Y%m%d-%H%M%S", time.localtime(tsec)) 
    
        fname = "laser-" + tname + ".jpg"
        cv2.imwrite(fname, self.thread.cv_img)   
        
        self.TXT_Log.append("Captured a laser image!\n") 
        
    def F_Get_DR(self):
        tsec = time.time()
        tname = time.strftime("%Y%m%d-%H%M%S", time.localtime(tsec))
    
        fname = "dr-" + tname + ".jpg"
        cv2.imwrite(fname, self.thread.cv_img)
        
        self.TXT_Log.append("Captured a DR image!\n") 
        
    def F_Apply_Laser(self):
        # Reference (set the ROI): https://bkshin.tistory.com/entry/OpenCV-6-dd
        file_path2 = QtWidgets.QFileDialog.getOpenFileName(None, "Select a laser isocenter image", "./*.jpg") 
    
        laser_img_rgb = Image.open(file_path2[0])
        laser_img = laser_img_rgb.convert("L")        
        
        w, h = laser_img.size
        left = w/6
        right = 5*w/6
        upper = h/8
        lower = 7*h/8

        crop_laser_rgb = laser_img_rgb.crop([ left, upper, right, lower])
        crop_laser = laser_img.crop([ left, upper, right, lower])
        crop_laser_gray = np.array(crop_laser)

        # Apply bilateral filter to reduce noise
        crop_laser_img = cv2.bilateralFilter(crop_laser_gray,9,75,75) 
    
        hh, ww = crop_laser_img.shape
        search_loc_init = 100
        
        # Assuming 'image' is a NumPy array representing the image
        max_value_x = np.amax(crop_laser_img[search_loc_init,:])
        max_value_y = np.amax(crop_laser_img[:,search_loc_init])
        max_loc_x = np.where(crop_laser_img[search_loc_init,:] == max_value_x)
        max_loc_y = np.where(crop_laser_img[:,search_loc_init] == max_value_y)
        # Max_location contains the x and y coordinates of the maximum value
        max_x_init = max_loc_x[0][0]
        max_y_init = max_loc_y[0][0]
       
        center_x = []
        for search_loc_ind in range(100, ww, 100):
            if abs(search_loc_ind - max_y_init) < 50:
                continue
    
            base_x = list(range(0,ww))
            line_y = crop_laser_img[search_loc_ind,:]
        
            half_max_x = max(line_y)/2.0
            s_x = splrep(base_x, line_y - half_max_x, k=3)
            roots_x = sproot(s_x)
            center_x.append( roots_x.sum()/roots_x.size )
            
        center_y = []
        for search_loc_ind in range(100, hh, 100):
            if abs(search_loc_ind - max_x_init) < 50:
                continue

            base_y = list(range(0,hh))
            line_x = crop_laser_img[:,search_loc_ind]
        
            half_max_y = max(line_x)/2.0
            s_y = splrep(base_y, line_x - half_max_y, k=3)
            roots_y = sproot(s_y)
            center_y.append( roots_y.sum()/roots_y.size )
        
        self.laser_x = max_x_init
        self.laser_y = max_y_init
        
        self.TXT_Log.append(f"Laser isocenter: ({max_x_init}, {max_y_init})") 

        self.merged_laser = ImageChops.add(self.img_merged, crop_laser_rgb)    
        w, h = self.merged_laser.size
        resized_laser = self.merged_laser.resize((int(w/6), int(h/6)))
        laser_starshot= ImageQt(resized_laser)
        
        # Create a QPixmap object with an image
        pixmap = QPixmap.fromImage(laser_starshot)
        
        # Add the QPixmap to the scene
        self.scene_starshot.addPixmap(pixmap)
        
        # Create a QGraphicsView
        self.GRP_Starshot.setScene(self.scene_starshot)

        self.TXT_Log.append("Applied a laser isocenter has been completed!\n") 
        
    def F_Apply_DR(self):
        file_path3 = QtWidgets.QFileDialog.getOpenFileName(None, "Select a DR center image", "./*.jpg")     
         
        dr_img_rgb = Image.open(file_path3[0])
        dr_img = dr_img_rgb.convert("L")

        w, h = dr_img.size
        left = w/6
        right = 5*w/6
        upper = h/8
        lower = 7*h/8

        crop_dr_rgb = dr_img_rgb.crop([ left, upper, right, lower])
        crop_dr = dr_img.crop([ left, upper, right, lower])
        
        crop_dr_img = np.array(crop_dr)
        crop_w, crop_h = crop_dr.size

        crop_roi = crop_dr_img[int(crop_w/2)-100:int(crop_w/2)+100, int(crop_h/2)-100:int(crop_h/2)+100]
        
        # Threshold the image to create a binary image
        ret, thresh = cv2.threshold(crop_roi, 127, 255, cv2.THRESH_BINARY)
    
        # Find the contours in the binary image
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
        # Loop over the contours
        for cnt in contours:
            # Find the minimum enclosing circle of the contour
            (xx, yy), radius = cv2.minEnclosingCircle(cnt)
            
            if radius > 5 and radius < 10:
                # Calculate the x,y coordinate of the centroid
                self.dr_x = xx + int(crop_h/2)-100 
                self.dr_y = yy + int(crop_w/2)-100

        self.TXT_Log.append(f"DR center: ({round(self.dr_x, 2)}, {round(self.dr_y, 2)})")  
         
        self.blend_image = Image.blend(self.merged_laser, crop_dr_rgb, 0.5)

        w, h = self.blend_image.size
        resized_dr= self.blend_image.resize((int(w/6), int(h/6)))
        dr_starshot= ImageQt(resized_dr)
        
        # Create a QPixmap object with an image
        pixmap = QPixmap.fromImage(dr_starshot)
        
        # Add the QPixmap to the scene
        self.scene_starshot.addPixmap(pixmap)
        
        # Create a QGraphicsView
        self.GRP_Starshot.setScene(self.scene_starshot)
        
        self.TXT_Log.append("Finished applying a DR center!\n")   
        
    def F_Analysis(self):
        star_path = QtWidgets.QFileDialog.getOpenFileName(None, "Select a star-shot image", "./*.jpg")
        mystar = Starshot(star_path[0], dpi=160, sid=1000)
        mystar.analyze()
        pylinac.settings.DICOM_COLORMAP = 'cool'
    
        result_data = mystar.results_data()
        passed = result_data.passed
        diameter = result_data.circle_diameter_mm
        star_x = result_data.circle_center_x_y[0]
        star_y = result_data.circle_center_x_y[1]
    
        result1 = (self.laser_x - star_x) * 30 / 233
        result2 = (self.laser_y - star_y) * 30 / 232
        result3 = (self.dr_x - star_x) * 30 / 233
        result4 = (self.dr_y - star_y) * 30 / 232
    
        self.TXT_Result.append(
            f"Laser isocenter: ({round(self.laser_x, 2)}, {round(self.laser_y, 2)}) \n"
            f"DR center: ({round(self.dr_x, 2)}, {round(self.dr_y, 2)}) \n"
            f"Radiation isocenter: ({round(star_x, 2)}, {round(star_y, 2)})")
    
        self.TXT_Result.append(
            f"Result passed: {passed}\n"
            f"Minimum circle radius: {round(diameter, 3)} mm.\n"
            "Position difference of radiation isocenter between\n"
            f"laser vs. radiation: ({round(result1, 2)}, {round(result2, 2)}) mm.\n"
            f"DR vs. radiation: ({round(result3, 2)}, {round(result4, 2)}) mm.")
    
        mystar.save_analyzed_subimage('Star-shot_analyzed', True)
        starshot_img = Image.open("Star-shot_analyzed.png")
        w, h = starshot_img.size
        left = 2 * w / 9
        right = 8 * w / 9
        upper = 1 * h / 9
        lower = 8 * h / 9
        
        crop_starshot_img = starshot_img.crop([left, upper, right, lower])    
        resized_img = crop_starshot_img.resize((int(w / 2.15), int(h / 1.85)))
    
        pylinac_starshot = ImageQt(resized_img)        
        q_img = QImage(pylinac_starshot)

        # Create a QPixmap object and set it to the QLabel object
        pixmap2 = QtGui.QPixmap.fromImage(q_img)
        
        # Create the label that holds the image
        image_label = QtWidgets.QLabel()
        image_label.setPixmap(pixmap2)
        
        # Create a vertical box layout and add the label
        vbox = QVBoxLayout()
        vbox.addWidget(image_label)

        # Disable updates in the QGraphicsView
        self.GRP_Starshot.setUpdatesEnabled(False)
        
        # Set the vbox layout as the widgets layout
        self.GRP_Analyzed.setLayout(vbox)
        
        self.TXT_Log.append("The analysis of star-shot has been completed!\n")
 
    def F_Close(self):
        QtWidgets.QApplication.quit()
        self.thread.cameraIsOn = False
        self.thread.stop()
        self.close()
            
if __name__=="__main__":
    app = QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
