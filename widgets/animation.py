import os
import pathlib

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from PyQt5 import QtCore, QtGui, QtOpenGL, QtWidgets

PATH = os.path.join(pathlib.Path().absolute(), 'data')


class SetupWidget(QtOpenGL.QGLWidget):
    '''
    Widget that renders a schematic PLI-Setup
    '''

    def __init__(self, parent=None, *args, **kwargs):
        super(SetupWidget, self).__init__(parent)
        self._tilt_angle = (0, 10)
        self._rotation = 0
        self._tex = {
            "lines":
                self.get_pattern_lines(),
            "cross":
                self.get_pattern_cross(),
            "polfilter":
                self.get_pattern_polfilter(),
            "section":
                self.greening_texture(
                    self.read_texture(os.path.join(PATH, "section.png"))),
            "test":
                self.get_pattern_test()
        }

        self.initializeGL()

    def resizeEvent(self, event):
        super(SetupWidget, self).resizeEvent(event)
        w, h = max(1, self.size().width()), max(1, self.size().height())
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
        w, h = max(1, self.size().width()), max(1, self.size().height())
        gluPerspective(20.0, w / h, 0.1, 1000.0)
        glViewport(0, 0, w, h)
        glMatrixMode(GL_MODELVIEW)

        self._quadObj = gluNewQuadric()
        gluQuadricTexture(self._quadObj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        self._tex_dict = self.bind_texture(self._quadObj)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -75)  # pos camera, ie move objects away
        glRotatef(20, 1, 0, 0)
        glRotatef(-20, 0, 1, 0)

        # coordinate system
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(10, 0, 0)
        glEnd()
        glBegin(GL_LINES)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 10, 0)
        glEnd()
        glBegin(GL_LINES)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 10)
        glEnd()

        self.drawOpticalElements()
        self.drawOtherElements()
        glFlush()

    def set_rotation(self, rot):
        if rot is None:
            return
        self._rotation = np.rad2deg(float(rot))

    def set_tilt(self, theta, phi):
        self._tilt_angle = (float(theta), float(phi))

    def read_texture(self, file_name):
        if os.path.isfile(file_name):
            img = Image.open(file_name)
            img = np.array(img, np.uint8)
            return img
        print(f"WARNING: texture '{file_name}' not found")
        return None

    def greening_texture(self, tex):
        if tex is None:
            return None

        shape = tex.shape
        tex.shape = (-1, 4)
        tex[:, 0] = tex[:, 0] * 0.25
        tex[:, 2] = tex[:, 2] * 0.25
        alpha = tex[:, 3]
        tex[alpha != 0, 3] = 150
        tex.shape = shape

        return tex

    def get_pattern_test(self):
        texture = np.zeros((16, 16, 3), np.uint8)
        v = np.mgrid[0:256].reshape(16, 16)
        texture[:, :, 0] = v
        texture[:, :, 1] = v.T
        return texture

    def get_pattern_lines(self):
        texture = np.zeros((180, 180, 4), np.uint8)
        texture[None, None, :] = [180, 180, 180, 25]
        for i in range(0, texture.shape[1], 10):
            texture[:, i, 0] = 0
            texture[:, i, 1] = 0
            texture[:, i, 2] = 0
            texture[:, i, 3] = 125
        return texture

    def get_pattern_cross(self):
        texture = np.zeros((180, 180, 4), np.uint8)
        texture[:, texture.shape[1] // 2 - 5:texture.shape[1] // 2 +
                5, :] = [0, 0, 0, 125]
        texture[texture.shape[0] // 2 - 5:texture.shape[0] // 2 +
                5, :, :] = [0, 0, 0, 125]
        return texture

    def get_pattern_polfilter(self):
        texture = np.zeros((180, 180, 4), np.uint8)
        texture[None, texture.shape[1] // 2 - 5:texture.shape[1] // 2 +
                5, :] = [0, 0, 0, 125]
        return texture

    def bind_texture(self, quadObj):

        textID = glGenTextures(len(self._tex))
        tex_dict = {}
        for tex_id, (tex_name, tex) in zip(textID, self._tex.items()):
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            if tex.shape[2] == 3:
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, tex.shape[1],
                             tex.shape[0], 0, GL_RGB, GL_UNSIGNED_BYTE,
                             tex.ravel())
            if tex.shape[2] == 4:
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex.shape[1],
                             tex.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE,
                             tex.ravel())
            glBindTexture(GL_TEXTURE_2D, tex_id)
            tex_dict[tex_name] = tex_id
        return tex_dict

    def drawOpticalElements(self):
        glPushMatrix()

        # glucylinder are orientatet along z axis, -> rotate to y axis
        glRotatef(-90, 1.0, 0.0, 0.0)

        h = 0.5
        dy = 4
        r = 5
        NUM_POLYGON = 42
        glColor3f(0.7, 0.7, 0.7)
        for i in range(4):
            glPushMatrix()
            y = -1.5 * dy - h // 2 + i * dy
            glTranslatef(0, 0, y)
            if i != 2:  # not tissue
                glRotatef(self._rotation, 0.0, 0.0, 1.0)  # filter rho
            if i == 2:  # tissue
                glRotatef(self._tilt_angle[1], 0.0, 0.0, 1.0)  # tilting
                glRotatef(self._tilt_angle[0], 0.0, 1.0, 0.0)  # tilting
                glRotatef(-self._tilt_angle[1], 0.0, 0.0, 1.0)  # tilting
            # bottom texture
            if i == 0:
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["polfilter"])
            if i == 1:
                glRotatef(45, 0.0, 0.0, 1.0)
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["cross"])
            if i == 2:
                glRotatef(180, 0.0, 0.0, 1.0)
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["section"])
            if i == 3:
                glRotatef(90, 0.0, 0.0, 1.0)
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["polfilter"])

            gluDisk(self._quadObj, 0, r, NUM_POLYGON, 1)
            glBindTexture(GL_TEXTURE_2D, self._tex_dict["lines"])
            gluCylinder(self._quadObj, r, r, h, NUM_POLYGON, 1)

            # top texture
            glTranslatef(0, 0, h)
            if i == 0:
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["polfilter"])
            if i == 1:
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["cross"])
            if i == 2:
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["section"])
            if i == 3:
                glBindTexture(GL_TEXTURE_2D, self._tex_dict["polfilter"])
            gluDisk(self._quadObj, 0, r, NUM_POLYGON, 1)

            glPopMatrix()
        glPopMatrix()

    def drawOtherElements(self):
        # LED
        glPushMatrix()
        glColor3f(0.2, 0.8, 0.2)
        glBegin(GL_POLYGON)
        z = -12.5
        glVertex3f(5, z, 5)
        glVertex3f(-5, z, 5)
        glVertex3f(-5, z, -5)
        glVertex3f(5, z, -5)
        glEnd()
        glPopMatrix()

        # CAMERA
        glPushMatrix()
        glTranslatef(0, 13, 0)
        glColor3f(0.3, 0.3, 0.3)
        h = 0.5
        wy = 2
        wx = 2
        glBegin(GL_QUADS)
        for z in [-1.0, 1.0]:
            glNormal3f(0.0, -z, 0.0)
            glVertex3f(wx, z * h, -wy)
            glVertex3f(wx, z * h, wy)
            glVertex3f(-wx, z * h, wy)
            glVertex3f(-wx, z * h, -wy)

        for x in [-1.0, 1.0]:
            glVertex3f(x * wx, h, wy)
            glVertex3f(x * wx, h, -wy)
            glVertex3f(x * wx, -h, -wy)
            glVertex3f(x * wx, -h, wy)

        for y in [-1.0, 1.0]:
            glVertex3f(-wx, h, y * wy)
            glVertex3f(-wx, -h, y * wy)
            glVertex3f(wx, -h, y * wy)
            glVertex3f(wx, h, y * wy)
        glEnd()

        # LENSE
        gobj = gluNewQuadric()
        glTranslatef(0, -h, 0)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gobj, 1.5, 1.5, 0.75, 42, 1)
        glPopMatrix()
