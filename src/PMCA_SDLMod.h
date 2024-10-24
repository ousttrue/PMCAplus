#pragma once
#undef _DEBUG
#include "mPMD.h"
#include <Python.h>

#define MODEL_COUNT 16
extern struct MODEL g_model[16];
extern struct LIST list;

PyObject *CreateViewerThread(PyObject *self, PyObject *args);
PyObject *WaitViewerThread(PyObject *self, PyObject *args);
PyObject *QuitViewerThread(PyObject *self, PyObject *args);
PyObject *KillViewerThread(PyObject *self, PyObject *args);
PyObject *GetViewerThreadState(PyObject *self, PyObject *args);
PyObject *show3Dview(PyObject *self, PyObject *args);
