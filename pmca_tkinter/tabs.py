# coding: utf-8

from tkinter import *
from pmca_tkinter.utils import LISTBOX


class Observable:
    def __init__(self):
        self.observers = set()

    def add(self, callback):
        self.observers.add(callback)
        return lambda : self.observers.remove(callback)

    def notify(self, *args):
        for callback in self.observers:
            callback(*args)


def list_on_click(listbox: Listbox, observable: Observable):
    try:
        selection=listbox.curselection()
        if selection:
            sel_t = int(selection[0])
            observable.notify(sel_t)
    except:
        pass           


class PartsFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.tree_select_observable=Observable()
        self.parts_select_observable=Observable()

        self.frame = Frame(self)
        self.text = "Model"

        self.parts_frame = LabelFrame(self.frame, text = 'Model')
        self.l_tree = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_tree.listbox.bind("<ButtonRelease-1>", 
                                 lambda event: list_on_click(self.l_tree.listbox, self.tree_select_observable))       

        self.parts_frame = LabelFrame(self.frame, text = 'Parts')
        self.l_sel = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_sel.listbox.bind("<ButtonRelease-1>", 
                                lambda event: list_on_click(self.l_sel.listbox, self.parts_select_observable))
        
        self.frame.pack(padx = 3, pady = 3, side = TOP, fill = BOTH, expand=1)
        
        self.comment = StringVar()
        self.comment.set("comment:")
        self.text_label = Label(self, textvariable=self.comment)
        self.text_label.pack(padx = 3, pady = 3, side = BOTTOM, fill = X)


class MaterialFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.material_select_observable=Observable()
        self.color_select_observable=Observable()

        self.frame = Frame(self)
        self.text = "Color"

        self.parts_frame = LabelFrame(self.frame, text = 'Material')
        self.l_tree = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_tree.listbox.bind("<ButtonRelease-1>", 
                                 lambda event: list_on_click(self.l_tree.listbox, self.material_select_observable))
        
        self.parts_frame = LabelFrame(self.frame, text = 'Select')
        self.l_sel = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_sel.listbox.bind("<ButtonRelease-1>", 
                                lambda event: list_on_click(self.l_sel.listbox, self.color_select_observable))
        
        self.frame.pack(padx = 3, pady = 3, side = TOP, fill = BOTH, expand=1)
        
        self.comment = StringVar()
        self.comment.set("comment:")
        self.text_label = Label(self, textvariable=self.comment)
        self.text_label.pack(padx = 3, pady = 3, side = BOTTOM, fill = X)


class TransformFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.tf_select_observable=Observable()

        self.text = "Transform"
        self.tfgroup_frame = LabelFrame(self, text = 'Groups')
        self.tfgroup = LISTBOX(self.tfgroup_frame)
        self.tfgroup_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tfgroup.listbox.bind("<ButtonRelease-1>", 
                                  lambda event: list_on_click(self.tfgroup.listbox, self.tf_select_observable))
        
        self.info_frame = LabelFrame(self, text = 'Info')
        self.info_frame.strvar = StringVar()
        self.info_frame.strvar.set('x=\ny=\nz=\n')
        self.info_frame.label = Label(self.info_frame, textvariable=self.info_frame.strvar).pack(side = LEFT, anchor = N)
        self.info_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)


class InfoFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.text = "Info"
        self.frame = Frame(self)
        self.frame.comment = Text(self.frame, height=10)
        self.frame.comment['state'] = 'normal'
        self.frame.yscroll = Scrollbar(self.frame, orient = VERTICAL, command = self.frame.comment.yview)
        self.frame.yscroll.pack(side = RIGHT, fill = Y, expand = 0, anchor=E)
        self.frame.comment["yscrollcommand"] = self.frame.yscroll.set
        self.frame.comment.pack(side = RIGHT, fill = BOTH, expand=1)
        
        self.frame.name = StringVar()
        self.frame.name_entry = Entry(self, textvariable = self.frame.name)
        self.frame.name_entry.pack(fill = X)
        
        self.frame.name_l = StringVar()
        self.frame.name_l_entry = Entry(self, textvariable = self.frame.name_l)
        self.frame.name_l_entry.pack(fill = X)
               
        self.frame.text = StringVar()
        self.frame.text_label = Label(self, textvariable=self.frame.text)
        self.frame.text_label.pack(fill = X)
        
        self.frame.pack(fill = BOTH, expand=1)

    def set_materials(self, materials):
        str1, str2=materials.license.get_entry()
        self.frame.text.set('Author : %s\nLicense : %s'%(str1, str2))

    def set_modelinfo(self, modelinfo):
        self.frame.name.set(modelinfo.name)
        self.frame.name_l.set(modelinfo.name)
