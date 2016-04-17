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
    if r.name.startswith('PIL.'):return False
    if r.name.startswith('glglue.'):return False
    return True
for h in logging.getLogger().handlers:
    h.addFilter(filter)


if __name__ == "__main__":
    PMCA.Init_PMD()

    pmca=PyPMCA.PyPMCA()
    scene=PMCA_GL.Scene()

    if mode=='tkinter':
        # tkinter
        app = pmca_tkinter.App(pmca, scene)
    else:
        # qt
        app = pmca_qt.App(pmca, scene)
        while len(logger.root.handlers)>0:
            logger.root.handlers.pop()
        qt_handler=pmca_qt.QPlainTextEditLogger(app.window.logger)
        qt_handler.setLevel(logging.DEBUG)
        qt_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        qt_handler.addFilter(filter)
        logging.root.handlers.append(qt_handler)

    try:
        pmca.load_CNL_File('./last.cnl')
    except:
        logger.info('前回のデータの読み込みに失敗しました')
    pmca.update()
    pmca.force_update_entry()

    app.mainloop()

    pmca.save_CNL_File('./last.cnl')
