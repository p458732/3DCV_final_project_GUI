# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtCore import QSize
from PyQt6 import QtOpenGLWidgets
from PyQt6.QtOpenGL import QOpenGLShaderProgram, QOpenGLShader, QOpenGLBuffer
from OpenGL import GL

import trimesh
import array
import math


class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.vertices = []
        self.faces = []
        self.faceCount = 0
        mesh = trimesh.load("00.obj")
        self.flushBufferFromMesh(mesh.vertices, mesh.faces)
        self.shaderProgram = None

    def sizeHint(self):
        return QSize(400, 300)

    def initializeGL(self):
        GL.glClearColor(0.8, 0.8, 0.8, 0.0)

        GL.glEnable(GL.GL_DEPTH_TEST)
        vertShader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Vertex)
        vertShader.compileSourceFile("shader.vs")
        fragShader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Fragment)
        fragShader.compileSourceFile("shader.fs")

        shaderProgram = QOpenGLShaderProgram()
        shaderProgram.addShader(vertShader)
        shaderProgram.addShader(fragShader)
        success = shaderProgram.link()
        print("Compile shader state:", "Success" if success else "Fail")
        shaderProgram.bind()

        self.shaderProgram = shaderProgram

        near_plane = 1
        far_plane = 200
        angle = 45
        aspect = 400 / 300

        self.modelMatrix = QtGui.QMatrix4x4()
        self.modelMatrix.setToIdentity()
        self.modelMatrix.scale(0.01)

        self.eyePosition = QtGui.QVector3D(0.0, 1.0, 0.0)
        self.centerPosition = QtGui.QVector3D(0.0, 0.0, 0.0)
        self.upDirection = QtGui.QVector3D(0.0, 0.0, 1.0)
        self.yaw, self.pitch = 0, 0
        self.viewMatrix = QtGui.QMatrix4x4()
        self.viewMatrix.setToIdentity()
        self.viewMatrix.lookAt(self.eyePosition, self.centerPosition, self.upDirection)

        self.projectionMatrix = QtGui.QMatrix4x4()
        self.projectionMatrix.setToIdentity()
        self.projectionMatrix.perspective(
            angle, aspect, near_plane, far_plane)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self._draw()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        GL.glViewport((width - side) // 2, (height - side) // 2, side, side)

    def mousePressEvent(self, event):
        self.prevMouseX = event.position().x()
        self.prevMouseY = event.position().y()
        print(self.prevMouseX, self.prevMouseY)

    def mouseMoveEvent(self, event):
        dx, dy = event.position().x() - self.prevMouseX, self.prevMouseY - event.position().y()
        self.yaw += dx
        self.pitch += dy
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        vecLength = 2.0
        self.eyePosition = QtGui.QVector3D(vecLength * -math.cos(pitch) * math.cos(yaw), vecLength * -math.sin(pitch),
                                               vecLength * -math.cos(pitch) * math.sin(yaw))
        self.viewMatrix.setToIdentity()
        self.viewMatrix.lookAt(self.eyePosition, self.centerPosition, self.upDirection)
        self.prevMouseX = event.position().x()
        self.prevMouseY = event.position().y()
        self.paintGL()
        self.update()

    def flushBufferFromMesh(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.faceCount = len(faces) * 3
        # self.vertices = [[0.5, 0.5, 0.0], [-0.5, 0.5, 0.0], [0.5, -0.5, 0.0]]
        # self.faces = [[0, 1, 2]]
        # self.faceCount = len(self.faces) * 3

        # self.vertex_buf = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
        # self.vertex_buf.create()
        # self.vertex_buf.bind()
        # verts = array.array('f')
        # for vert in self.vertices:
        #     verts.extend(vert)
        # self.vertex_buf.allocate(verts, len(verts) * 4)
        # self.vertex_buf.release()
        #
        # self.index_buf = QOpenGLBuffer(QOpenGLBuffer.Type.IndexBuffer)
        # self.index_buf.create()
        # self.index_buf.bind()
        # indices = array.array('I')
        # for face in self.faces:
        #     indices.extend(face)
        # self.index_buf.allocate(indices, len(indices) * 4)
        # self.index_buf.release()

    def _draw(self):
        if len(self.vertices) > 0 and len(self.faces) > 0:
            self.shaderProgram.bind()
            self.shaderProgram.setUniformValue("mvp_matrix", self.projectionMatrix * self.viewMatrix * self.modelMatrix)

            GL.glEnableVertexAttribArray(0)

            # self.vertex_buf.bind()
            # self.index_buf.bind()
            # vertex_loc = self.shaderProgram.attributeLocation("position")
            # self.shaderProgram.enableAttributeArray(vertex_loc)
            # self.shaderProgram.setAttributeBuffer(vertex_loc, GL.GL_FLOAT, 0, 3)

            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, self.vertices)
            GL.glDrawElements(GL.GL_TRIANGLES, self.faceCount, GL.GL_UNSIGNED_INT, self.faces)
            # GL.glDrawElements(GL.GL_TRIANGLES, self.faceCount, GL.GL_UNSIGNED_INT, None)

            GL.glDisableVertexAttribArray(0)

            # self.index_buf.release()
            # self.vertex_buf.release()
            self.shaderProgram.release()



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.typeSelecter = QtWidgets.QListWidget(self.centralwidget)
        self.typeSelecter.setGeometry(QtCore.QRect(30, 90, 191, 341))
        self.typeSelecter.setObjectName("typeSelecter")
        self.imageDisplay = QtWidgets.QListWidget(self.centralwidget)
        self.imageDisplay.setGeometry(QtCore.QRect(290, 90, 491, 341))
        self.imageDisplay.setObjectName("imageDisplay")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.openGLWidget = GLWidget(self.centralwidget)
        # pos_y, pos_x, height, width
        self.openGLWidget.setGeometry(QtCore.QRect(800, 10, 400, 300))

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
