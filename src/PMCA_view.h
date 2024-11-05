#pragma once
#include "mPMD.h"

void view_model_initialize();
void view_model_copy(struct MODEL *src);

DLL void CreateViewerThread();
DLL void QuitViewerThread();
DLL void MODEL_LOCK(int num);
