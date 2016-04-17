from pmca_qt.mainframe import *
import sys
from PyQt4 import Qt
import PMCA_GL
import logging


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg) 


class MainLoop:
    def __init__(self, app, window):
        self.app=app
        self.window=window

    def mainloop(self):
        sys.exit(self.app.exec_())
        '''
        while True:
            try:
                self.app.processEvents()
            except:
                break
                '''

def App(pmca, scene):
    global w
    app = Qt.QApplication(sys.argv)

    controller=PMCA_GL.GLController(root=scene)
    controller.name="QT"

    # bind pmca with opengl
    def update_gl():
        scene.clear()
        model=PMCA_GL.ModelVBO(*pmca.get_model())
        scene.add_item(model, model.draw)
    pmca.model_update_observable.add(update_gl)

    w=MainFrame(controller)
    w.resize(1024, 600)
    #w.setGeometry(300, 300, 250, 150)
    w.show()
    w.bind_pmca(pmca)

    return MainLoop(app, w)
