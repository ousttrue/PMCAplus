#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
mode='tkinter' if len(sys.argv)>1 and sys.argv[1]=='tkinter' else 'qt'
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'glglue'))
import PMCA
import PyPMCA
import PMCA_GL
import pmca_tkinter
import pmca_qt


if __name__ == "__main__":
    PMCA.Init_PMD()

    pmca=PyPMCA.PyPMCA()
    try:
        pmca.load_CNL_File('./last.cnl')
    except:
        print('前回のデータの読み込みに失敗しました')

    scene=PMCA_GL.Scene()

    if mode=='tkinter':
        # tkinter
        app = pmca_tkinter.App(pmca, scene)
    else:
        # qt
        app = pmca_qt.App(pmca, scene)

    pmca.update()
    pmca.force_update_entry()

    app.mainloop()

    pmca.save_CNL_File('./last.cnl')
