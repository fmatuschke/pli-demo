import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

app = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.showMaximized()
app.exec_()
