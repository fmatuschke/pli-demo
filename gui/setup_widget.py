import numpy as np

import moderngl
from moderngl_window.opengl.projection import Projection3D

from PyQt5 import QtOpenGL, QtWidgets, QtGui, QtCore


class SetupWidget(QtOpenGL.QGLWidget):
    '''
    Widget that renders a schematic PLI-Setup
    '''

    def __init__(self, parent=None, *args, **kwargs):
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(SetupWidget, self).__init__(fmt, None)
        self.init_shaders()
        self.tilt = 1
        self.rotation = 0

    def resizeEvent(self, event):
        # w = event.size().width()
        # h = event.size().height()
        # if w > 5 * h:
        #     w = h // 5
        # else:
        #     h = w * 5
        # self.setMaximumSize(w, h)
        # event = QtGui.QResizeEvent(QtCore.QSize(w, h), event.oldSize())
        super(SetupWidget, self).resizeEvent(event)

    def init_shaders(self):
        '''
        Loads the renderings shaders
        '''
        self.vertex_file = "shader/3dshader.vert"
        self.vertex_string = open(self.vertex_file, 'r').read()

        self.geom_file = "shader/3dshader.geom"
        self.geom_string = open(self.geom_file, 'r').read()

        self.frag_file = "shader/3dshader.frag"
        self.frag_string = open(self.frag_file, 'r').read()

    def create_data(self):
        '''
        Creates a cylinder for every optical element
        '''
        if (self.tilt == 0):
            tiltdirection = [0, 1, 0]
        elif (self.tilt == 1):
            tiltdirection = [0, 1, -0.2]
        elif (self.tilt == 2):
            tiltdirection = [0.2, 1, 0]
        elif (self.tilt == 3):
            tiltdirection = [0, 1, 0.2]
        elif (self.tilt == 4):
            tiltdirection = [-0.2, 1, 0]
        else:
            raise ValueError("Wrong tilt")

        dy = 1
        h = 0.25
        z_pos = -50
        positions = np.array([[0, -1.5 * dy - h / 2, z_pos],
                              [0, -1.5 * dy + h / 2, z_pos],
                              [0, -0.5 * dy - h / 2, z_pos],
                              [0, -0.5 * dy + h / 2, z_pos],
                              [0, 0.5 * dy - h / 2, z_pos],
                              [0, 0.5 * dy + h / 2, z_pos],
                              [0, 1.5 * dy - h / 2, z_pos],
                              [0, 1.5 * dy + h / 2, z_pos]])
        orientations = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0],
                                 tiltdirection, tiltdirection, [0, 1, 0],
                                 [0, 1, 0], [0, 1, 0]])
        self.data = np.hstack((positions, orientations))

    def set_rotation(self, rotation):
        '''
        Slot function which changes the tiltdirection and updates the rendering scene
        '''
        self.rotation = rotation
        self.update()

    def set_tilt(self, tilt):
        '''
        Slot function which changes the tiltdirection and updates the rendering scene
        '''
        self.tilt = tilt
        self.update()

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.prog = self.ctx.program(
            vertex_shader=self.vertex_string,
            geometry_shader=self.geom_string,
            fragment_shader=self.frag_string,
        )
        project = Projection3D(1, 4.2, 0.1, 1000.0)
        project = tuple(np.array(project.matrix).flatten().T)
        self.prog['worldToCamera'].value = project

    def paintGL(self):
        # always same via aspect ratio
        w = self.width()
        h = self.height()
        if w > 2 * h:
            w = h * 2
        else:
            h = w // 2

        self.ctx.viewport = (0, 0, w, h)
        self.ctx.clear(46 / 255, 48 / 255, 58 / 255)
        # self.ctx.clear(38 / 255, 65 / 255, 100 / 255)
        self.create_data()
        vbo = self.ctx.buffer(self.data.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'v_position',
                                                'v_orientation')
        self.vao.render(mode=1)
        self.ctx.finish()
