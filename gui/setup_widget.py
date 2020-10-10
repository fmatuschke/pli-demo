import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtOpenGL

from OpenGL.GL import *
from OpenGL.GLU import *

DELTA = 0.25
HEIGHT = 0.1
RADIUS = 0.5
NUM_POLYGON = 42


class SetupWidget(QtOpenGL.QGLWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(SetupWidget, self).__init__(parent, *args, **kwargs)

        self.setMinimumSize(640, 480)
        self.quadObj = gluNewQuadric()

    def cylinder(self, y, rot=[0, 0, 0], color=[0, 0.42, 0]):
        glPushMatrix()
        glColor3f(0.0, 0.42, 0.42)
        glTranslatef(0, y, 0)
        # glRotatef(rot[0], 1.0, 0.0, 0.0)
        # glRotatef(rot[1], 0.0, 1.0, 0.0)
        # glRotatef(rot[2], 0.0, 0.0, 1.0)

        glRotatef(-90, 1.0, 0.0, 0.0)
        gluCylinder(self.quadObj, RADIUS, RADIUS, HEIGHT, NUM_POLYGON, 1)
        gluDisk(self.quadObj, 0, RADIUS, NUM_POLYGON, 1)
        glTranslatef(0, 0, HEIGHT)
        gluDisk(self.quadObj, 0, RADIUS, NUM_POLYGON, 1)
        glPopMatrix()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0, 0, -6)
        glPolygonMode(GL_FRONT, GL_FILL)
        glBegin(GL_POLYGON)
        glColor3f(1.0, 1.0, 1.0)
        glVertex3f(3.0, 0.0, 0.0)
        glVertex3f(3.0, -2.0, 0.0)
        glVertex3f(-3.0, -2.0, 0.0)
        glVertex3f(-3.0, 0.0, 0.0)
        glEnd()

        # glTranslatef(-2, -2, 0)

        # # coordinate system
        # glPolygonMode(GL_FRONT, GL_FILL)
        # glBegin(GL_LINES)
        # glColor3f(1.0, 0.0, 0.0)
        # glVertex3f(0.0, 0.0, 0.0)
        # glVertex3f(10.0, 0.0, 0.0)

        # glColor3f(0.0, 1.0, 0.0)
        # glVertex3f(0.0, 0.0, 0.0)
        # glVertex3f(0.0, 10.0, 0.0)

        # glColor3f(0.0, 0.0, 1.0)
        # glVertex3f(0.0, 0.0, 0.0)
        # glVertex3f(0.0, 0.0, 10.0)
        # glEnd()

        # # cylinder
        # for i in range(4):
        #     self.cylinder(i * DELTA)

        glFlush()

    def initializeGL(self):
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, 1.33, 0.1, 100000.0)
        glMatrixMode(GL_MODELVIEW)

        # setting scene
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
