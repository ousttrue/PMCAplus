#include <thread>

#include "PMCA.h"
#include "PMCA_SDLMod.h"

extern int viewer_thread();

std::thread g_thread;

PyObject *CreateViewerThread(PyObject *self, PyObject *args) {
  g_thread = std::thread([]() { viewer_thread(); });
  Py_RETURN_NONE;
}

PyObject *WaitViewerThread(PyObject *self, PyObject *args) {
  g_thread.join();
  Py_RETURN_NONE;
}

PyObject *QuitViewerThread(PyObject *self, PyObject *args) {
  myflags.quit = 1;
  g_thread.join();
  Py_RETURN_NONE;
}

PyObject *KillViewerThread(PyObject *self, PyObject *args) {
  g_thread.detach();
  Py_RETURN_NONE;
}

PyObject *GetViewerThreadState(PyObject *self, PyObject *args) {
  return Py_BuildValue("i", myflags.quit);
}

PyObject *show3Dview(PyObject *self, PyObject *args) {
  if (myflags.quit == 1) {
    g_thread = std::thread([]() { viewer_thread(); });
  }
  Py_RETURN_NONE;
}
