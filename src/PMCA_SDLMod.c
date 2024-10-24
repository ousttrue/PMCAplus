#include "PMCA_SDLMod.h"
#include "PMCA_view.h"

struct MODEL g_model[MODEL_COUNT];
struct LIST list;
SDL_Thread *viewer_th;

PyObject *_CreateViewerThread(PyObject *self, PyObject *args) {
  viewer_th = SDL_CreateThread(&viewer_thread, NULL);
  Py_RETURN_NONE;
}

PyObject *_WaitViewerThread(PyObject *self, PyObject *args) {
  SDL_WaitThread(viewer_th, NULL);
  Py_RETURN_NONE;
}

PyObject *_QuitViewerThread(PyObject *self, PyObject *args) {
  myflags.quit = 1;
  SDL_WaitThread(viewer_th, NULL);

  Py_RETURN_NONE;
}

PyObject *_KillViewerThread(PyObject *self, PyObject *args) {
  SDL_KillThread(viewer_th);
  Py_RETURN_NONE;
}

PyObject *_GetViewerThreadState(PyObject *self, PyObject *args) {
  return Py_BuildValue("i", myflags.quit);
}

PyObject *_show3Dview(PyObject *self, PyObject *args) {
  if (myflags.quit == 1) {
    viewer_th = SDL_CreateThread(&viewer_thread, NULL);
  }
  Py_RETURN_NONE;
}
