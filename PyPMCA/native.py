from typing import Any
import PMCA  # type: ignore


class PmcaView:
    def __init__(self):
        PMCA.Init_PMD()

    def __enter__(self):
        return self

    def __exit__(self, _exception_type: Any, _exception_value: Any, _traceback: Any):
        PMCA.QuitViewerThread()

    def start_thread(self):
        PMCA.CretateViewerThread()
