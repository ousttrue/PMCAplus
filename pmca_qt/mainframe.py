import sys
from PyQt4 import Qt
import PyPMCA
import pmca_qt


class MainWidget(Qt.QWidget):
    def __init__(self, glcontroller):
        super().__init__()

        quitButton = Qt.QPushButton("QUIT")

        hbox = Qt.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(quitButton)

        vbox = Qt.QVBoxLayout()
        vbox.addWidget(pmca_qt.GLFrame(glcontroller))
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)    


class MainFrame(Qt.QMainWindow):   
    def __init__(self, glcontroller):
        super().__init__()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle(PyPMCA.APP_NAME)
        self.setCentralWidget(MainWidget(glcontroller))
