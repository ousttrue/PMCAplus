import sys
import os
sys.path.append(os.getcwd()+'/glglue')
import tkinter
import glglue.togl
import glglue.sample
from logging import getLogger
logger = getLogger(__name__)


class GLFrame(tkinter.Frame):
    def __init__(self, master, controller, width=None, height=None, **kw):
        #super(Frame, self).__init__(master, **kw)
        tkinter.Frame.__init__(self, master, **kw)
        # setup opengl widget
        self.controller=controller
        self.glwidget=glglue.togl.Widget(
                self, self.controller, width=width, height=height)
        self.glwidget.pack(fill=tkinter.BOTH, expand=True)
        # event binding(require focus)
        self.bind('<Key>', self.onKeyDown)
        self.bind('<MouseWheel>', lambda e: self.controller.onWheel(-e.delta) and self.glwidget.onDraw())

    def onKeyDown(self, event):
        key=event.keycode
        if key==27:
            # Escape
            sys.exit()
        if key==81:
            # q
            sys.exit()
        else:
            logger.debug("keycode: %d", key)
