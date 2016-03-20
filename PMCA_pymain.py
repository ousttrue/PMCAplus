#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.getcwd())
import PMCA
import PyPMCA
import PMCA_View
import pmca_tkinter
       
        
if __name__ == "__main__":
    PMCA.Init_PMD()

    pmca=PyPMCA.PyPMCA()
    try:
        pmca.load_CNL_File('./last.cnl')
    except:
        print('前回のデータの読み込みに失敗しました')

    app = pmca_tkinter.MainFrame()
    with PMCA_View.PMCA_View() as v:
        pmca.model_update_observable.add(v.refresh)
        app.bind_pmca(pmca)
        app.mainloop()
        pmca.save_CNL_File('./last.cnl')
