#pragma once
#include "mPMD.h"

void *model_mgr(int flag, int num, void *p);
DLL void CreateViewerThread();
DLL void QuitViewerThread();
DLL void MODEL_LOCK(int num);
