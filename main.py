import sys

from PyQt5.QtWidgets import QApplication, QWidget

import widgets.application


def main():
    app = QApplication(sys.argv)
    window = widgets.application.Application()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
