import tkinter

import PMCA


APPNAME = "PMCA v0.0.6r10"
COMMANDS = {}


def main():
    PMCA.Init_PMD()

    root = tkinter.Tk()

    import main_frame

    app = main_frame.MainFrame(APPNAME, master=root)

    app.init()

    PMCA.CretateViewerThread()

    app.refresh()
    app.mainloop()

    try:
        app.save_CNL_File("./last.cnl")
    except:
        pass

    PMCA.QuitViewerThread()


if __name__ == "__main__":
    main()
