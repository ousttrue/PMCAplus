from pmca_qt.mainframe import *
from pmca_qt.glframe import *
import sys
from PyQt4 import Qt
import PMCA_GL


w=None


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
    w.resize(640, 480)
    #w.setGeometry(300, 300, 250, 150)
    w.show()
    w.bind_pmca(pmca)

    return app
