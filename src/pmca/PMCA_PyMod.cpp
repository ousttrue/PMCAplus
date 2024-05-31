#include <memory>

#include "PMCA_PyMod.h"
#include "pmd_model.h"

static PyObject *PMCAError;

#include <plog/Appenders/ColorConsoleAppender.h>
#include <plog/Formatters/TxtFormatter.h>
#include <plog/Init.h>
#include <plog/Log.h>

static PyObject *Add_PMD(PyObject *self, PyObject *args) {
  const uint8_t *pa;
  size_t sa;
  const uint8_t *pb;
  size_t sb;
  if (!PyArg_ParseTuple(args, "y#y#", &pa, &sa, &pb, &sb)) {
    Py_RETURN_FALSE;
  }

  auto a = MODEL::from_bytes({pa, sa});
  auto b = MODEL::from_bytes({pb, sb});
  a->add_PMD(b);

  auto bytes = a->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyObject *Marge_PMD(PyObject *self, PyObject *args) {
  const uint8_t *pa;
  size_t sa;
  if (!PyArg_ParseTuple(args, "y#", &pa, &sa)) {
    Py_RETURN_NONE;
  }

  auto model = MODEL::from_bytes({pa, sa});
  LOGD << "ボーンマージ";
  if (!model->marge_bone()) {
    Py_RETURN_NONE;
  }

  LOGD << "材質マージ";
  if (!model->marge_mat()) {
    Py_RETURN_NONE;
  }

  LOGD << "IKマージ";
  model->marge_IK();

  LOGD << "ボーングループマージ";
  model->marge_bone_disp();

  LOGD << "剛体マージ";
  model->marge_rb();

  auto bytes = model->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyObject *Resize_Bone(PyObject *self, PyObject *args) {
  const uint8_t *pa;
  size_t sa;
  const char *str;
  double len, thi;
  if (!PyArg_ParseTuple(args, "y#ydd", &pa, &sa, &str, &len, &thi)) {
    Py_RETURN_NONE;
  }

  auto model = MODEL::from_bytes({pa, sa});
  int index = 0;
  for (; index < model->bone.size(); index++) {
    if (strcmp(model->bone[index].name, str) == 0) {
      break;
    }
  }
  if (index == model->bone.size()) {
    Py_RETURN_NONE;
  }

  if (!model->scale_bone(index, thi, len, thi)) {
    // Py_RETURN_NONE;
  }

  auto bytes = model->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyObject *Move_Bone(PyObject *self, PyObject *args) {
  const uint8_t *pa;
  size_t sa;
  const char *str;
  double pos[3];
  if (!PyArg_ParseTuple(args, "y#yddd", &pa, &sa, &str, &pos[0], &pos[1],
                        &pos[2])) {
    Py_RETURN_NONE;
  }

  auto model = MODEL::from_bytes({pa, sa});
  int index = 0;
  for (; index < model->bone.size(); index++) {
    if (strcmp(model->bone[index].name, str) == 0) {
      break;
    }
  }
  if (index == model->bone.size()) {
    Py_RETURN_NONE;
  }

  model->move_bone(index, pos);

  auto bytes = model->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyObject *Update_Skin(PyObject *self, PyObject *args) {
  const uint8_t *pa;
  size_t sa;
  if (!PyArg_ParseTuple(args, "y#", &pa, &sa)) {
    Py_RETURN_NONE;
  }

  auto model = MODEL::from_bytes({pa, sa});
  model->update_skin();

  auto bytes = model->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyObject *Adjust_Joints(PyObject *self, PyObject *args) {
  const uint8_t *pa;
  size_t sa;
  if (!PyArg_ParseTuple(args, "y#", &pa, &sa)) {
    Py_RETURN_NONE;
  }

  auto model = MODEL::from_bytes({pa, sa});
  model->adjust_joint();

  auto bytes = model->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyMethodDef PMCAMethods[] = {
    {"Add_PMD", Add_PMD, METH_VARARGS, "Add PMD from file"},
    {"Marge_PMD", Marge_PMD, METH_VARARGS, "Marge PMD"},
    {"Resize_Bone", Resize_Bone, METH_VARARGS, "Resize_Bone"},
    {"Move_Bone", Move_Bone, METH_VARARGS, "Move_Bone"},
    {"Update_Skin", Update_Skin, METH_VARARGS, "Update_Skin"},
    {"Adjust_Joints", Adjust_Joints, METH_VARARGS, "Adjust_Joints"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef PMCAmodule = {PyModuleDef_HEAD_INIT,
                                        "PMCA",
                                        NULL,
                                        -1,
                                        PMCAMethods,
                                        NULL,
                                        NULL,
                                        NULL,
                                        NULL};

// モジュール登録
PyMODINIT_FUNC PyInit_PMCA(void) {
  if (false) {
    static plog::ColorConsoleAppender<plog::TxtFormatter> consoleAppender;
    plog::init(plog::verbose, &consoleAppender);
  }

  PLOG_INFO << "PyInit_PMCA";

  auto m = PyModule_Create(&PMCAmodule);
  if (m == NULL)
    Py_RETURN_NONE;

  PMCAError = PyErr_NewException("PMCA.error", NULL, NULL);
  Py_INCREF(PMCAError);
  PyModule_AddObject(m, "error", PMCAError);

  return m;
}
