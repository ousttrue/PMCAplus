#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
#インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())
import PMCA
import PyPMCA
import pmca_tkinter
       
        
if __name__ == "__main__":
    PMCA.Init_PMD()

    pmca=PyPMCA.PyPMCA()
    try:
        pmca.load_CNL_File('./last.cnl')
    except Exception as ex:
        #print(ex)
        print('前回のデータの読み込みに失敗しました')

    app = pmca_tkinter.MainFrame(pmca)
              
    PMCA.CretateViewerThread()
    
    app.refresh()
    app.mainloop()
    
    try:
        pmca.save_CNL_File('./last.cnl')
    except:
        pass
    
    PMCA.QuitViewerThread()
