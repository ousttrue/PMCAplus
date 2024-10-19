import tkinter.ttk


class TransformTab(tkinter.ttk.Frame):
    def __init__(self, master: tkinter.Misc):
        super().__init__(master=master)
        self.text = "Transform"
