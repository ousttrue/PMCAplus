from pmca_tkinter.mainframe import *
from pmca_tkinter.tabs import *
from pmca_tkinter.utils import *
from pmca_tkinter.glframe import *
import PMCA_GL


def App(pmca, scene):
    glcontroller=PMCA_GL.GLController(root=scene)
    glcontroller.name="TKINTER"

    # bind pmca with opengl
    def update_gl():
        scene.clear()
        model=PMCA_GL.ModelVBO(*pmca.get_model())
        scene.add_item(model, model.draw)
    pmca.model_update_observable.add(update_gl)

    tkinter_app=MainFrame(glcontroller)
    tkinter_app.bind_pmca(pmca)
    return tkinter_app
