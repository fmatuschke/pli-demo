import sys

import pretty_errors  # type: ignore
from PyQt5.QtWidgets import QApplication, QWidget

import widgets.application

#TODO: arguments like camera_port or video_file


def main():
    app = QApplication(sys.argv)
    window = widgets.application.Application()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
