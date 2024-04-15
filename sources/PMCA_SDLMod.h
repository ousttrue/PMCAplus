#pragma once
#undef _DEBUG
#include <Python.h>

PyObject* CreateViewerThread(PyObject *self, PyObject *args);
PyObject* WaitViewerThread(PyObject *self, PyObject *args);
PyObject* QuitViewerThread(PyObject *self, PyObject *args);
PyObject* KillViewerThread(PyObject *self, PyObject *args);
PyObject* GetViewerThreadState(PyObject *self, PyObject *args);
PyObject* show3Dview(PyObject *self, PyObject *args);

