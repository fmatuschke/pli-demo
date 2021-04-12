import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow, Controller

app = QApplication(sys.argv)
controller = Controller()
#mainwindow = MainWindow()
# mainwindow.resize(1600, 1600 // 1.618)
# mainwindow.show()
#mainwindow.showMaximized()
#app.exec_()

controller.show_offset()
sys.exit(app.exec_())

