import tkinter


class MENUBAR:
    def __init__(self, master: tkinter.Tk, app: tkinter.Misc):
        self.menubar = tkinter.Menu(master)
        master.configure(menu=self.menubar)
        files = tkinter.Menu(self.menubar, tearoff=False)
        editing = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="ファイル", underline=0, menu=files)
        self.menubar.add_cascade(label="編集", underline=0, menu=editing)
        files.add_command(label="新規", under=0, command=app.clear)
        files.add_command(label="読み込み", under=0, command=app.load_node)
        files.add_separator
        files.add_command(label="保存", under=0, command=app.save_node)
        files.add_command(label="モデル保存", under=0, command=app.dialog_save_PMD)
        files.add_separator
        files.add_command(label="一括組立て", under=0, command=app.batch_assemble)
        files.add_separator
        files.add_command(
            label="PMDフォーマットチェック", under=0, command=app.savecheck_PMD
        )
        files.add_command(label="PMD概要確認", under=0, command=app.check_PMD)
        files.add_command(label="PMD詳細確認", under=0, command=app.propcheck_PMD)
        files.add_separator

        def quit():
            master.winfo_toplevel().destroy()
            master.quit()

        files.add_command(label="exit", under=0, command=quit)

        editing.add_command(label="体型調整を初期化", under=0, command=app.init_tf)
        editing.add_command(label="材質をランダム選択", under=0, command=app.rand_mat)
        editing.add_command(label="PMCA設定", under=0, command=app.setting_dialog)
