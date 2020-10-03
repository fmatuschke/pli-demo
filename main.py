import sys
from PyQt5.QtWidgets import QApplication
from gui.mainwindow import MainWindow

app = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.showMaximized()
app.exec_()
