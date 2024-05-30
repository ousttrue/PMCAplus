from typing import Any
import pathlib
import os
import shutil
import random
import logging
import tkinter.ttk
from .. import PMCA_asset
from .. import PMCA_cnl
from .. import pmd_type
from .. import native
from . import tabs
from ..app import App
from ..gl_scene import GlScene, PmdSrc
import glglue.tk_frame
import PMCA


LOGGER = logging.getLogger(__name__)


class Buttons(tkinter.ttk.Frame):
    def __init__(self, master: tkinter.Tk):
        super().__init__(master)
        self.QUIT = tkinter.ttk.Button(self)
        self.QUIT["text"] = "QUIT"

        def quit():
            master.winfo_toplevel().destroy()
            master.quit()

        self.QUIT["command"] = quit
        self.QUIT.pack(side=tkinter.RIGHT)


class MainFrame(tkinter.ttk.Frame):
    def __init__(
        self,
        title: str,
        app: App,
    ):
        master = tkinter.Tk()
        master.title(title)

        super().__init__(master)
        self.pack()

        self.app = app
        self.export2folder = False
        self.target_dir = "./model/"

        # setup opengl widget
        self.scene = GlScene()
        self.glwidget = glglue.tk_frame.TkGlFrame(
            master,
            self.scene.render,
        )
        self.glwidget.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.notebook = tabs.Tabs(master, self.app)
        self.notebook.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=0)

        self.frame_button = Buttons(master)
        self.frame_button.pack(padx=5, pady=5, side=tkinter.TOP, fill="x")

        # menu
        self.menubar = tkinter.Menu(master)
        master.configure(menu=self.menubar)

        # menu: files
        files = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="ファイル", underline=0, menu=files)
        files.add_command(label="新規", underline=0, command=self.clear)
        files.add_command(label="読み込み", underline=0, command=self.load_node)
        files.add_separator
        files.add_command(label="保存", underline=0, command=self.save_node)
        files.add_command(label="モデル保存", underline=0, command=self.dialog_save_PMD)
        files.add_separator
        files.add_command(label="一括組立て", underline=0, command=self.batch_assemble)
        files.add_separator
        files.add_command(
            label="PMDフォーマットチェック", underline=0, command=self.savecheck_PMD
        )
        files.add_command(
            label="PMD概要確認", underline=0, command=lambda: native.check_PMD(self)
        )
        files.add_command(label="PMD詳細確認", underline=0, command=self.propcheck_PMD)
        files.add_separator

        def quit():
            master.winfo_toplevel().destroy()
            master.quit()

        files.add_command(label="exit", underline=0, command=quit)

        # menu: editing
        editing = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="編集", underline=0, menu=editing)
        editing.add_command(label="体型調整を初期化", underline=0, command=self.init_tf)
        editing.add_command(
            label="材質をランダム選択", underline=0, command=self.rand_mat
        )
        editing.add_command(label="PMCA設定", underline=0, command=self.setting_dialog)

    def on_refresh(self):
        data = PMCA.Get_PMD(0)
        if data:
            self.scene.set_model(PmdSrc(*data))
            self.notebook.on_refresh()
            self.glwidget.tkExpose(None)

    # functions menu
    def clear(self):
        self.app.load()

    def savecheck_PMD(self):
        self.refresh(level=3)
        model = pmd.Get_PMD(0)

        errors = []

        if len(model.info.name) > 20:
            errors.append(
                "モデル名の長さが20byteを超えています:"
                + str(len(model.info.name))
                + "byte"
            )
        if len(model.info.comment) > 256:
            errors.append(
                "モデルコメントの長さが256byteを超えています:"
                + str(len(model.info.comment))
                + "byte"
            )
        if len(model.info.name_eng) > 20:
            errors.append(
                "英語モデル名の長さが20byteを超えています:"
                + str(len(model.info.name))
                + "byte"
            )
        if len(model.info.comment_eng) > 256:
            errors.append(
                "英語モデルコメントの長さが256byteを超えています:"
                + str(len(model.info.comment))
                + "byte"
            )
        for x in model.mat:
            if (len(x.tex) + len(x.sph)) > 20:
                errors.append(
                    '材質"'
                    + x.name
                    + '"のテクスチャ+スフィアマップの長さが20byteを超えています:'
                    + str(len(x.tex) + len(x.sph))
                    + "byte"
                )

        for x in model.bone:
            if len(x.name) > 20:
                errors.append(
                    'ボーン"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )
            if len(x.name_eng) > 20:
                errors.append(
                    'ボーン"'
                    + x.name
                    + '"の英語名の長さが20byteを超えています:'
                    + str(len(x.name_eng))
                    + "byte"
                )
            i = x.parent
            count = 0
            bone_count = len(model.bone)
            while count < bone_count:
                if i >= bone_count:
                    break
                i = model.bone[i].parent
                count += 1
            else:
                errors.append("循環依存：%s" % (x.name))

        for x in model.skin:
            if len(x.name) > 20:
                errors.append(
                    '表情"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )
            if len(x.name_eng) > 20:
                errors.append(
                    '表情"'
                    + x.name
                    + '"の英語名の長さが20byteを超えています:'
                    + str(len(x.name_eng))
                    + "byte"
                )

        for x in model.bone_grp:
            if len(x.name) > 50:
                errors.append(
                    'ボーングループ"'
                    + x.name
                    + '"の名前の長さが50byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )
            if len(x.name_eng) > 50:
                errors.append(
                    'ボーングループ"'
                    + x.name
                    + '"の英語名の長さが50byteを超えています:'
                    + str(len(x.name_eng))
                    + "byte"
                )

        for x in model.rb:
            if len(x.name) > 20:
                errors.append(
                    '剛体"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )

        for x in model.joint:
            if len(x.name) > 20:
                errors.append(
                    'ジョイント"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )

        for i, x in enumerate(model.face):
            for y in x:
                if y >= len(model.vt):
                    errors.append("面%dの頂点インデックスが不正です:%s" % (i, str(x)))

        for i, x in enumerate(model.vt):
            for y in x.bone_num:
                if y >= len(model.bone):
                    errors.append(
                        "頂点%dのボーンインデックスが不正です:%s" % (i, str(x))
                    )

        if len(errors) == 0:
            errors.append("PMDとして正常に保存できます")

        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        frame.log = Text(frame)
        for x in errors:
            frame.log.insert(END, x + "\n")
        frame.log["state"] = "disabled"
        frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        frame.log["yscrollcommand"] = frame.yscroll.set
        frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        frame.pack(fill=BOTH, expand=1)
        Button(root, text="OK", command=close).pack()
        root.mainloop()

    def propcheck_PMD(self):
        self.refresh(level=3)
        model = pmd.Get_PMD(0)
        string = "name :" + model.info.name
        string += "\ncomment :\n" + model.info.comment
        string += "\n\nname_en :" + model.info.name_eng
        string += "\ncomment_en :\n" + model.info.comment_eng
        string += "\n\n頂点数 :" + str(model.info.data["vt_count"]) + "\n"
        for i, x in enumerate(model.vt):
            string += str(i) + "\n"
            string += "loc:" + str(x.loc) + "\n"
            string += "nor:" + str(x.nor) + "\n"
            string += "uv:" + str(x.uv) + "\n"
            string += "bone:" + str(x.bone_num) + "\n"
            string += "weight:" + str(x.weight) + "\n"
            string += "edge:" + str(x.edge) + "\n\n"

        string += "\n面数　 :" + str(model.info.data["face_count"]) + "\n"
        for i, x in enumerate(model.face):
            string += str(x) + "\n"
        string += "\n材質数 :" + str(model.info.data["mat_count"]) + "\n"
        for i, x in enumerate(model.mat):
            string += str(i) + "\n"
            string += "diff_col:" + str(x.diff_col) + "\n"
            string += "mirr_col:" + str(x.mirr_col) + "\n"
            string += "spec_col:" + str(x.spec_col) + "\n"
            string += "spec:" + str(x.spec) + "\n"
            string += "alpha:" + str(x.alpha) + "\n"
            string += "toon:" + str(x.toon) + "\n"
            string += "edge:" + str(x.edge) + "\n"
            string += "tex:" + x.tex + "\n"
            string += "sph:" + x.sph + "\n"
            string += "face_count:" + str(x.face_count) + "\n\n"

        string += "\nボーン数 :" + str(model.info.data["bone_count"]) + "\n"
        for i, x in enumerate(model.bone):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n"
            string += "name_en:" + x.name_eng + "\n"
            string += "parent:" + str(x.parent) + "\n"
            string += "tail:" + str(x.tail) + "\n"
            string += "type:" + str(x.type) + "\n"
            string += "IK:" + str(x.IK) + "\n"
            string += "loc:" + str(x.loc) + "\n\n"

        string += "\nIK数   :" + str(model.info.data["IK_count"]) + "\n"
        for i, x in enumerate(model.IK_list):
            string += str(i) + "\n"
            string += "index:" + str(x.index) + "\n"
            string += "tail_index:" + str(x.tail_index) + "\n"
            string += "chain_len:" + str(x.chain_len) + "\n"
            string += "iterations:" + str(x.iterations) + "\n"
            string += "weight:" + str(x.weight) + "\n"
            string += "child:" + str(x.child) + "\n\n"

        string += "\n表情数 :" + str(model.info.data["skin_count"]) + "\n"
        for i, x in enumerate(model.skin):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n"
            string += "name_en:" + x.name_eng + "\n"
            string += "count:" + str(x.count) + "\n"
            string += "type:" + str(x.type) + "\n\n"
            # string += 'data:' + x.data + '\n'

        string += (
            "\nボーングループ数 :" + str(model.info.data["bone_group_count"]) + "\n"
        )
        for i, x in enumerate(model.bone_grp):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n"
            string += "name_en:" + x.name_eng + "\n\n"

        string += "\nボーン表示数 :" + str(model.info.data["bone_disp_count"]) + "\n"
        for i, x in enumerate(model.bone_dsp):
            string += str(i) + "\n"
            string += "index:" + str(x.index) + "\n"
            string += "group:" + str(x.group) + "\n\n"

        for i, x in enumerate(model.toon.name):
            string += "%d %s\n" % (i, x)

        string += "\n\n英語対応 :" + str(model.info.data["eng_support"])
        string += "\n\n剛体数 :" + str(model.info.data["rb_count"]) + "\n"
        for i, x in enumerate(model.rb):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n\n"

        string += "\nジョイント数 :" + str(model.info.data["joint_count"]) + "\n"
        for i, x in enumerate(model.joint):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n\n"

        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        frame.log = Text(frame)
        frame.log.insert(END, string)
        frame.log["state"] = "disabled"
        frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        frame.log["yscrollcommand"] = frame.yscroll.set
        frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        frame.pack(fill=BOTH, expand=1)
        Button(root, text="OK", command=close).pack()
        root.mainloop()

    def init_tf(self):
        self.transform_data = [
            pmd.MODEL_TRANS_DATA(
                scale=1.0, pos=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], bones=[], props={}
            )
        ]
        self.refresh()

    def rand_mat(self):
        for x in self.mat_rep.mat.items():
            random.seed()
            x[1].sel = x[1].mat.entries[random.randint(0, len(x[1].mat.entries) - 1)]
        self.refresh()

    def save_node(self):
        x = self.tree_list[0].node.children[0]
        if x != None:
            name = filedialog.asksaveasfilename(
                filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
                initialdir=self.target_dir,
                defaultextension=".cnl",
            )
            if name == "":
                # showinfo(text='Error!')
                return None
            self.refresh(level=3)
            self.save_CNL_File(name)
            self.target_dir = name.rsplit("/", 1)[0]

        else:
            showinfo(lavel="ノードが空です")

    def load_node(self):
        name = filedialog.askopenfilename(
            filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
            initialdir=self.target_dir,
            defaultextension=".cnl",
        )
        if name == None:
            showinfo(text="Error!")
            return None
        pastnode = self.tree_list[0]
        self.tree_list[0].node = pmd.NODE(
            parts=pmd.PARTS(name="ROOT", joint=["root"]), depth=-1, child=[None]
        )
        self.load_CNL_File(name)
        self.target_dir = name.rsplit("/", 1)[0]
        self.refresh()

    def dialog_save_PMD(self):
        name = filedialog.asksaveasfilename(
            filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
            initialdir=self.target_dir,
            defaultextension=".pmd",
        )
        self.refresh()
        self.save_PMD(name)
        self.target_dir = name.rsplit("/", 1)[0]

    def batch_assemble(self):
        names = filedialog.askopenfilename(
            filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
            initialdir=self.target_dir,
            defaultextension=".cnl",
            multiple=True,
        )

        self.save_CNL_File("./last.cnl")
        if type(names) is str:
            names = names.split(" ")
        for name in names:
            self.load_CNL_File(name)
            self.refresh()

            name_PMD = name
            if name_PMD[-4:] == ".cnl":
                name_PMD = name_PMD[:-4] + ".pmd"
            else:
                name_PMD += ".pmd"
            self.save_PMD(name_PMD)
        self.load_CNL_File("./last.cnl")
        self.refresh()
        self.target_dir = name.rsplit("/", 1)[0]

    def setting_dialog(self):
        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        fancs = PMCA_dialogs.SETTING_DIALOG_FANC(self, root)

        frame.export2folder = Checkbutton(
            root,
            text="個別のフォルダを作成してPMDを保存する",
            variable=fancs.flag_export2folder,
            command=fancs.apply_all,
        )

        frame.export2folder.pack()
        Button(root, text="OK", command=close).pack(padx=5, pady=5, side=RIGHT)
        root.mainloop()
