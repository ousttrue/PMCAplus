#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.argv = [''] 
import os
#import cms
import shutil

import time
import random

#インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())
sys.path.append('%s/converter'%(os.getcwd()))
sysenc = sys.getfilesystemencoding()

import PMCA
import PyPMCA
import PMCA_dialogs

import converter

from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *

softwarename = 'PMCA v0.0.6r10'

commands={}

class QUIT:
    def __init__(self, root):
        self.root = root
    
    def __call__(self):
        self.root.winfo_toplevel().destroy()
        self.root.quit()


class MainFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title(softwarename)
        self.pack()

        self.materials=PyPMCA.MaterialSelector()
        self.transform=PyPMCA.BodyTransform()
        self.modelinfo = PyPMCA.MODELINFO()
        self.target_dir = './model/'
        self.settings = SETTINGS()
        self.parts_tree=PyPMCA.PartsTree()

        #タブを作成
        notebook = Notebook(self.master)
        notebook.pack(side = TOP, fill = BOTH, expand=1)
        
        self.tab = []
        ########################################################################################################
        #Tab0
        self.tab.append(Frame(self.master))
        
        self.tab[0].frame = Frame(self.tab[0])
        self.tab[0].text = "Model"
        self.tab[0].parts_frame = LabelFrame(self.tab[0].frame, text = 'Model')
        self.tab[0].l_tree = LISTBOX(self.tab[0].parts_frame)
        self.tab[0].parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tab[0].l_tree.listbox.bind("<ButtonRelease-1>",self.tree_click)
        
        self.tab[0].parts_frame = LabelFrame(self.tab[0].frame, text = 'Parts')
        self.tab[0].l_sel = LISTBOX(self.tab[0].parts_frame)
        self.tab[0].parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tab[0].l_sel.listbox.bind("<ButtonRelease-1>",self.parts_sel_click)
        
        self.tab[0].frame.pack(padx = 3, pady = 3, side = TOP, fill = BOTH, expand=1)
        
        self.tab[0].comment = StringVar()
        self.tab[0].comment.set("comment:")
        self.tab[0].text_label = Label(self.tab[0], textvariable=self.tab[0].comment)
        self.tab[0].text_label.pack(padx = 3, pady = 3, side = BOTTOM, fill = X)
        
        
        ########################################################################################################
        #Tab1
        
        self.tab.append(Frame(self.master))
        self.tab[1].frame = Frame(self.tab[1])
        self.tab[1].text = "Color"
        self.tab[1].parts_frame = LabelFrame(self.tab[1].frame, text = 'Material')
        self.tab[1].l_tree = LISTBOX(self.tab[1].parts_frame)
        self.tab[1].parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tab[1].l_tree.listbox.bind("<ButtonRelease-1>",self.mats_click)
        
        self.tab[1].parts_frame = LabelFrame(self.tab[1].frame, text = 'Select')
        self.tab[1].l_sel = LISTBOX(self.tab[1].parts_frame)
        self.tab[1].parts_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tab[1].l_sel.listbox.bind("<ButtonRelease-1>",self.mats_sel_click)
        
        self.tab[1].frame.pack(padx = 3, pady = 3, side = TOP, fill = BOTH, expand=1)
        
        self.tab[1].comment = StringVar()
        self.tab[1].comment.set("comment:")
        self.tab[1].text_label = Label(self.tab[1], textvariable=self.tab[1].comment)
        self.tab[1].text_label.pack(padx = 3, pady = 3, side = BOTTOM, fill = X)
        
        
        
        ########################################################################################################
        #Tab2
        self.tab.append(Frame(self.master))
        self.tab[2].text = "Transform"
        self.tab[2].tfgroup_frame = LabelFrame(self.tab[2], text = 'Groups')
        self.tab[2].tfgroup = LISTBOX(self.tab[2].tfgroup_frame)
        self.tab[2].tfgroup_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        self.tab[2].tfgroup.listbox.bind("<ButtonRelease-1>",self.tf_click)
        
        self.tab[2].info_frame = LabelFrame(self.tab[2], text = 'Info')
        self.tab[2].info_frame.strvar = StringVar()
        self.tab[2].info_frame.strvar.set('x=\ny=\nz=\n')
        self.tab[2].info_frame.label = Label(self.tab[2].info_frame, textvariable=self.tab[2].info_frame.strvar).pack(side = LEFT, anchor = N)
        self.tab[2].info_frame.pack(padx = 3, pady = 3, side = LEFT, fill = BOTH, expand=1)
        
        
        ########################################################################################################
        #Tab3
        self.tab.append(Frame(self.master))
        self.tab[3].text = "Info"
        self.tab[3].frame = Frame(self.tab[3])
        self.tab[3].frame.comment = Text(self.tab[3].frame, height=10)
        self.tab[3].frame.comment['state'] = 'normal'
        self.tab[3].frame.yscroll = Scrollbar(self.tab[3].frame, orient = VERTICAL, command = self.tab[3].frame.comment.yview)
        self.tab[3].frame.yscroll.pack(side = RIGHT, fill = Y, expand = 0, anchor=E)
        self.tab[3].frame.comment["yscrollcommand"] = self.tab[3].frame.yscroll.set
        self.tab[3].frame.comment.pack(side = RIGHT, fill = BOTH, expand=1)
        
        self.tab[3].frame.name = StringVar()
        self.tab[3].frame.name.set(self.modelinfo.name)
        self.tab[3].frame.name_entry = Entry(self.tab[3], textvariable = self.tab[3].frame.name)
        self.tab[3].frame.name_entry.pack(fill = X)
        
        self.tab[3].frame.name_l = StringVar()
        self.tab[3].frame.name_l.set(self.modelinfo.name)
        self.tab[3].frame.name_l_entry = Entry(self.tab[3], textvariable = self.tab[3].frame.name_l)
        self.tab[3].frame.name_l_entry.pack(fill = X)
               
        self.tab[3].frame.text = StringVar()
        str1, str2=self.materials.license.get_entry()
        self.tab[3].frame.text.set('Author : %s\nLicense : %s'%(str1, str2))
        self.tab[3].frame.text_label = Label(self.tab[3], textvariable=self.tab[3].frame.text)
        self.tab[3].frame.text_label.pack(fill = X)
        
        self.tab[3].frame.pack(fill = BOTH, expand=1)
        for x in self.tab:
            notebook.insert(END, x, text = x.text)
        ########################################################################################################
        #Buttons
        
        self.frame_button = Frame(self.master)
        self.QUIT = Button(self.frame_button)
        self.QUIT["text"] = "QUIT"
        self.QUIT["command"] = QUIT(self.master)
        self.QUIT.pack(side = RIGHT)
        self.frame_button.pack(padx = 5, pady = 5, side = TOP, fill = 'x')
        
    ###########################################################################################
    #functions tab0
    def tree_click(self,event):
        self.tab[0].comment.set("comment:")
        sel_t = int(self.tab[0].l_tree.listbox.curselection()[0])+1
        entry, sel=self.parts_tree.select_node(sel_t)
        self.tab[0].l_sel.set_entry(entry, sel=sel)
    
    def parts_sel_click(self,event):
        sel = int(self.tab[0].l_sel.listbox.curselection()[0])
        sel_t = int(self.tab[0].l_tree.listbox.curselection()[0])+1
        node=self.parts_tree.select_part(sel_t, sel)
        if node == None:
            self.tab[0].comment.set("comment:")
        else:
            self.tab[0].comment.set("comment:%s"%(node.parts.comment))
        self.refresh()
    
    ########################################################################################
    #functions tab1
    def mats_click(self,event):
        sel_t = int(self.tab[1].l_tree.listbox.curselection()[0])
        tmp_list=self.materials.select_material(sel_t)
        self.tab[1].l_sel.set_entry(tmp_list)
        self.tab[0].l_sel.set_entry(self.parts_tree.parts_entry_k, sel=self.parts_tree.tree_list[sel_t].node.list_num)       
        self.tab[1].comment.set("comment:%s"%(self.materials.mat_rep.mat[self.materials.mat_entry[1][sel_t]].mat.comment))
    
    def mats_sel_click(self,event):
        sel_t = int(self.tab[1].l_sel.listbox.curselection()[0])
        self.materials.select_color(sel_t)
        self.refresh(level=1)
    ########################################################################################
    #functions tab2
    def tf_click(self,event):
        sel = int(self.tab[2].tfgroup.listbox.curselection()[0])
        self.transform.select_body(self, sel)
    
    ######################################################################################
    def refresh(self, level=0):
        sel_t = int(self.tab[0].l_tree.listbox.curselection()[0])
        entry=self.parts_tree.refresh()
        self.tab[0].l_tree.set_entry(entry, sel = sel_t)
        
        #モデル組み立て
        PMCA.MODEL_LOCK(1)
        
        if level < 1:
            self.parts_tree.build()
        else:
            PMCA.Copy_PMD(1,0)
        
        if level < 2:
            #材質関連
            entry, sel=self.materials.replace()
            #print("2")
            self.tab[1].l_tree.set_entry(entry, sel = sel)

        else:
            PMCA.Copy_PMD(2,0)
        
        if level < 3:
            self.transform.update()
        else:
            PMCA.Copy_PMD(3,0)
        
        if level < 4:
            str1, str2=self.materials.license.get_entry()
            self.modelinfo.name = self.tab[3].frame.name.get()
            self.modelinfo.name_l = self.tab[3].frame.name_l.get()
            self.modelinfo.comment = self.tab[3].frame.comment.get('1.0',END)
            PyPMCA.Set_Name_Comment(name=self.modelinfo.name,
                comment='%s\nAuthor:%s\nLicense:%s\n%s'%(self.modelinfo.name_l,str1,str2,self.modelinfo.comment), 
                name_eng=self.modelinfo.name_eng,
                comment_eng='%s\nAuthor:%s\nLicense:%s\n%s'%(self.modelinfo.name_l_eng,str1,str2,self.modelinfo.comment_eng))
        
        if level < 3:
            PMCA.PMD_view_set(0, 'replace')    #テクスチャを変更しない
        else:
            PMCA.PMD_view_set(0, 'replace')
        
        PMCA.MODEL_LOCK(0)
        
        wht = PMCA.getWHT(0)
        self.tab[2].info_frame.strvar.set('height     = %f\nwidth      = %f\nthickness = %f\n'%(wht[1],wht[0],wht[2]))
        self.tab[3].frame.text.set('Author : %s\nLicense : %s'%(str1, str2))
        
        print("Done")
    ########################################################################################
    #functions menu
    def clear(self):
        init(self)
        self.refresh()
    
    def savecheck_PMD(self):
        self.refresh(level=3)
        model = PyPMCA.Get_PMD(0)
        
        errors=[]
        
        if len(model.info.name) > 20:
            errors.append('モデル名の長さが20byteを超えています:' + str(len(model.info.name)) + 'byte')
        if len(model.info.comment) > 256:
            errors.append('モデルコメントの長さが256byteを超えています:' + str(len(model.info.comment)) + 'byte')
        if len(model.info.name_eng) > 20:
            errors.append('英語モデル名の長さが20byteを超えています:' + str(len(model.info.name)) + 'byte')
        if len(model.info.comment_eng) > 256:
            errors.append('英語モデルコメントの長さが256byteを超えています:' + str(len(model.info.comment)) + 'byte')
        for x in model.mat:
            if (len(x.tex)+len(x.sph)) > 20:
                errors.append('材質"' + x.name + '"のテクスチャ+スフィアマップの長さが20byteを超えています:' + str(len(x.tex)+len(x.sph)) + 'byte')
        
        for x in model.bone:
            if len(x.name) > 20:
                errors.append('ボーン"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
            if len(x.name_eng) > 20:
                errors.append('ボーン"' + x.name + '"の英語名の長さが20byteを超えています:' + str(len(x.name_eng)) + 'byte')
            i = x.parent
            count = 0
            bone_count = len(model.bone)
            while count < bone_count:
                if i >= bone_count:
                    break
                print(i)
                i=model.bone[i].parent
                count += 1
            else:
                errors.append('循環依存：%s'%(x.name))
        
        for x in model.skin:
            if len(x.name) > 20:
                errors.append('表情"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
            if len(x.name_eng) > 20:
                errors.append('表情"' + x.name + '"の英語名の長さが20byteを超えています:' + str(len(x.name_eng)) + 'byte')
        
        for x in model.bone_grp:
            if len(x.name) > 50:
                errors.append('ボーングループ"' + x.name + '"の名前の長さが50byteを超えています:' + str(len(x.name)) + 'byte')
            if len(x.name_eng) > 50:
                errors.append('ボーングループ"' + x.name + '"の英語名の長さが50byteを超えています:' + str(len(x.name_eng)) + 'byte')
        
        for x in model.rb:
            if len(x.name) > 20:
                errors.append('剛体"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
        
        for x in model.joint:
            if len(x.name) > 20:
                errors.append('ジョイント"' + x.name + '"の名前の長さが20byteを超えています:' + str(len(x.name)) + 'byte')
        
        for i,x in enumerate(model.face):
            for y in x:
                if y >= len(model.vt):
                    errors.append('面%dの頂点インデックスが不正です:%s'%(i, str(x)))
        
        for i,x in enumerate(model.vt):
            for y in x.bone_num:
                if y >= len(model.bone):
                    errors.append('頂点%dのボーンインデックスが不正です:%s'%(i, str(x)))
        
        if len(errors) == 0:
            errors.append('PMDとして正常に保存できます')
        
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
    
    def check_PMD(self):
        self.refresh(level=3)
        info_data = PMCA.getInfo(0)
        info = PyPMCA.INFO(info_data)
        string = 'name :' + info.name
        string += '\ncomment :\n' + info.comment
        string += '\n頂点数 :' + str(info_data['vt_count'])
        string += '\n面数　 :' + str(info_data['face_count'])
        string += '\n材質数 :' + str(info_data['mat_count'])
        string += '\nボーン数 :' + str(info_data['bone_count'])
        string += '\nIK数   :' + str(info_data['IK_count'])
        string += '\n表情数 :' + str(info_data['skin_count'])
        string += '\nボーングループ数 :' + str(info_data['bone_group_count'])
        string += '\nボーン表示数 :' + str(info_data['bone_disp_count'])
        
        string += '\n\n英語対応 :' + str(info_data['eng_support'])
        string += '\n剛体数 :' + str(info_data['rb_count'])
        string += '\nジョイント数 :' + str(info_data['joint_count'])
        
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
    
    def propcheck_PMD(self):
        self.refresh(level=3)
        model = PyPMCA.Get_PMD(0)
        string = 'name :' + model.info.name
        string += '\ncomment :\n' + model.info.comment
        string += '\n\nname_en :' + model.info.name_eng
        string += '\ncomment_en :\n' + model.info.comment_eng
        string += '\n\n頂点数 :' + str(model.info.data['vt_count']) + '\n'
        for i,x in enumerate(model.vt):
            string += str(i) + '\n'
            string += 'loc:' + str(x.loc) + '\n'
            string += 'nor:' + str(x.nor) + '\n'
            string += 'uv:' + str(x.uv) + '\n'
            string += 'bone:' + str(x.bone_num) + '\n'
            string += 'weight:' + str(x.weight) + '\n'
            string += 'edge:' + str(x.edge) + '\n\n'
            
        string += '\n面数　 :' + str(model.info.data['face_count']) + '\n'
        for i,x in enumerate(model.face):
            string += str(x) + '\n'
        string += '\n材質数 :' + str(model.info.data['mat_count']) + '\n'
        for i,x in enumerate(model.mat):
            string += str(i) + '\n'
            string += 'diff_col:' + str(x.diff_col) + '\n'
            string += 'mirr_col:' + str(x.mirr_col) + '\n'
            string += 'spec_col:' + str(x.spec_col) + '\n'
            string += 'spec:' + str(x.spec) + '\n'
            string += 'alpha:' + str(x.alpha) + '\n'
            string += 'toon:' + str(x.toon) + '\n'
            string += 'edge:' + str(x.edge) + '\n'
            string += 'tex:' + x.tex + '\n'
            string += 'sph:' + x.sph + '\n'
            string += 'face_count:' + str(x.face_count) + '\n\n'
        
        string += '\nボーン数 :' + str(model.info.data['bone_count']) + '\n'
        for i,x in enumerate(model.bone):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n'
            string += 'name_en:' + x.name_eng + '\n'
            string += 'parent:' + str(x.parent) + '\n'
            string += 'tail:' + str(x.tail) + '\n'
            string += 'type:' + str(x.type) + '\n'
            string += 'IK:' + str(x.IK) + '\n'
            string += 'loc:' + str(x.loc) + '\n\n'
        
        string += '\nIK数   :' + str(model.info.data['IK_count']) + '\n'
        for i,x in enumerate(model.IK_list):
            string += str(i) + '\n'
            string += 'index:' + str(x.index) + '\n'
            string += 'tail_index:' + str(x.tail_index) + '\n'
            string += 'chain_len:' + str(x.chain_len) + '\n'
            string += 'iterations:' + str(x.iterations) + '\n'
            string += 'weight:' + str(x.weight) + '\n'
            string += 'child:' + str(x.child) + '\n\n'
            
        string += '\n表情数 :' + str(model.info.data['skin_count']) + '\n'
        for i,x in enumerate(model.skin):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n'
            string += 'name_en:' + x.name_eng + '\n'
            string += 'count:' + str(x.count) + '\n'
            string += 'type:' + str(x.type) + '\n\n'
            #string += 'data:' + x.data + '\n'
        
        string += '\nボーングループ数 :' + str(model.info.data['bone_group_count']) + '\n'
        for i,x in enumerate(model.bone_grp):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n'
            string += 'name_en:' + x.name_eng + '\n\n'
        
        string += '\nボーン表示数 :' + str(model.info.data['bone_disp_count']) + '\n'
        for i,x in enumerate(model.bone_dsp):
            string += str(i) + '\n'
            string += 'index:' + str(x.index) + '\n'
            string += 'group:' + str(x.group) + '\n\n'
        
        for i,x in enumerate(model.toon.name):
            string += '%d %s\n'%(i,x)
        
        
        string += '\n\n英語対応 :' + str(model.info.data['eng_support'])
        string += '\n\n剛体数 :' + str(model.info.data['rb_count']) + '\n'
        for i,x in enumerate(model.rb):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n\n'
        
        string += '\nジョイント数 :' + str(model.info.data['joint_count']) + '\n'
        for i,x in enumerate(model.joint):
            string += str(i) + '\n'
            string += 'name:' + x.name + '\n\n'
        
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
    
    def init_tf(self):
        self.transform.clear()
        self.refresh()
    
    def rand_mat(self):
        self.materials.random()
        self.refresh()
    
    def save_node(self):
        x = self.tree_list[0].node.child[0]
        if x != None:
            name = filedialog.asksaveasfilename(filetypes = [('キャラクタノードリスト','.cnl'),('all','.*')], initialdir = self.target_dir, defaultextension='.cnl')
            if name == '':
                #showinfo(text='Error!')
                return None
            self.refresh(level = 3)
            self.save_CNL_File(name)
            self.target_dir = name.rsplit('/',1)[0]

        else:
            showinfo(lavel='ノードが空です')
    
    def load_node(self):
        name = filedialog.askopenfilename(filetypes = [('キャラクタノードリスト','.cnl'),('all','.*')], initialdir = self.target_dir, defaultextension='.cnl')
        if name == None:
            showinfo(text='Error!')
            return None
        pastnode = self.tree_list[0]
        self.tree_list[0].node=PyPMCA.NODE(parts = PyPMCA.PARTS(name = 'ROOT',joint=['root']), depth = -1, child=[None])
        self.load_CNL_File(name)
        self.target_dir = name.rsplit('/',1)[0]
        self.refresh()
    
    def save_PMD(self, name):
        if self.settings.export2folder:
            dirc = name[0:-4]
            os.mkdir(dirc)
            tmp = name.rsplit('/', 1)
            name = "%s/%s/%s"%(tmp[0] ,dirc.rsplit('/', 1)[1] ,tmp[1])
            
        if PMCA.Write_PMD(0, name.encode(sysenc,'replace')) == 0:    
            #テクスチャコピー
            dirc = name.rsplit('/', 1)[0]
            dirc += '/'
            info_data = PMCA.getInfo(0)
            info = PyPMCA.INFO(info_data)
            for i in range(info.data["mat_count"]):
                mat = PyPMCA.MATERIAL(**PMCA.getMat(0, i))
                if mat.tex != '':
                    try:
                        shutil.copy(mat.tex_path, dirc)
                    except IOError:
                        print('コピー失敗:%s'%(mat.tex_path))
                if mat.sph != '':
                    try:
                        shutil.copy(mat.sph_path, dirc)
                    except IOError:
                        print('コピー失敗:%s'%(mat.sph_path))
    
            toon = PMCA.getToon(0)
            for i,x in enumerate(PMCA.getToonPath(0)):
                toon[i] = toon[i].decode('cp932','replace')
                print(toon[i], x)
                if toon[i] != '':
                    try:
                        shutil.copy('toon/' + toon[i], dirc)
                    except IOError:
                        try:
                            shutil.copy('parts/' + toon[i], dirc)
                        except IOError:
                            print('コピー失敗:%s'%(toon[i]))
    
    def dialog_save_PMD(self):
        name = filedialog.asksaveasfilename(filetypes = [('Plygon Model Deta(for MMD)','.pmd'),('all','.*')], initialdir = self.target_dir, defaultextension='.pmd')
        self.refresh()
        self.save_PMD(name)
        self.target_dir = name.rsplit('/',1)[0]
        
    def batch_assemble(self):
        names = filedialog.askopenfilename(filetypes = [('キャラクタノードリスト','.cnl'),('all','.*')], initialdir = self.target_dir, defaultextension='.cnl',  multiple=True)
        
        self.save_CNL_File('./last.cnl')
        print(type(names))
        if type(names) is str:
            names = names.split(' ')
        for name in names:
            self.load_CNL_File(name)
            self.refresh()
            
            name_PMD = name
            if name_PMD[-4:] == '.cnl':
                name_PMD = name_PMD[:-4] + '.pmd'
            else:
                name_PMD += '.pmd'
            self.save_PMD(name_PMD)
        self.load_CNL_File('./last.cnl')
        self.refresh()
        self.target_dir = name.rsplit('/',1)[0]
    
    def load_CNL_File(self, name):
        f = open(name, 'r', encoding = 'utf-8-sig')
        lines = f.read()
        f.close
        lines = lines.split('\n')
        
        self.tab[3].frame.name.set(lines[0])
        self.tab[3].frame.name_l.set(lines[1])
        for line in lines[2:]:
            if line == 'PARTS':
                break
            elif line == '':
                pass
            else:
                self.tab[3].frame.comment.insert(END, line)
                self.tab[3].frame.comment.insert(END, '\n')
        
        else:
            self.tab[3].frame.comment.delete('1.0',END)
    
        self.parts_tree.load_CNL_lines(lines)
        self.materials.load_CNL_lines(lines)
        self.transform.load_CNL_lines(lines)
        return True
        
    def save_CNL_File(self, name):
        if self.parts_tree.tree_list[0].node.child[0] == None:
            return False
        
        lines = []
        lines.append(self.modelinfo.name)
        lines.append(self.modelinfo.name_l)
        lines.append(self.modelinfo.comment)
    
        lines.append('PARTS')
        lines.extend(self.parts_tree.tree_list[0].node.child[0].node_to_text())
        lines.append('MATERIAL')
        lines.extend(self.materials.mat_rep.list_to_text())
        lines.append('TRANSFORM')
        lines.extend(self.transform.transform_data[0].list_to_text())
        
        fp = open(name, 'w', encoding = 'utf-8')
        for x in lines:
            fp.write(x+'\n')
        fp.close
        
        return True
    
    def setting_dialog(self):
        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        fancs = PMCA_dialogs.SETTING_DIALOG_FANC(self, root)
        
        frame.export2folder = Checkbutton(root, text = '個別のフォルダを作成してPMDを保存する', variable = fancs.flag_export2folder, command = fancs.apply_all)
        
        frame.export2folder.pack()
        Button(root, text = 'OK', command = close).pack(padx=5, pady=5, side = RIGHT)
        root.mainloop()

class SETTINGS:
    def __init__(self):
        self.export2folder = False
        
        
class MENUBAR:
    def __init__(self, master=None, app=None):
        self.menubar = Menu(master)
        master.configure(menu = self.menubar)
        files = Menu(self.menubar, tearoff = False)
        editing = Menu(self.menubar, tearoff = False)
        self.menubar.add_cascade(label="ファイル", underline = 0, menu=files)
        self.menubar.add_cascade(label="編集", underline = 0, menu=editing)
        files.add_command(label = "新規", under = 0, command = app.clear)
        files.add_command(label = "読み込み", under = 0, command = app.load_node)
        files.add_separator
        files.add_command(label = "保存", under = 0, command = app.save_node)
        files.add_command(label = "モデル保存", under = 0, command = app.dialog_save_PMD)
        files.add_separator
        files.add_command(label = "一括組立て", under = 0, command = app.batch_assemble)
        files.add_separator
        files.add_command(label = "PMDフォーマットチェック", under = 0, command = app.savecheck_PMD)
        files.add_command(label = "PMD概要確認", under = 0, command = app.check_PMD)
        files.add_command(label = "PMD詳細確認", under = 0, command = app.propcheck_PMD)
        files.add_separator
        files.add_command(label = "exit", under = 0, command = QUIT(master))
        
        editing.add_command(label = "体型調整を初期化", under = 0, command = app.init_tf)
        editing.add_command(label = "材質をランダム選択", under = 0, command = app.rand_mat)
        editing.add_command(label = "PMCA設定", under = 0, command = app.setting_dialog)

class LISTBOX:
    def __init__(self, master=None):
        self.listbox = Listbox(master, height = 6, exportselection = 0, selectmode = SINGLE)
        self.listbox.yscroll = Scrollbar(master, orient = VERTICAL, command = self.listbox.yview)
        self.listbox.yscroll.pack(side = RIGHT, fill = Y, expand = 0)
        self.listbox["yscrollcommand"] = self.listbox.yscroll.set
        self.listbox.pack(fill = BOTH, expand=1)
    
    def set_entry(self, entry, sel = -1):
        self.listbox.delete(0, END)
        for x in entry:
            self.listbox.insert('end', x)
        if sel >= 0:
            self.listbox.selection_set(sel)

def init(app):
    
    print('登録データ読み込み')
    for x in os.listdir('./'):
        if os.path.isfile(x):
            print(x)
            
            fp = open(x, 'r', encoding = 'cp932')
            try:
                lines = fp.read()
                line = lines.split('\n')
                line = line[0].replace('\n', '')
                print('"%s"'%(line))
                if line == "PMCA Parts list v1.0" or line == "PMCA Materials list v1.1" or line == "PMCA Materials list v1.0" or line == "PMCA Textures list v1.0" or line == "PMCA Bone_Group list v1.0":
                    fp.close()
                    
                    if os.name == 'posix':
                        fp = open(x, 'w', encoding = 'cp932')
                        fp.write(lines)
                        fp.close()
                        converter.v1_v2('./converter/PMCA_1.0-2.0converter', [x])
                    elif os.name == 'nt':
                        converter.v1_v2('.\\converter\\PMCA_1.0-2.0converter.exe', [x])
                if line == "bone":
                    fp = open(x, 'r', encoding = 'cp932')
                    lines = fp.read()
                    fp.close()
                    
                    fp = open(x, 'w', encoding = 'utf-8')
                    fp.write('PMCA list data v2.0\n')
                    fp.write(lines)
                    fp.close()
                    
            except UnicodeDecodeError:
                fp.close()
            fp = open(x, 'r', encoding = 'utf-8-sig')
            try:
                line = fp.readline()
                print(line)
                
                if line=='PMCA Parts list v2.0\n' :
                    app.parts_tree.load_partslist(fp)
                elif line=='PMCA Materials list v2.0\n' :
                    app.materials.load_materiallist(fp)
                elif line=='PMCA Transform list v2.0\n' :
                    app.transform.load_transformlist(fp)
                
                fp.close()
            except UnicodeDecodeError:
                fp.close()
            except UnicodeEncodeError:
                fp.close()
            
    print('list.txt読み込み')
    with open('list.txt', 'r', encoding = 'utf-8-sig') as fp:
        LIST = PyPMCA.load_list(fp)
        PMCA.Set_List(len(LIST['b'][0]), LIST['b'][0], LIST['b'][1], len(LIST['s'][0]), LIST['s'][0], LIST['s'][1], len(LIST['g'][0]), LIST['g'][0], LIST['g'][1])   

    app.tab[0].l_tree.set_entry(app.parts_tree.tree_entry, sel=0)
    app.tab[0].l_sel.set_entry(app.parts_tree.parts_entry_k)
    app.tab[2].tfgroup.set_entry(app.transform.tmp)     
    app.tab[3].frame.name.set('PMCAモデル')
    app.tab[3].frame.name_l.set('PMCAモデル')
    app.tab[3].frame.comment.delete('1.0',END)
    

def main():
    root = Tk()
    app = MainFrame(master=root)
    menubar = MENUBAR(master=root, app=app)
    
    PMCA.Init_PMD()
    init(app)
    
        
    try:
        app.load_CNL_File('./last.cnl')
    except Exception as ex:
        print(ex)
        print('前回のデータの読み込みに失敗しました')
        
    PMCA.CretateViewerThread()
    
    app.refresh()
    app.mainloop()
    #model = PyPMCA.Get_PMD(0)
    
    
    #PMCA.PMD_view_set(0, 'replace')
    #PyPMCA.Set_PMD(0, model)
    #PMCA.Write_PMD(0, "./model/output.pmd")
    
    try:
        app.save_CNL_File('./last.cnl')
    except:
        pass
    
    PMCA.QuitViewerThread()
    

if __name__ == "__main__":
    main()
