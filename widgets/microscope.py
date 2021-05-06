import os
import pathlib

import numpy as np
from OpenGL import GL, GLU
from PIL import Image
from PyQt5 import QtOpenGL

PATH = os.path.join(pathlib.Path().absolute(), 'data')


class SetupWidget(QtOpenGL.QGLWidget):
    """
    Widget that renders a schematic PLI-Setup
    """

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

    def resizeEvent(self, event):
        super(SetupWidget, self).resizeEvent(event)
        w, h = max(1, self.size().width()), max(1, self.size().height())
        GL.glViewport(0, 0, w, h)

    def initializeGL(self):
        # will be called from qt
        GL.glClearDepth(1.0)
        GL.glClearColor(0.2, 0.2, 0.2, 0.0)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glMatrixMode(GL.GL_PROJECTION)

        GL.glLightModeli(GL.GL_LIGHT_MODEL_LOCAL_VIEWER, GL.GL_TRUE)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_COLOR_MATERIAL)

        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])

        GL.glLoadIdentity()
        w, h = max(1, self.size().width()), max(1, self.size().height())
        GLU.gluPerspective(20.0, w / h, 0.1, 1000.0)
        GL.glViewport(0, 0, w, h)
        GL.glMatrixMode(GL.GL_MODELVIEW)

        self._quadObj = GLU.gluNewQuadric()
        GLU.gluQuadricTexture(self._quadObj, GL.GL_TRUE)
        GL.glEnable(GL.GL_TEXTURE_2D)
        self._tex_dict = self.bind_texture(self._quadObj)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslatef(0, 0, -75)  # pos camera, ie move objects away
        GL.glRotatef(20, 1, 0, 0)
        GL.glRotatef(-20, 0, 1, 0)

        # coordinate system
        GL.glBegin(GL.GL_LINES)
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glVertex3f(0, 0, 0)
        GL.glVertex3f(10, 0, 0)
        GL.glEnd()
        GL.glBegin(GL.GL_LINES)
        GL.glColor3f(0.0, 1.0, 0.0)
        GL.glVertex3f(0, 0, 0)
        GL.glVertex3f(0, 10, 0)
        GL.glEnd()
        GL.glBegin(GL.GL_LINES)
        GL.glColor3f(0.0, 0.0, 1.0)
        GL.glVertex3f(0, 0, 0)
        GL.glVertex3f(0, 0, 10)
        GL.glEnd()

        self.drawOpticalElements()
        self.drawOtherElements()
        GL.glFlush()

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

        textID = GL.glGenTextures(len(self._tex))
        tex_dict = {}
        for tex_id, (tex_name, tex) in zip(textID, self._tex.items()):
            GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
            GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
                               GL.GL_CLAMP)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
                               GL.GL_CLAMP)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
                               GL.GL_REPEAT)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
                               GL.GL_REPEAT)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                               GL.GL_NEAREST)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                               GL.GL_NEAREST)
            GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_DECAL)
            if tex.shape[2] == 3:
                GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, tex.shape[1],
                                tex.shape[0], 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE,
                                tex.ravel())
            if tex.shape[2] == 4:
                GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, tex.shape[1],
                                tex.shape[0], 0, GL.GL_RGBA,
                                GL.GL_UNSIGNED_BYTE, tex.ravel())
            GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
            tex_dict[tex_name] = tex_id
        return tex_dict

    def drawOpticalElements(self):
        GL.glPushMatrix()

        # glucylinder are orientatet along z axis, -> rotate to y axis
        GL.glRotatef(-90, 1.0, 0.0, 0.0)

        h = 0.5
        dy = 4
        r = 5
        NUM_POLYGON = 42
        GL.glColor3f(0.7, 0.7, 0.7)
        for i in range(4):
            GL.glPushMatrix()
            y = -1.5 * dy - h // 2 + i * dy
            GL.glTranslatef(0, 0, y)
            if i != 2:  # not tissue
                GL.glRotatef(self._rotation, 0.0, 0.0, 1.0)  # filter rho
            if i == 2:  # tissue
                GL.glRotatef(self._tilt_angle[1], 0.0, 0.0, 1.0)  # tilting
                GL.glRotatef(self._tilt_angle[0], 0.0, 1.0, 0.0)  # tilting
                GL.glRotatef(-self._tilt_angle[1], 0.0, 0.0, 1.0)  # tilting
            # bottom texture
            if i == 0:
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["polfilter"])
            if i == 1:
                GL.glRotatef(45, 0.0, 0.0, 1.0)
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["cross"])
            if i == 2:
                GL.glRotatef(180, 0.0, 0.0, 1.0)
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["section"])
            if i == 3:
                GL.glRotatef(90, 0.0, 0.0, 1.0)
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["polfilter"])

            GLU.gluDisk(self._quadObj, 0, r, NUM_POLYGON, 1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["lines"])
            GLU.gluCylinder(self._quadObj, r, r, h, NUM_POLYGON, 1)

            # top texture
            GL.glTranslatef(0, 0, h)
            if i == 0:
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["polfilter"])
            if i == 1:
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["cross"])
            if i == 2:
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["section"])
            if i == 3:
                GL.glBindTexture(GL.GL_TEXTURE_2D, self._tex_dict["polfilter"])
            GLU.gluDisk(self._quadObj, 0, r, NUM_POLYGON, 1)

            GL.glPopMatrix()
        GL.glPopMatrix()

    def drawOtherElements(self):
        # LED
        GL.glPushMatrix()
        GL.glColor3f(0.2, 0.8, 0.2)
        GL.glBegin(GL.GL_POLYGON)
        z = -12.5
        GL.glVertex3f(5, z, 5)
        GL.glVertex3f(-5, z, 5)
        GL.glVertex3f(-5, z, -5)
        GL.glVertex3f(5, z, -5)
        GL.glEnd()
        GL.glPopMatrix()

        # CAMERA
        GL.glPushMatrix()
        GL.glTranslatef(0, 13, 0)
        GL.glColor3f(0.3, 0.3, 0.3)
        h = 0.5
        wy = 2
        wx = 2
        GL.glBegin(GL.GL_QUADS)
        for z in [-1.0, 1.0]:
            GL.glNormal3f(0.0, -z, 0.0)
            GL.glVertex3f(wx, z * h, -wy)
            GL.glVertex3f(wx, z * h, wy)
            GL.glVertex3f(-wx, z * h, wy)
            GL.glVertex3f(-wx, z * h, -wy)

        for x in [-1.0, 1.0]:
            GL.glVertex3f(x * wx, h, wy)
            GL.glVertex3f(x * wx, h, -wy)
            GL.glVertex3f(x * wx, -h, -wy)
            GL.glVertex3f(x * wx, -h, wy)

        for y in [-1.0, 1.0]:
            GL.glVertex3f(-wx, h, y * wy)
            GL.glVertex3f(-wx, -h, y * wy)
            GL.glVertex3f(wx, -h, y * wy)
            GL.glVertex3f(wx, h, y * wy)
        GL.glEnd()

        # LENSE
        gobj = GLU.gluNewQuadric()
        GL.glTranslatef(0, -h, 0)
        GL.glRotatef(90, 1, 0, 0)
        GLU.gluCylinder(gobj, 1.5, 1.5, 0.75, 42, 1)
        GL.glPopMatrix()
