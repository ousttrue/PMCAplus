from typing import NamedTuple, Callable
import pathlib, logging
import tkinter.filedialog
import tkinter.ttk
import glglue.tk_frame
from ..app import App
from ..gl_scene import GlScene
from .. import pmd_type
from .model_tab import ModelTab
from .color_tab import ColorTab
from .transform_tab import TransformTab
from .info_tab import InfoTab


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


class FileFilter(NamedTuple):
    label: str
    ext: str  # ".cnl"


class Tabs(tkinter.ttk.Notebook):
    def __init__(
        self,
        root: tkinter.Tk,
        app: App,
    ):
        super().__init__(root)

        self.app = app

        self.model_tab = ModelTab(root, self.app)
        self._add_tab(self.model_tab)

        self.color_tab = ColorTab(root, self.app)
        self._add_tab(self.color_tab)

        self.transform_tab = TransformTab(root, self.app)
        self._add_tab(self.transform_tab)

        self.info_tab = InfoTab(root)
        self._add_tab(self.info_tab)

    def _add_tab(self, x: tkinter.ttk.Frame) -> None:
        self.insert(tkinter.END, x, text=x.text)  # type: ignore

    def on_refresh(self) -> None:
        self.model_tab.set_tree(self.app.cnl.tree, True)
        if self.color_tab.cur_mat:
            self.color_tab.l_tree.set_entry(self.app.cnl.mat_rep.get_entries(), sel=self.color_tab.sel_t)  # type: ignore
        else:
            self.color_tab.l_tree.set_entry(self.app.cnl.mat_rep.get_entries())
        self.info_tab.refresh()
        # self.transform_tab.info_frame.strvar.set(  # type: ignore
        #     "height     = %f\nwidth      = %f\nthickness = %f\n" % (w, h, t)
        # )


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
        self.target_dir = pathlib.Path("./model/")

        # setup opengl widget
        self.scene = GlScene()
        self.glwidget = glglue.tk_frame.TkGlFrame(
            master,
            self.scene.render,
        )
        self.glwidget.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.notebook = Tabs(master, self.app)
        self.notebook.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=0)

        self.frame_button = Buttons(master)
        self.frame_button.pack(padx=5, pady=5, side=tkinter.TOP, fill="x")

        # menu
        self.menubar = tkinter.Menu(master)
        master.configure(menu=self.menubar)

        # menu: files
        files = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="File", underline=0, menu=files)
        files.add_command(
            label="新規(new cnl)",
            underline=0,
            command=self.app.cnl_reload,
        )
        files.add_command(
            label="読み込み(load cnl)",
            underline=0,
            command=self.make_open_file_dialog(
                self.app.cnl_load, FileFilter("キャラクタノードリスト", ".cnl")
            ),
        )
        files.add_separator()
        files.add_command(
            label="保存(save cnl)",
            underline=0,
            command=self.make_save_file_dialog(
                self.app.cnl_save, FileFilter("キャラクタノードリスト", ".cnl")
            ),
        )

        files.add_command(
            label="モデル保存(save pmd)",
            underline=0,
            command=self.make_save_file_dialog(
                self.app.pmd_save, FileFilter("Plygon Model Deta(for MMD)", ".pmd")
            ),
        )
        files.add_separator()

        # cnl を連続で pmd 化する
        # names = filedialog.askopenfilename(
        #     filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
        #     initialdir=self.target_dir,
        #     defaultextension=".cnl",
        #     multiple=True,
        # )
        # files.add_command(label="一括組立て", underline=0, command=self.batch_assemble)
        # files.add_separator()

        files.add_command(
            label="PMDフォーマットチェック",
            underline=0,
            command=self.app.pmd_format_check,
        )
        files.add_command(
            label="PMD概要確認",
            underline=0,
            command=self.app.pmd_overview_check,
        )
        files.add_command(
            label="PMD詳細確認",
            underline=0,
            command=self.app.pmd_property_check,
        )
        files.add_separator()

        def quit():
            master.winfo_toplevel().destroy()
            master.quit()

        files.add_command(label="exit", underline=0, command=quit)

        # menu: editing
        editing = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Edit", underline=0, menu=editing)
        editing.add_command(
            label="体型調整を初期化", underline=0, command=self.app.init_tf
        )
        editing.add_command(
            label="材質をランダム選択", underline=0, command=self.app.rand_mat
        )

    def update_scene(self, data: bytes):
        # data = b''PMCA.Get_PMD(0)
        assert data
        pmd = pmd_type.parse(data)
        assert pmd
        self.scene.set_model(pmd, pathlib.Path("parts"))
        self.notebook.on_refresh()
        self.glwidget.tkExpose(None)  # type: ignore

    def make_open_file_dialog(
        self, callback: Callable[[pathlib.Path], None], *filters: FileFilter
    ) -> Callable[[], None]:
        def func() -> None:
            name = tkinter.filedialog.askopenfilename(
                filetypes=list(filters) + [FileFilter("all", ".*")],
                initialdir=str(self.target_dir),
                defaultextension=filters[0].ext,
            )
            if name:
                path = pathlib.Path(name)
                self.target_dir = path.parent
                callback(path)

        return func

    def make_save_file_dialog(
        self, callback: Callable[[pathlib.Path], None], *filters: FileFilter
    ) -> Callable[[], None]:
        def func() -> None:
            name = tkinter.filedialog.asksaveasfilename(
                filetypes=list(filters) + [FileFilter("all", ".*")],
                initialdir=str(self.target_dir),
                defaultextension=filters[0].ext,
            )
            if name:
                path = pathlib.Path(name)
                self.target_dir = path.parent
                callback(path)

        return func


def run(name: str, app: App):
    window = MainFrame(name, app)
    app.on_assemble.append(window.update_scene)
    app.assemble()
    window.mainloop()
