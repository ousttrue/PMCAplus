#include <memory>

#include "PMCA_PyMod.h"
#include "pmd_model.h"

#define PMCA_MODULE
#define MODEL_COUNT 16

static PyObject *PMCAError;

static std::shared_ptr<MODEL> g_model[16];
static NameList list;

#include <plog/Appenders/ColorConsoleAppender.h>
#include <plog/Formatters/TxtFormatter.h>
#include <plog/Init.h>
#include <plog/Log.h>

/*データ変換Utils*/
PyObject *Array_to_PyList_UShort(const unsigned short *input, int count) {
  auto l = PyList_New(0);
  for (int i = 0; i < count; i++) {
    auto x = PyLong_FromLong((int)input[i]);
    if (x == NULL)
      break;
    PyList_Append(l, x);
    Py_DECREF(x);
  }
  // Py_INCREF(l);
  return l;
}

PyObject *Array_to_PyList_Float(const float *input, int count) {
  auto l = PyList_New(0);
  for (int i = 0; i < count; i++) {
    auto x = PyFloat_FromDouble(input[i]);
    if (x == NULL)
      break;
    PyList_Append(l, x);
    Py_DECREF(x);
  }
  // Py_INCREF(l);
  return l;
}

int PyList_to_Array_Float(float *output, PyObject *List, int size) {
  for (int i = 0; i < size; i++) {
    auto tmp = PyList_GetItem(List, i);
    output[i] = PyFloat_AsDouble(tmp);
  }
  return 0;
}

int PyList_to_Array_UShort(unsigned short *output, PyObject *List, int size) {
  if (size > PyList_Size(List))
    return -1;
  for (int i = 0; i < size; i++) {
    auto tmp = PyList_GetItem(List, i);
    if (tmp == NULL)
      return -1;
    output[i] = (unsigned short)PyLong_AsLong(tmp);
    // printf("%d, ", (int)output[i]);
  }
  // printf("\n");
  return 0;
}

std::vector<std::string> PyList_to_Array_Str(PyObject *List) {
  auto size = PyList_GET_SIZE(List);
  std::vector<std::string> list;
  for (size_t i = 0; i < size; i++) {
    auto tmp = PyList_GetItem(List, i);
    char *p;
    Py_ssize_t maxlen;
    if (PyBytes_AsStringAndSize(tmp, &p, &maxlen) == 0) {
      list.push_back(p);
    } else {
      list.push_back("");
    }
  }
  return list;
}

/*******************************************************************************/
static PyObject *Set_List(PyObject *self, PyObject *args) {
  PyObject *bn, *bne, *sn, *sne, *gn, *gne;
  int bone_count;
  int skin_count;
  int disp_count;
  if (!PyArg_ParseTuple(args, "iOOiOOiOO", &bone_count, &bn, &bne, &skin_count,
                        &sn, &sne, &disp_count, &gn, &gne))
    Py_RETURN_FALSE;

  list.bone.resize(bone_count);
  list.bone_eng.resize(bone_count);
  list.skin.resize(skin_count);
  list.skin_eng.resize(skin_count);
  list.disp.resize(disp_count);
  list.disp_eng.resize(disp_count);

  /*ボーン*/
  for (int i = 0; i < bone_count; i++) {
    auto tmp = PyList_GetItem(bn, i);
    char *p = NULL;
    Py_ssize_t len;
    PyBytes_AsStringAndSize(tmp, &p, &len);
    strncpy(list.bone[i].data(), p, NAME_LEN);

    tmp = PyList_GetItem(bne, i);
    PyBytes_AsStringAndSize(tmp, &p, &len);
    strncpy(list.bone_eng[i].data(), p, NAME_LEN);
    // printf("%d %s\n", i, list.bone[i]);
  }

  /*表情*/
  for (int i = 0; i < skin_count; i++) {
    auto tmp = PyList_GetItem(sn, i);
    char *p = NULL;
    Py_ssize_t len;
    PyBytes_AsStringAndSize(tmp, &p, &len);
    strncpy(list.skin[i].data(), p, NAME_LEN);

    tmp = PyList_GetItem(sne, i);
    PyBytes_AsStringAndSize(tmp, &p, &len);
    strncpy(list.skin_eng[i].data(), p, NAME_LEN);
  }

  /*ボーングループ*/
  for (int i = 0; i < disp_count; i++) {
    auto tmp = PyList_GetItem(gn, i);
    char *p = NULL;
    Py_ssize_t len;
    PyBytes_AsStringAndSize(tmp, &p, &len);
    strncpy(list.disp[i].data(), p, NAME_LEN);

    tmp = PyList_GetItem(gne, i);
    PyBytes_AsStringAndSize(tmp, &p, &len);
    strncpy(list.disp_eng[i].data(), p, NAME_LEN);
  }

  return Py_BuildValue("i", 0);
}

