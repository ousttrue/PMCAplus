#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
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

    # qt
    qt_app = pmca_qt.App(pmca, scene)

    # tkinter
    tkinter_app = pmca_tkinter.App(pmca, scene)

    pmca.update()
    pmca.force_update_entry()

    while True:
        try:
            qt_app.processEvents()
            tkinter_app.update()
        except:
            break

    pmca.save_CNL_File('./last.cnl')

