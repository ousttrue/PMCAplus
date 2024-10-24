#pragma once
#undef _DEBUG
#include "mPMD.h"
#include <Python.h>
#include <SDL.h>

#define MODEL_COUNT 16
extern struct MODEL g_model[16];
extern struct LIST list;
extern SDL_Thread *viewer_th;

PyObject *_CreateViewerThread(PyObject *self, PyObject *args);
PyObject *_WaitViewerThread(PyObject *self, PyObject *args);
PyObject *_QuitViewerThread(PyObject *self, PyObject *args);
PyObject *_KillViewerThread(PyObject *self, PyObject *args);
PyObject *_GetViewerThreadState(PyObject *self, PyObject *args);
PyObject *_show3Dview(PyObject *self, PyObject *args);
