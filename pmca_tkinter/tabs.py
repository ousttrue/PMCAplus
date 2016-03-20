# coding: utf-8

from tkinter import *
from pmca_tkinter.utils import LISTBOX

class PartsFrame(Frame):
    def __init__(self, master, tree_click, parts_sel_click):
        super().__init__(master)
        self.frame = Frame(self)
        self.text = "Model"
        self.parts_frame = LabelFrame(self.frame, text = 'Model')
        self.l_tree = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_tree.listbox.bind("<ButtonRelease-1>", tree_click)
        
        self.parts_frame = LabelFrame(self.frame, text = 'Parts')
        self.l_sel = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_sel.listbox.bind("<ButtonRelease-1>", parts_sel_click)
        
        self.frame.pack(padx = 3, pady = 3, side = TOP, fill = BOTH, expand=1)
        
        self.comment = StringVar()
        self.comment.set("comment:")
        self.text_label = Label(self, textvariable=self.comment)
        self.text_label.pack(padx = 3, pady = 3, side = BOTTOM, fill = X)


class MaterialFrame(Frame):
    def __init__(self, master, mats_click, mats_sel_click):
        super().__init__(master)
        self.frame = Frame(self)
        self.text = "Color"
        self.parts_frame = LabelFrame(self.frame, text = 'Material')
        self.l_tree = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_tree.listbox.bind("<ButtonRelease-1>", mats_click)
        
        self.parts_frame = LabelFrame(self.frame, text = 'Select')
        self.l_sel = LISTBOX(self.parts_frame)
        self.parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.l_sel.listbox.bind("<ButtonRelease-1>", mats_sel_click)
        
        self.frame.pack(padx = 3, pady = 3, side = TOP, fill = BOTH, expand=1)
        
        self.comment = StringVar()
        self.comment.set("comment:")
        self.text_label = Label(self, textvariable=self.comment)
        self.text_label.pack(padx = 3, pady = 3, side = BOTTOM, fill = X)


class TransformFrame(Frame):
    def __init__(self, master, tf_click):
        super().__init__(master)
        self.text = "Transform"
        self.tfgroup_frame = LabelFrame(self, text = 'Groups')
        self.tfgroup = LISTBOX(self.tfgroup_frame)
        self.tfgroup_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tfgroup.listbox.bind("<ButtonRelease-1>", tf_click)
        
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
