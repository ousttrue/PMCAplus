﻿# coding: utf-8
from tkinter import *
from tkinter.ttk import Notebook
import pmca_tkinter
import PMCA_GL
import PyPMCA
from logging import getLogger
logger = getLogger(__name__)


class MainFrame(Frame):
    def __init__(self, glcontroller):
        super().__init__(None)
        self.master.title(PyPMCA.APP_NAME)
        self.glframe=pmca_tkinter.GLFrame(self, glcontroller, width=640, height=480)
        self.glframe.pack(side = TOP, fill=BOTH, expand=True)
        notebook=self.create_notebook(self)
        notebook.pack(side = TOP, fill = BOTH, expand=True)
        button=self.create_quitbutton(self)
        button.pack(side = TOP, padx = 5, pady = 5, fill = 'x')
        self.pack(fill=BOTH, expand=True)

    def create_notebook(self, master):
        #Tab      
        notebook = Notebook(master)

        #Tab0
        self.parts_tab=pmca_tkinter.PartsFrame(notebook)
        notebook.insert(END, self.parts_tab, text = self.parts_tab.text)

        #Tab1
        self.material_tab=pmca_tkinter.MaterialFrame(notebook)
        notebook.insert(END, self.material_tab, text = self.material_tab.text)
        
        #Tab2
        self.transform_tab=pmca_tkinter.TransformFrame(notebook)
        notebook.insert(END, self.transform_tab, text = self.transform_tab.text)              

        #Tab3
        self.info_tab=pmca_tkinter.InfoFrame(notebook)
        self.info_tab.frame.name.set('PMCAモデル')
        self.info_tab.frame.name_l.set('PMCAモデル')
        self.info_tab.frame.comment.delete('1.0',END)
        notebook.insert(END, self.info_tab, text = self.info_tab.text)

        return notebook

    def create_quitbutton(self, master):          
        #Buttons        
        frame_button = Frame(master)
        self.QUIT = Button(frame_button)
        self.QUIT["text"] = "QUIT"
        self.QUIT["command"] = pmca_tkinter.QUIT(self.master)
        self.QUIT.pack(side = RIGHT)
        return frame_button

       
    def bind_pmca(self, pmca):
        #Menu
        self.menubar = Menu(self.master)
        self.master.configure(menu = self.menubar)

        files = Menu(self.menubar, tearoff = False)
        self.menubar.add_cascade(label="ファイル", underline = 0, menu=files)
        files.add_command(label = "新規", under = 0, command = pmca.init)

        def load_node_tkinter():
            name = filedialog.askopenfilename(filetypes = [('キャラクタノードリスト','.cnl'),('all','.*')], 
                                              initialdir = pmca.target_dir, 
                                              defaultextension='.cnl'
                                              )
            if name == None:
                #showinfo(text='Error!')
                return

            pmca.load_CNL_File(name)
            pmca.target_dir = name.rsplit('/',1)[0]
            #self.refresh()
        files.add_command(label = "読み込み", under = 0, command = load_node_tkinter)

        files.add_separator

        def save_node_tkinter():
            if pmca.parts_tree.is_empty():
                showinfo(lavel='ノードが空です')
                return

            name = filedialog.asksaveasfilename(filetypes = [('キャラクタノードリスト','.cnl'),('all','.*')], initialdir = pmca.target_dir, defaultextension='.cnl')
            if name == '':
                #showinfo(text='Error!')
                return None

            pmca.refresh(level = 3)
            pmca.save_CNL_File(name)
            pmca.target_dir = name.rsplit('/',1)[0]
        files.add_command(label = "保存", under = 0, command = save_node_tkinter)

        def dialog_save_PMD_tkinter():
            name = filedialog.asksaveasfilename(filetypes = [('Plygon Model Deta(for MMD)','.pmd'),('all','.*')], initialdir = pmca.target_dir, defaultextension='.pmd')
            pmca.refresh()
            pmca.save_PMD(name)
            pmca.target_dir = name.rsplit('/',1)[0]
        files.add_command(label = "モデル保存", under = 0, command = dialog_save_PMD)

        files.add_separator

        def batch_assemble():
            names = filedialog.askopenfilename(filetypes = [('キャラクタノードリスト','.cnl'),('all','.*')], initialdir = self.target_dir, defaultextension='.cnl',  multiple=True)
            if names:
                pmca.batch_assemble(names)
        files.add_command(label = "一括組立て", under = 0, command = pmca.batch_assemble)

        files.add_separator

        def savecheck_PMD():
            errors=pmca.savecheck_PMD()
            root = Toplevel()
            root.transient(self)
            close = QUIT(root)
            frame = Frame(root)
            frame.log = Text(frame)
            for x in errors:
                frame.log.insert(END, x + '\n')
            frame.log['state'] = 'disabled'
            frame.yscroll = Scrollbar(frame, orient = VERTICAL, command = frame.log.yview)
            frame.yscroll.pack(side = RIGHT, fill = Y, expand = 0, anchor=E)
            frame.log["yscrollcommand"] = frame.yscroll.set
            frame.log.pack(side = RIGHT, fill = BOTH, expand=1)
            frame.pack(fill = BOTH, expand=1)
            Button(root, text = 'OK', command = close).pack()
            root.mainloop()
        files.add_command(label = "PMDフォーマットチェック", under = 0, command = savecheck_PMD)

        def check_PMD():
            string=pmca.check_PMD()
            root = Toplevel()
            root.transient(self)
            close = QUIT(root)
            frame = Frame(root)
            frame.log = Text(frame)
            frame.log.insert(END, string)
            frame.log['state'] = 'disabled'
            frame.yscroll = Scrollbar(frame, orient = VERTICAL, command = frame.log.yview)
            frame.yscroll.pack(side = RIGHT, fill = Y, expand = 0, anchor=E)
            frame.log["yscrollcommand"] = frame.yscroll.set
            frame.log.pack(side = RIGHT, fill = BOTH, expand=1)
            frame.pack(fill = BOTH, expand=1)
            Button(root, text = 'OK', command = close).pack()
            root.mainloop()
        files.add_command(label = "PMD概要確認", under = 0, command = check_PMD)

        def procheck_PMD():
            string=pmca.procheck_PMD()
            root = Toplevel()
            root.transient(self)
            close = QUIT(root)
            frame = Frame(root)
            frame.log = Text(frame)
            frame.log.insert(END, string)
            frame.log['state'] = 'disabled'
            frame.yscroll = Scrollbar(frame, orient = VERTICAL, command = frame.log.yview)
            frame.yscroll.pack(side = RIGHT, fill = Y, expand = 0, anchor=E)
            frame.log["yscrollcommand"] = frame.yscroll.set
            frame.log.pack(side = RIGHT, fill = BOTH, expand=1)
            frame.pack(fill = BOTH, expand=1)
            Button(root, text = 'OK', command = close).pack()
            root.mainloop()
        files.add_command(label = "PMD詳細確認", under = 0, command = propcheck_PMD)

        files.add_separator
        files.add_command(label = "exit", under = 0, command = pmca_tkinter.QUIT(self.master))
        
        editing = Menu(self.menubar, tearoff = False)
        self.menubar.add_cascade(label="編集", underline = 0, menu=editing)
        editing.add_command(label = "体型調整を初期化", under = 0, command = pmca.transform.clear)
        editing.add_command(label = "材質をランダム選択", under = 0, command = pmca.materials.random)
        editing.add_command(label = "PMCA設定", under = 0, command = self.setting_dialog)

        #
        # tree
        #
        def on_tree_entry(entry, sel):
            logger.debug('on_tree_entry %s, %d', entry, sel)
            self.parts_tab.l_tree.set_entry(entry, sel=sel)
        pmca.parts_tree.tree_entry_observable.add(on_tree_entry)

        def on_parts_entry(entry, sel):
            logger.debug('on_parts_entry %s, %d', entry, sel)
            self.parts_tab.l_sel.set_entry(entry, sel=sel)
        pmca.parts_tree.parts_entry_observable.add(on_parts_entry)

        def on_tree_select(sel):
            logger.debug('on_tree_select %d', sel)
            pmca.parts_tree.select_node(sel)
        self.parts_tab.tree_select_observable.add(on_tree_select)

        def on_parts_select(sel):
            logger.debug('on_parts_select %d', sel)
            pmca.parts_tree.select_part(sel)
        self.parts_tab.parts_select_observable.add(on_parts_select)            

        #
        # material
        #
        def on_material_entry(entry, sel):
            self.material_tab.l_tree.set_entry(entry, sel=sel)
        pmca.materials.material_entry_observable.add(on_material_entry)

        def on_color_entry(entry, sel):
            self.material_tab.l_sel.set_entry(entry, sel=sel)
        pmca.materials.color_entry_observable.add(on_color_entry)

        def on_material_select(sel):
            pmca.materials.select_material(sel)
        self.material_tab.material_select_observable.add(on_material_select)

        def on_color_select(sel):
            pmca.materials.select_color(sel)
        self.material_tab.color_select_observable.add(on_color_select)

        #
        # tranform
        #
        self.transform_tab.tfgroup.set_entry(pmca.transform.tmp)
        def on_tf_select(sel):
            pmca.transform.select_body(self, sel)
        self.transform_tab.tf_select_observable.add(on_tf_select)

        def on_bb(wht):
            self.transform_tab.info_frame.strvar.set('height     = %f\nwidth      = %f\nthickness = %f\n'%(wht[1],wht[0],wht[2]))
        pmca.model_bb_observable.add(on_bb)

        #
        # info
        #
        self.info_tab.set_materials(pmca.materials)
        self.info_tab.set_modelinfo(pmca.modelinfo)
        def on_model_update():
            str1, str2=pmca.get_license()
            self.info_tab.frame.text.set('Author : %s\nLicense : %s'%(str1, str2))
        pmca.model_update_observable.add(on_model_update)

        #
        # OpenGL
        #
        def update_gl():
            self.glframe.glwidget.event_generate("<Expose>")
        pmca.model_update_observable.add(update_gl)

        #
        # 更新タイマー
        #
        def timer_update():
            pmca.update()
            self.after(33, timer_update)
        timer_update()

    #menu
    def setting_dialog(self):
        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        fancs = PMCA_dialogs.SETTING_DIALOG_FANC(self, root)
        
        frame.export2folder = Checkbutton(root, text = '個別のフォルダを作成してPMDを保存する', 
                                          variable = fancs.flag_export2folder, 
                                          command = fancs.apply_all)
        
        frame.export2folder.pack()
        Button(root, text = 'OK', command = close).pack(padx=5, pady=5, side = RIGHT)
        root.mainloop()