/*******************************************************************************/

static PyObject *Set_Name_Comment(PyObject *self, PyObject *args) {
  const char *name;
  const char *comment;
  const char *name_eng;
  const char *comment_eng;
  int num;
  int ret;
  if (!PyArg_ParseTuple(args, "iyyyy", &num, &name, &comment, &name_eng,
                        &comment_eng))
    Py_RETURN_FALSE;

  strncpy(g_model[num]->header.name.data(), name, NAME_LEN);
  strncpy(g_model[num]->header.comment.data(), comment, COMMENT_LEN);
  strncpy(g_model[num]->header.name_eng.data(), name_eng, NAME_LEN);
  strncpy(g_model[num]->header.comment_eng.data(), comment_eng, COMMENT_LEN);
  return Py_BuildValue("i", 0);
}

/*******************************************************************************/
static PyObject *Init_PMD(PyObject *self, PyObject *args) {
  for (int i = 0; i < MODEL_COUNT; i++) {
    g_model[i] = MODEL::create();
  }
  return Py_BuildValue("i", 0);
}

static PyObject *Set_PMD(PyObject *self, PyObject *args) {
  int num;
  const uint8_t *p;
  size_t size;
  if (!PyArg_ParseTuple(args, "iy#", &num, &p, &size)) {
    Py_RETURN_NONE;
  }

  auto model = MODEL::create();
  if (size) {
    model->load({p, size});
  }
  g_model[num] = model;

  auto bytes = model->to_bytes();
  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

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

static PyObject *Copy_PMD(PyObject *self, PyObject *args) {
  int src, dst;
  if (!PyArg_ParseTuple(args, "ii", &src, &dst))
    Py_RETURN_FALSE;

  g_model[dst] = g_model[src];
  Py_RETURN_TRUE;
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

static PyObject *Sort_PMD(PyObject *self, PyObject *args) {
  int num;
  if (!PyArg_ParseTuple(args, "i", &num))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  LOGD << "ボーンマージ";
  if (!model->marge_bone()) {
    Py_RETURN_FALSE;
  }

  LOGD << "ボーンソート";
  model->sort_bone(&list);

  LOGD << "表情ソート";
  model->sort_skin(&list);

  LOGD << "ボーングループソート";
  model->sort_disp(&list);

  //-0ボーン削除
  if (strcmp(model->bone[model->bone.size() - 1].name, "-0") == 0) {
    model->bone.pop_back();
  }

  LOGD << "英語対応化";
  model->translate(&list, 1);

  Py_RETURN_TRUE;
}

static PyObject *Resize_Model(PyObject *self, PyObject *args) {
  int num;
  double size;
  if (!PyArg_ParseTuple(args, "id", &num, &size))
    Py_RETURN_FALSE;

  g_model[num]->resize_model(size);
  Py_RETURN_TRUE;
}

static PyObject *Move_Model(PyObject *self, PyObject *args) {
  int num;
  double s[3];
  if (!PyArg_ParseTuple(args, "iddd", &num, &s[0], &s[1], &s[2]))
    Py_RETURN_FALSE;

  g_model[num]->move_model(s);
  Py_RETURN_TRUE;
}

static PyObject *Resize_Bone(PyObject *self, PyObject *args) {
  int num;
  const char *str;
  double len, thi;
  if (!PyArg_ParseTuple(args, "iydd", &num, &str, &len, &thi))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  int index = 0;
  for (; index < model->bone.size(); index++) {
    if (strcmp(model->bone[index].name, str) == 0) {
      break;
    }
  }
  if (index == model->bone.size()) {
    Py_RETURN_FALSE;
  }

  if (!model->scale_bone(index, thi, len, thi)) {
    Py_RETURN_FALSE;
  }

  Py_RETURN_TRUE;
}

static PyObject *Move_Bone(PyObject *self, PyObject *args) {
  int num;
  const char *str;
  double pos[3];
  if (!PyArg_ParseTuple(args, "iyddd", &num, &str, &pos[0], &pos[1], &pos[2]))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  int index = 0;
  for (; index < model->bone.size(); index++) {
    if (strcmp(model->bone[index].name, str) == 0) {
      break;
    }
  }
  if (index == model->bone.size()) {
    Py_RETURN_FALSE;
  }

  model->move_bone(index, pos);
  Py_RETURN_TRUE;
}

static PyObject *Update_Skin(PyObject *self, PyObject *args) {
  int num;
  if (!PyArg_ParseTuple(args, "i", &num))
    Py_RETURN_FALSE;

  g_model[num]->update_skin();
  Py_RETURN_FALSE;
}

static PyObject *Adjust_Joints(PyObject *self, PyObject *args) {
  int num;
  if (!PyArg_ParseTuple(args, "i", &num))
    Py_RETURN_FALSE;

  g_model[num]->adjust_joint();
  Py_RETURN_TRUE;
}

static PyObject *Get_PMD(PyObject *self, PyObject *args) {
  int num;
  if (!PyArg_ParseTuple(args, "i", &num)) {
    Py_RETURN_NONE;
  }
  auto model = g_model[num];
  auto bytes = model->to_bytes();
  if (bytes.empty()) {
    Py_RETURN_NONE;
  }

  MODEL::create()->load(bytes);

  return Py_BuildValue("y#", bytes.data(), bytes.size());
}

static PyObject *getWHT(PyObject *self, PyObject *args) {
  int num;
  if (!PyArg_ParseTuple(args, "i", &num))
    Py_RETURN_NONE;

  auto model = g_model[num];
  double min[3] = {0.0, 0.0, 0.0};
  double max[3] = {0.0, 0.0, 0.0};
  for (size_t i = 0; i < model->vt.size(); i++) {
    for (size_t j = 0; j < 3; j++) {
      if (model->vt[i].loc[j] > max[j]) {
        max[j] = model->vt[i].loc[j];
      } else if (model->vt[i].loc[j] < min[j]) {
        min[j] = model->vt[i].loc[j];
      }
    }
  }

  double wht[3];
  for (size_t i = 0; i < 3; i++) {
    wht[i] = (max[i] - min[i]) * 8;
  }

  return Py_BuildValue("(fff)", wht[0], wht[1], wht[2]);
}

static PyMethodDef PMCAMethods[] = {
    /***********************************************************************/
    {"Set_List", Set_List, METH_VARARGS, "Set List of bone or things"},
    /***********************************************************************/
    {"Set_Name_Comment", Set_Name_Comment, METH_VARARGS,
     "Set Name and Comment"},
    /***********************************************************************/
    {"Init_PMD", Init_PMD, METH_VARARGS, "Initialize"},
    {"Set_PMD", Set_PMD, METH_VARARGS, "Set PMD bytes"},
    {"Add_PMD", Add_PMD, METH_VARARGS, "Add PMD from file"},
    {"Copy_PMD", Copy_PMD, METH_VARARGS, "Copy PMD"},
    {"Marge_PMD", Marge_PMD, METH_VARARGS, "Marge PMD"},
    {"Sort_PMD", Sort_PMD, METH_VARARGS, "Sort PMD"},
    {"Get_PMD", Get_PMD, METH_VARARGS, "Get PMD Vertices, Indices, Submeshes"},
    /***********************************************************************/
    {"Resize_Model", Resize_Model, METH_VARARGS, "Resize_Model"},
    {"Move_Model", Move_Model, METH_VARARGS, "Move_Model"},
    {"Resize_Bone", Resize_Bone, METH_VARARGS, "Resize_Bone"},
    {"Move_Bone", Move_Bone, METH_VARARGS, "Move_Bone"},
    {"Update_Skin", Update_Skin, METH_VARARGS, "Update_Skin"},
    {"Adjust_Joints", Adjust_Joints, METH_VARARGS, "Adjust_Joints"},

    /***********************************************************************/
    {"getWHT", getWHT, METH_VARARGS, "get height, width, thickness from model"},
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
