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
import logging
logger = logging.getLogger(__name__)


logging.basicConfig(
    format='%(levelname)s:%(name)s:%(message)s'
    , level=logging.DEBUG
    )


def filter(r: logging.LogRecord):
    if r.name.startswith('PIL.'):
        return False
    return True
for h in logging.getLogger().handlers:
    h.addFilter(filter)


if __name__ == "__main__":
    PMCA.Init_PMD()

    pmca=PyPMCA.PyPMCA()
    try:
        pmca.load_CNL_File('./last.cnl')
    except:
        logger.info('前回のデータの読み込みに失敗しました')

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
