import tkinter.ttk


class InfoTab(tkinter.ttk.Frame):
    """
    +--------+------+
    |material|select|
    +--------+------+
    |comment        |
    +---------------+
    """

    def __init__(self, master: tkinter.Misc):
        super().__init__(master=master)
        self.text = "Info"
