from email.mime import image
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QPushButton
from UI import Ui_MainWindow
import sys
import os
import glob

typeList = ['bed', 'trash can', 'cabinet', 'bathtub', 'bookshelf', 'chair', 'clock', 'dishwasher', 'faucet', 'file cabinet', 'lamp'\
            'pillow', 'sofa', 'table']

test1 = ['ss','sss','ss','ssa']
test2 = ['ttt','tqt', 'ttttttt']

class QCustomQWidget (QtWidgets.QWidget):
    # TODO: Need to change to buttons
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        self.textQVBoxLayout = QtWidgets.QVBoxLayout()
        self.textUpQLabel    = QtWidgets.QLabel()
        self.textDownQLabel  = QtWidgets.QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout  = QtWidgets.QHBoxLayout()
        self.iconQLabel      = QtWidgets.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        # setStyleSheet
        self.textUpQLabel.setStyleSheet('''
            color: rgb(0, 0, 255);
        ''')
        self.textDownQLabel.setStyleSheet('''
            color: rgb(255, 0, 0);
        ''')

    def setTextUp (self, text):
        self.textUpQLabel.setText(text)

    def setTextDown (self, text):
        self.textDownQLabel.setText(text)

    def setIcon (self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath).scaled(64,64))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.typeSelecter.addItems(typeList)
        self.ui.typeSelecter.clicked.connect(self.getTypeSelected)


    def createButtons(self, typeName):
        buttons = []
        imagePaths  = glob.glob(os.path.join("./images/" + typeName, "*"))
        for imagePath in imagePaths:
            print(imagePath)
            myQListWidgetItem = QtWidgets.QListWidgetItem(self.ui.imageDisplay)
            myCustomQWidget = QCustomQWidget()
            myCustomQWidget.setIcon(imagePath)
            myCustomQWidget.setTextUp('s')
            myCustomQWidget.setTextDown('na')
            button = QPushButton('', self)
            button.setIcon(QtGui.QIcon(imagePath))
            myQListWidgetItem.setSizeHint(myCustomQWidget.sizeHint())
            self.ui.imageDisplay.addItem(myQListWidgetItem)
            self.ui.imageDisplay.setItemWidget(myQListWidgetItem, myCustomQWidget)
            #buttons.append(myCustomQWidget)
        return buttons

    def getTypeSelected(self, qIndex):
        self.ui.imageDisplay.clear()
        
        self.createButtons(typeList[qIndex.row()])
        
        #self.ui.imageDisplay.addItems(buttons)



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())