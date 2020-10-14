import numpy as np

import moderngl
from moderngl_window.opengl.projection import Projection3D

from PyQt5 import QtOpenGL, QtWidgets
from PyQt5.QtGui import QMatrix4x4


class SetupWidget(QtOpenGL.QGLWidget):
    '''
    Widget that renders a schematic PLI-Setup
    '''

    def __init__(self, parent=None, *args, **kwargs):
        self.init_shaders()
        self.tilt = 1
        self.rotation = 0
        fmt = QtOpenGL.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super(SetupWidget, self).__init__(fmt, None)

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

        z_pos = -50
        positions = np.array([[0, -0.714, z_pos], [0, -0.571, z_pos],
                              [0, -0.286, z_pos], [0, -0.143, z_pos],
                              [0, 0.143, z_pos], [0, 0.286, z_pos],
                              [0, 0.571, z_pos], [0, 0.741, z_pos]])
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

        project = Projection3D(min(1,
                                   self.width() / self.height()), 4.2, 0.1,
                               1000.0)
        project = tuple(np.array(project.matrix).flatten().T)
        self.prog['worldToCamera'].value = project

    def paintGL(self):
        # always same vie aspect ratio
        w = self.width()
        h = self.height()
        if h > 3 * w:
            h = w * 3
        else:
            w = h // 3

        self.ctx.viewport = (0, 0, w, h)
        self.ctx.clear(0.9, 0.9, 0.9)
        self.create_data()
        vbo = self.ctx.buffer(self.data.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'v_position',
                                                'v_orientation')
        self.vao.render(mode=1)
        self.ctx.finish()
