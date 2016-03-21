#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.getcwd())
import PMCA
import PyPMCA
import pmca_tkinter
       
        
if __name__ == "__main__":
    PMCA.Init_PMD()

    pmca=PyPMCA.PyPMCA()
    try:
        pmca.load_CNL_File('./last.cnl')
    except:
        print('前回のデータの読み込みに失敗しました')

    app = pmca_tkinter.MainFrame()
    app.bind_pmca(pmca)
    app.mainloop()
    pmca.save_CNL_File('./last.cnl')
