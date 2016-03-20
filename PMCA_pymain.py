#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import shutil
import time

#インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())
sys.path.append('%s/converter'%(os.getcwd()))
sysenc = sys.getfilesystemencoding()

import PMCA
import PyPMCA
import PMCA_dialogs
import pmca_tkinter

import converter

from tkinter import *
from tkinter.messagebox import *
       
        
def init(app):
    
    #print('登録データ読み込み')
    for x in os.listdir('./'):
        if os.path.isfile(x):
            #print(x)
            
            fp = open(x, 'r', encoding = 'cp932')
            try:
                lines = fp.read()
                line = lines.split('\n')
                line = line[0].replace('\n', '')
                #print('"%s"'%(line))
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
                #print(line)
                
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
            
    #print('list.txt読み込み')
    with open('list.txt', 'r', encoding = 'utf-8-sig') as fp:
        LIST = PyPMCA.load_list(fp)
        PMCA.Set_List(len(LIST['b'][0]), LIST['b'][0], LIST['b'][1], len(LIST['s'][0]), LIST['s'][0], LIST['s'][1], len(LIST['g'][0]), LIST['g'][0], LIST['g'][1])   

    app.transform_tab.tfgroup.set_entry(app.transform.tmp)     
    app.info_tab.frame.name.set('PMCAモデル')
    app.info_tab.frame.name_l.set('PMCAモデル')
    app.info_tab.frame.comment.delete('1.0',END)
    

if __name__ == "__main__":
    app = pmca_tkinter.MainFrame()
    
    PMCA.Init_PMD()
    init(app)
    
        
    try:
        app.load_CNL_File('./last.cnl')
    except Exception as ex:
        #print(ex)
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
