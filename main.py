import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

app = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.resize(1600, 1600 // 1.618)
mainwindow.show()
# mainwindow.showMaximized()
app.exec_()
