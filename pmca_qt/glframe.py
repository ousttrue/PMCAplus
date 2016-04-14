import sys
import os
sys.path.append(os.getcwd()+'/glglue')
from PyQt4 import Qt
import glglue.sample
import glglue.qgl


class GLFrame(Qt.QWidget):
    def __init__(self, controller):
        Qt.QWidget.__init__(self)
        # setup opengl widget
        self.controller=controller
        self.glwidget=glglue.qgl.Widget(self, self.controller)
        # packing
        mainLayout = Qt.QHBoxLayout()
        mainLayout.addWidget(self.glwidget)
        self.setLayout(mainLayout)
