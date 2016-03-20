# coding: utf-8
from tkinter import *
from tkinter.ttk import Notebook
import pmca_tkinter
import PMCA

APP_NAME = 'PMCA v0.0.6r10'


class MainFrame(Frame):
    def __init__(self, pmca, master=None):
        super().__init__(master)
        self.master.title(APP_NAME)
        self.pack()

        self.pmca=pmca

        #Tab      
        notebook = Notebook(self.master)
        notebook.pack(side = TOP, fill = BOTH, expand=1)

        #Tab0
        self.parts_tab=pmca_tkinter.PartsFrame(self.master, self.tree_click, self.parts_sel_click)
        notebook.insert(END, self.parts_tab, text = self.parts_tab.text)

        #Tab1
        self.material_tab=pmca_tkinter.MaterialFrame(self.master, self.mats_click, self.mats_sel_click)
        notebook.insert(END, self.material_tab, text = self.material_tab.text)
        
        #Tab2
        self.transform_tab=pmca_tkinter.TransformFrame(self.master, self.tf_click)
        notebook.insert(END, self.transform_tab, text = self.transform_tab.text)              

        #Tab3
        self.info_tab=pmca_tkinter.InfoFrame(self.master)
        self.info_tab.frame.name.set('PMCAモデル')
        self.info_tab.frame.name_l.set('PMCAモデル')
        self.info_tab.frame.comment.delete('1.0',END)
        notebook.insert(END, self.info_tab, text = self.info_tab.text)
           
        #Buttons        
        self.frame_button = Frame(self.master)
        self.QUIT = Button(self.frame_button)
        self.QUIT["text"] = "QUIT"
        self.QUIT["command"] = pmca_tkinter.QUIT(self.master)
        self.QUIT.pack(side = RIGHT)
        self.frame_button.pack(padx = 5, pady = 5, side = TOP, fill = 'x')
        
        #Menu
        self.menubar = Menu(self.master)
        self.master.configure(menu = self.menubar)

        files = Menu(self.menubar, tearoff = False)
        self.menubar.add_cascade(label="ファイル", underline = 0, menu=files)
        files.add_command(label = "新規", under = 0, command = pmca.init)
        files.add_command(label = "読み込み", under = 0, command = pmca.load_node)
        files.add_separator
        files.add_command(label = "保存", under = 0, command = pmca.save_node)
        files.add_command(label = "モデル保存", under = 0, command = pmca.dialog_save_PMD)
        files.add_separator
        files.add_command(label = "一括組立て", under = 0, command = pmca.batch_assemble)
        files.add_separator
        files.add_command(label = "PMDフォーマットチェック", under = 0, command = pmca.savecheck_PMD)
        files.add_command(label = "PMD概要確認", under = 0, command = pmca.check_PMD)
        files.add_command(label = "PMD詳細確認", under = 0, command = pmca.propcheck_PMD)
        files.add_separator
        files.add_command(label = "exit", under = 0, command = pmca_tkinter.QUIT(master))
        
        editing = Menu(self.menubar, tearoff = False)
        self.menubar.add_cascade(label="編集", underline = 0, menu=editing)
        editing.add_command(label = "体型調整を初期化", under = 0, command = self.pmca.transform.clear)
        editing.add_command(label = "材質をランダム選択", under = 0, command = pmca.materials.random)
        editing.add_command(label = "PMCA設定", under = 0, command = self.setting_dialog)

        # tree
        def on_tree_entry(entry, sel):
            self.parts_tab.l_tree.set_entry(entry, sel=sel)
        pmca.parts_tree.tree_entry_observable.add(on_tree_entry)

        def on_parts_entry(entry, sel):
            self.parts_tab.l_sel.set_entry(entry, sel=sel)
        pmca.parts_tree.parts_entry_observable.add(on_parts_entry)

        # material
        def on_material_entry(entry, sel):
            self.material_tab.l_tree.set_entry(entry, sel=sel)
        pmca.materials.material_entry_observable.add(on_material_entry)

        def on_color_entry(entry, sel):
            self.material_tab.l_sel.set_entry(entry, sel=sel)
        pmca.materials.color_entry_observable.add(on_color_entry)

        # tranform
        self.transform_tab.tfgroup.set_entry(pmca.transform.tmp)

        # info
        self.info_tab.set_materials(pmca.materials)
        self.info_tab.set_modelinfo(pmca.modelinfo)

        def on_model_update():
            wht = PMCA.getWHT(0)
            self.transform_tab.info_frame.strvar.set('height     = %f\nwidth      = %f\nthickness = %f\n'%(wht[1],wht[0],wht[2]))

            str1, str2=self.pmca.get_license()
            self.info_tab.frame.text.set('Author : %s\nLicense : %s'%(str1, str2))
        pmca.model_update_observable.add(on_model_update)

        pmca.update()
        '''
        if level < 1:
            pass
        else:
            PMCA.Copy_PMD(1,0)

        if level < 2:
            pass
        else:
            PMCA.Copy_PMD(2,0)
        
        if level < 3:
            self.pmca.transform.update()
        else:
            PMCA.Copy_PMD(3,0)
        
        if level < 4:
            self.pmca.name_update()       
        '''

    #functions tab0
    def tree_click(self,event):
        self.parts_tab.comment.set("comment:")
        sel_t = int(self.parts_tab.l_tree.listbox.curselection()[0])
        self.pmca.parts_tree.select_node(sel_t)
    
    def parts_sel_click(self,event):
        sel = int(self.parts_tab.l_sel.listbox.curselection()[0])
        sel_t = int(self.parts_tab.l_tree.listbox.curselection()[0])
        node=self.pmca.parts_tree.select_part(sel_t, sel)
        if node == None:
            self.parts_tab.comment.set("comment:")
        else:
            self.parts_tab.comment.set("comment:%s"%(node.parts.comment))
    
    #functions tab1
    def mats_click(self,event):
        sel_t = int(self.material_tab.l_tree.listbox.curselection()[0])
        comment=self.pmca.materials.select_material(sel_t)
        self.material_tab.comment.set("comment:%s"%(comment))
    
    def mats_sel_click(self,event):
        sel_t = int(self.material_tab.l_sel.listbox.curselection()[0])
        self.pmca.materials.select_color(sel_t)

    #functions tab2
    def tf_click(self,event):
        sel = int(self.transform_tab.tfgroup.listbox.curselection()[0])
        self.pmca.transform.select_body(self, sel)
    
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
