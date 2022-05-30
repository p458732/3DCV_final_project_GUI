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
        self.meshShaderProgram = None
        self.edgeShaderProgram = None
        self.enableLineDraw = False

    def sizeHint(self):
        return QSize(800, 600)

    def initializeGL(self):
        GL.glClearColor(0.8, 0.8, 0.8, 0.0)

        GL.glEnable(GL.GL_DEPTH_TEST)

        vertShader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Vertex)
        vertShader.compileSourceFile("mesh_shader.vs")
        fragShader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Fragment)
        fragShader.compileSourceFile("mesh_shader.fs")

        shaderProgram = QOpenGLShaderProgram()
        shaderProgram.addShader(vertShader)
        shaderProgram.addShader(fragShader)
        success = shaderProgram.link()
        print("Compile shader state:", "Success" if success else "Fail")
        shaderProgram.bind()

        self.meshShaderProgram = shaderProgram

        vertShader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Vertex)
        vertShader.compileSourceFile("edge_shader.vs")
        fragShader = QOpenGLShader(QOpenGLShader.ShaderTypeBit.Fragment)
        fragShader.compileSourceFile("edge_shader.fs")

        shaderProgram = QOpenGLShaderProgram()
        shaderProgram.addShader(vertShader)
        shaderProgram.addShader(fragShader)
        success = shaderProgram.link()
        print("Compile shader state:", "Success" if success else "Fail")
        shaderProgram.bind()

        self.edgeShaderProgram = shaderProgram

        self.pointLightAmbient = QtGui.QVector3D(0.2, 0.2, 0.2)
        self.pointLightDiffuse = QtGui.QVector3D(0.8, 0.8, 0.8)
        # self.pointLightSpecular =

        near_plane = 0.1
        far_plane = 100
        angle = 45
        aspect = 400 / 300

        self.modelMatrix = QtGui.QMatrix4x4()
        self.modelMatrix.setToIdentity()
        self.modelMatrix.scale(0.005)

        self.centerPosition = QtGui.QVector3D(0.0, 0.0, 0.0)
        self.upDirection = QtGui.QVector3D(0.0, 0.0, 1.0)
        self.yaw, self.pitch = 0, 0
        self.vecLength = 2.0
        self.eyePosition = QtGui.QVector3D(0, 0, 0)
        self.viewMatrix = QtGui.QMatrix4x4()
        self.updateViewMatrix()
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

    def updateViewMatrix(self):
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        self.eyePosition = QtGui.QVector3D(self.vecLength * math.cos(pitch) * math.cos(yaw),
                                           self.vecLength * math.cos(pitch) * math.sin(yaw),
                                           self.vecLength * math.sin(pitch))
        self.viewMatrix.setToIdentity()
        self.viewMatrix.lookAt(self.eyePosition, self.centerPosition, self.upDirection)

    def mouseMoveEvent(self, event):
        dx, dy = event.position().x() - self.prevMouseX, self.prevMouseY - event.position().y()
        self.yaw += dx
        self.pitch += dy
        self.updateViewMatrix()
        self.prevMouseX = event.position().x()
        self.prevMouseY = event.position().y()
        self.update()

    def wheelEvent(self, event):
        if self.vecLength - event.angleDelta().y() / 360 < 0.01 or self.vecLength - event.angleDelta().y() / 360 > 100.0:
            pass
        else:
            self.vecLength -= event.angleDelta().y() / 600
            self.updateViewMatrix()
            self.update()

    def flushBufferFromMesh(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.faceCount = len(faces) * 3
        import numpy as np
        f = np.array(self.faces)
        self.normals = np.array(self.vertices)[f]
        self.normals = np.cross(self.normals[:, 0, :] - self.normals[:, 1, :],
                                self.normals[:, 2, :] - self.normals[:, 1, :], axis=1)
        # normal per face
        self.normals = np.transpose(self.normals.T / np.linalg.norm(self.normals, axis=1))
        self.normals_per_vertices = np.zeros_like(self.vertices)
        for face_id, face in enumerate(faces):
            self.normals_per_vertices[face[0]] += self.normals[face_id]
            self.normals_per_vertices[face[1]] += self.normals[face_id]
            self.normals_per_vertices[face[2]] += self.normals[face_id]
        self.normals_per_vertices = np.transpose(
            self.normals_per_vertices.T / np.linalg.norm(self.normals_per_vertices, axis=1))

        self.edges = np.vstack((f[:, 0:2], f[:, 1:3], f[:, 0:4:2]))
        self.edgeCount = len(self.edges) * 2
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
            self.meshShaderProgram.bind()
            self.meshShaderProgram.setUniformValue("mvp_matrix",
                                                   self.projectionMatrix * self.viewMatrix * self.modelMatrix)
            self.meshShaderProgram.setUniformValue("inv_model_matrix", self.modelMatrix.normalMatrix())
            self.meshShaderProgram.setUniformValue("model_matrix", self.modelMatrix)
            self.meshShaderProgram.setUniformValue("eye_position", self.eyePosition)
            self.meshShaderProgram.setUniformValue("light_position", self.eyePosition)
            self.meshShaderProgram.setUniformValue("ambient_color", self.pointLightAmbient)
            self.meshShaderProgram.setUniformValue("diffuse_color", self.pointLightDiffuse)

            GL.glEnableVertexAttribArray(0)

            # self.vertex_buf.bind()
            # self.index_buf.bind()
            # vertex_loc = self.shaderProgram.attributeLocation("position")
            # self.shaderProgram.enableAttributeArray(vertex_loc)
            # self.shaderProgram.setAttributeBuffer(vertex_loc, GL.GL_FLOAT, 0, 3)

            GL.glEnableVertexAttribArray(0)
            GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, self.vertices)
            GL.glEnableVertexAttribArray(1)
            GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, self.normals_per_vertices)
            GL.glDrawElements(GL.GL_TRIANGLES, self.faceCount, GL.GL_UNSIGNED_INT, self.faces)
            # GL.glDrawElements(GL.GL_TRIANGLES, self.faceCount, GL.GL_UNSIGNED_INT, None)

            GL.glDisableVertexAttribArray(0)

            # self.index_buf.release()
            # self.vertex_buf.release()
            self.meshShaderProgram.release()

            if self.enableLineDraw == True:
                self.edgeShaderProgram.bind()
                self.edgeShaderProgram.setUniformValue("mvp_matrix",
                                                       self.projectionMatrix * self.viewMatrix * self.modelMatrix)

                GL.glEnableVertexAttribArray(0)

                # self.vertex_buf.bind()
                # self.index_buf.bind()
                # vertex_loc = self.shaderProgram.attributeLocation("position")
                # self.shaderProgram.enableAttributeArray(vertex_loc)
                # self.shaderProgram.setAttributeBuffer(vertex_loc, GL.GL_FLOAT, 0, 3)

                GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, self.vertices)
                GL.glDrawElements(GL.GL_LINES, self.edgeCount, GL.GL_UNSIGNED_INT, self.edges)
                # GL.glDrawElements(GL.GL_TRIANGLES, self.faceCount, GL.GL_UNSIGNED_INT, None)

                GL.glDisableVertexAttribArray(0)

                # self.index_buf.release()
                # self.vertex_buf.release()
                self.edgeShaderProgram.release()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.typeLabel = QtWidgets.QLabel(self.centralwidget)
        self.typeLabel.setGeometry(QtCore.QRect(30, 30, 421, 21))
        self.typeLabel.setText("Category")
        self.typeLabel.setObjectName("type label")
        self.typeSelecter = QtWidgets.QListWidget(self.centralwidget)
        self.typeSelecter.setGeometry(QtCore.QRect(30, 50, 120, 341))
        self.typeSelecter.setObjectName("typeSelecter")

        self.inputImageLabel = QtWidgets.QLabel(self.centralwidget)
        self.inputImageLabel.setGeometry(QtCore.QRect(180, 30, 421, 21))
        self.inputImageLabel.setText("Input image")
        self.inputImageLabel.setObjectName("input image label")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(180, 50, 441, 341))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.geometricTextureLabel = QtWidgets.QLabel(self.centralwidget)
        self.geometricTextureLabel.setGeometry(QtCore.QRect(30, 421, 421, 21))
        self.geometricTextureLabel.setText("Geometric texture")
        self.geometricTextureLabel.setObjectName("geometric texture label")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget_2.setGeometry(QtCore.QRect(30, 441, 591, 161))
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerItem)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 620, 421, 21))
        self.label.setText("")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 792, 171, 21))
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(30, 672, 161, 41))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(30, 30, 1078, 50))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        fileMenu = self.menubar.addMenu("File")

        importImageAction = QtGui.QAction("Import image", MainWindow)
        fileMenu.addAction(importImageAction)
        self.MainWindow = MainWindow
        importImageAction.triggered.connect(self.getFileDialog)

        self.statusbar.addPermanentWidget(QtWidgets.QLabel(MainWindow))
        self.statusProgressBar = QtWidgets.QProgressBar(MainWindow)
        self.statusbar.addPermanentWidget(self.statusProgressBar)

        self.objectSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self.centralwidget)
        self.objectSlider.setGeometry(QtCore.QRect(260, 672, 300, 30))
        self.objectSlider.setTickInterval(1)
        self.objectSlider.setMinimum(0)
        self.objectSlider.setMaximum(48)
        self.objectSlider.setObjectName("slider")
        self.objectSlider.valueChanged[int].connect(self.changeValue)
        # self.objectSlider.setValue(0)

        self.objectLabel = QtWidgets.QLabel(self.centralwidget)
        self.objectLabel.setGeometry(QtCore.QRect(200, 672, 50, 21))
        self.objectLabel.setText("Level: 0")
        self.objectLabel.setObjectName("object label")

        self.openGLWidget = GLWidget(self.centralwidget)
        # pos_y, pos_x, height, width
        self.openGLWidget.setGeometry(QtCore.QRect(650, 10, 800, 600))

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # placeholder
        self.tableWidgetCount = 0

    def getFileDialog(self):
        if len(self.typeSelecter.selectedItems()) <= 0:
            self.statusbar.showMessage("[ERROR] Haven't assign category to open image to.")
            return
        filePath, type = QtWidgets.QFileDialog.getOpenFileName(
            self.MainWindow, "Open File", ".", "Images (*.png *.jpg)")

        position = self.tableWidgetCount
        self.tableWidgetCount += 1
        self.tableWidget.setRowCount(int(self.tableWidgetCount / 6) + 1)
        t = QtWidgets.QTableWidgetItem()
        t.setData(QtCore.Qt.ItemDataRole.DecorationRole,
                  QtGui.QPixmap.fromImage(QtGui.QImage(filePath)).scaled(64, 64))
        t.imagePath = filePath
        self.tableWidget.setItem(position//6, position%6, t)

    def changeValue(self, value):
        self.objectLabel.setText("Level: " + str(value))
        # TODO wire extracted object filename, flush mesh from this member function

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Start"))
