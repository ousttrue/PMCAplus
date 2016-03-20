# coding: utf-8
import PMCA


class PMCA_View:

    def __init__(self):
        pass

    def __enter__(self):
        PMCA.CretateViewerThread()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        PMCA.QuitViewerThread()

    def refresh(self):
        '''
        描画モデルを更新する
        '''
        try:
            PMCA.MODEL_LOCK(1)
            PMCA.PMD_view_set(0, 'replace')       
        finally:
            PMCA.MODEL_LOCK(0)
