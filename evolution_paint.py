#!/usr/bin/python3
"""
VIN project
Uses genetic programming to evolve image into passes in image,
generating similar images

@author: Marek Sedlacek (xsedla1b)
@date: September 2021
"""

import PyQt5
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QAction,
                             QPushButton,
                             QFileDialog)


class MainWindow(QMainWindow):
    """
    Main program windows
    """

    def __init__(self, width, height):
        super(MainWindow, self).__init__()
        self.resize(width, height)
        # Center the screen
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center = QApplication.desktop().screenGeometry(screen).center()
        self.move(center.x() - self.width() / 2, center.y() - self.height() / 2)
        self.initUI()
    
    def initUI(self):
        """
        Initialize UI
        """
        self.setWindowTitle("Evolution paint")
        
        # Adding a menu bar
        self.menuBar().clear()
        self.menu_bar = self.menuBar()
        self.mb_file = self.menu_bar.addMenu("File")

        # Setting up File menu bar
        # Upload image
        self.mb_upload_image = QAction("Upload image")
        self.mb_file.addAction(self.mb_upload_image)
        self.mb_upload_image.triggered.connect(self.upload_image)

        #Quit
        self.mb_quit = QAction("Quit")
        self.mb_file.addAction(self.mb_quit)
        self.mb_quit.triggered.connect(lambda: app.exit())

        # Upload image button in the middle of the windows when nothing is open
        self.button_upload_image = QPushButton("Upload image", self)
        self.button_upload_image.resize(200, 50)
        self.button_upload_image.move(self.width() / 2 - self.button_upload_image.width() / 2,
                                      self.height() / 2 - self.button_upload_image.height() / 2)
        self.button_upload_image.pressed.connect(self.upload_image)

        # Show the window
        self.show()

    def upload_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select file to evolve into", "","Images (*.png);;All Files (*)", options=options)
        if fileName:
            print(fileName)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    win = MainWindow(1024, 600)

    sys.exit(app.exec_())