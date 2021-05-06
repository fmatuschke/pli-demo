import argparse
import sys

import pretty_errors  # type: ignore # noqa: F401
from PyQt5.QtWidgets import QApplication

import widgets.application


def process_cl_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=str)
    parser.add_argument('--port', type=int)
    parser.add_argument('--resolution', type=str)
    parser.add_argument('--fps', type=int)
    parser.add_argument('--first-n', action='store_true')
    parser.add_argument('--insert-threshold', type=float, default=2.5)

    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args


def main():
    parsed_args, unparsed_args = process_cl_args()
    qt_args = sys.argv[:1] + unparsed_args

    app = QApplication(qt_args)
    window = widgets.application.Application(parsed_args)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
