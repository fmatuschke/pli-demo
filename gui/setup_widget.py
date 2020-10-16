import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

from PyQt5 import QtOpenGL, QtWidgets, QtGui, QtCore


class SetupWidget(QtOpenGL.QGLWidget):
    '''
    Widget that renders a schematic PLI-Setup
    '''

    def __init__(self, parent=None, *args, **kwargs):
        super(SetupWidget, self).__init__(parent)
        self._tilt_angle = (0, 10)
        self._rotation = 0

        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        self.setAutoFillBackground(True)
        self.setPalette(p)

    def resizeEvent(self, event):
        super(SetupWidget, self).resizeEvent(event)
        w, h = max(1, self.size().width()), max(1, self.size().height())
        gluPerspective(45.0, w / h, 0.1, 1000.0)
        glViewport(0, 0, w, h)

    def initializeGL(self):
        glClearDepth(1.0)
        glClearColor(0.2, 0.2, 0.2, 0.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)

        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])

        glLoadIdentity()
        # gluPerspective(10, 4.2, 0.1, 1000.0)
        w, h = max(1, self.size().width()), max(1, self.size().height())
        gluPerspective(20.0, w / h, 0.1, 1000.0)
        glViewport(0, 0, w, h)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -50)  # pos camera
        self.drawOpticalElements()
        glFlush()

    def set_rotation(self, rot):
        self._rotation = float(rot)

    def set_tilt(self, theta, phi):
        self._tilt_angle = (float(theta), float(phi))

    def drawOpticalElements(self):
        quadObj = gluNewQuadric()
        h = 0.5
        dy = 3
        r = 5
        NUM_POLYGON = 6
        glColor3f(0.2, 0.6, 0.2)
        for i in range(4):
            glPushMatrix()
            y = -1.5 * dy - h // 2 + i * dy
            glTranslatef(0, y, 0)
            glRotatef(-90, 1.0, 0.0, 0.0)  # along y axis
            if i != 2:  # not tissue
                glRotatef(self._rotation, 0.0, 0.0, 1.0)  # filter rho
            if i == 2:  # tissue
                glRotatef(self._tilt_angle[0], 0.0, 0.0, 1.0)  # tilting
                glRotatef(self._tilt_angle[1], 0.0, 1.0, 0.0)  # tilting
                glRotatef(-self._tilt_angle[0], 0.0, 0.0, 1.0)  # tilting
            gluDisk(quadObj, 0, r, NUM_POLYGON, 1)
            gluCylinder(quadObj, r, r, h, NUM_POLYGON, 1)
            glTranslatef(0, 0, h)
            gluDisk(quadObj, 0, r, NUM_POLYGON, 1)

            glPopMatrix()
