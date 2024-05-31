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

/************************************************************/
static PyObject *Create_FromInfo(PyObject *self, PyObject *args) {
  auto model = MODEL::create();
  int num;
  char *str[4];
  int vt_count;
  int vt_index_count;
  int mat_count;
  int bone_count;
  int IK_count;
  int skin_count;
  int skin_disp_count;
  int bone_group_count;
  int bone_disp_count;
  int rbody_count;
  int joint_count;
  PyObject *PyTmp;
  if (!PyArg_ParseTuple(args,
                        "i"
                        "yyyy"
                        "iiii"
                        "iiii"
                        "iii"
                        "iO",
                        &num, &str[0], &str[1], &str[2], &str[3],

                        &vt_count, &vt_index_count, &mat_count, &bone_count,

                        &IK_count, &skin_count, &bone_group_count,
                        &bone_disp_count,

                        &model->eng_support, &rbody_count, &joint_count,
                        &skin_disp_count, &PyTmp))
    Py_RETURN_FALSE;

  model->header.magic = {'P', 'm', 'd', '\0'};
  model->header.version = 1.0;
  strncpy(model->header.name.data(), str[0], NAME_LEN);
  strncpy(model->header.comment.data(), str[1], 256);
  strncpy(model->header.name_eng.data(), str[2], NAME_LEN);
  strncpy(model->header.comment_eng.data(), str[3], 256);
  g_model[num] = model;

  /* メモリ確保 */
  model->vt.resize(vt_count);
  model->vt_index.resize(vt_index_count * 3);
  model->mat.resize(mat_count);
  model->bone.resize(bone_count);
  model->IK.resize(IK_count);
  model->skin.resize(skin_count);
  model->skin_disp.resize(skin_disp_count);
  PyList_to_Array_UShort(model->skin_disp.data(), PyTmp,
                         model->skin_disp.size());
  model->bone_group.resize(bone_group_count);
  model->bone_disp.resize(bone_disp_count);
  model->rbody.resize(rbody_count);
  model->joint.resize(joint_count);

  Py_RETURN_TRUE;
}

static PyObject *setVt(PyObject *self, PyObject *args) {
  int num, i;
  PyObject *PyTmp[3];
  VERTEX vt;
  if (!PyArg_ParseTuple(args,
                        "iiOOO"
                        "hh"
                        "bb",
                        &num, &i, &PyTmp[0], &PyTmp[1], &PyTmp[2],
                        &vt.bone_num[0], &vt.bone_num[1], &vt.bone_weight,
                        &vt.edge_flag))
    Py_RETURN_FALSE;

  PyList_to_Array_Float(vt.loc, PyTmp[0], 3);
  PyList_to_Array_Float(vt.nor, PyTmp[1], 3);
  PyList_to_Array_Float(vt.uv, PyTmp[2], 2);
  auto model = g_model[num];
  if (model->vt.size() <= i)
    Py_RETURN_FALSE;

  model->vt[i] = vt;
  Py_RETURN_TRUE;
}

static PyObject *setFace(PyObject *self, PyObject *args) {
  int num, i;
  PyObject *PyTmp;
  if (!PyArg_ParseTuple(args, "iiO", &num, &i, &PyTmp))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  if (model->vt_index.size() < i * 3 + 3)
    Py_RETURN_FALSE;

  PyList_to_Array_UShort(&model->vt_index[i * 3], PyTmp, 3);
  Py_RETURN_TRUE;
}

static PyObject *setMat(PyObject *self, PyObject *args) {
  int num, i;
  PyObject *PyTmp[3];
  MATERIAL mat;
  char *str;
  if (!PyArg_ParseTuple(args, "iiOffOOiiiy*", &num, &i, &PyTmp[0], &mat.alpha,
                        &mat.spec, &PyTmp[1], &PyTmp[2],

                        &mat.toon_index, &mat.edge_flag, &mat.vt_index_count,
                        &str)) {
    Py_RETURN_FALSE;
  }

  auto model = g_model[num];
  if (i >= model->mat.size()) {
    Py_RETURN_FALSE;
  }

  // PyList_to_Array_Float(mat.diffuse, PyTmp[0], 3);
  // PyList_to_Array_Float(mat.spec_col, PyTmp[1], 3);
  // PyList_to_Array_Float(mat.mirror_col, PyTmp[2], 3);

  // mat.tex[0] = 0;
  memset(mat.tex, 0, sizeof(mat.tex));
  {
    int j = 0;
    for (; j < 20 && str[j]; ++j) {
      mat.tex[j] = str[j];
    }
    mat.tex[j] = 0;
  }
  // strncpy(mat.sph, str[1], NAME_LEN);
  // strncpy(mat.tex_path, str[2], PATH_LEN);
  // strncpy(mat.sph_path, str[3], PATH_LEN);
  model->mat[i] = mat;
  Py_RETURN_TRUE;
}

static PyObject *setBone(PyObject *self, PyObject *args) {
  int num, i;
  PyObject *PyTmp;
  BONE bone;
  char *str[2];
  if (!PyArg_ParseTuple(args, "iiyyiiiiO", &num, &i, &str[0], &str[1],

                        &bone.PBone_index, &bone.TBone_index, &bone.type,
                        &bone.IKBone_index,

                        &PyTmp))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  if (model->bone.size() <= i)
    Py_RETURN_FALSE;

  strncpy(bone.name, str[0], NAME_LEN);
  strncpy(bone.name_eng, str[1], NAME_LEN);

  PyList_to_Array_Float(bone.loc, PyTmp, 3);
  model->bone[i] = bone;
  Py_RETURN_TRUE;
}

static PyObject *setIK(PyObject *self, PyObject *args) {
  int num, i;
  IK_LIST IK_list;
  PyObject *PyTmp;
  int IK_chain_len;
  if (!PyArg_ParseTuple(args, "iiiiiifO", &num, &i, &IK_list.IKBone_index,
                        &IK_list.IKTBone_index, &IK_chain_len,
                        &IK_list.iterations, &IK_list.weight, &PyTmp))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  if (model->IK.size() <= i)
    Py_RETURN_FALSE;

  printf("%d %zu\n", IK_chain_len, model->IK[i].IK_chain.size());

  IK_list.IK_chain.resize(IK_chain_len);

  PyList_to_Array_UShort(IK_list.IK_chain.data(), PyTmp, IK_chain_len);

  model->IK[i] = IK_list;
  Py_RETURN_TRUE;
}

static PyObject *setSkin(PyObject *self, PyObject *args) {
  int num, i;
  SKIN skin;
  char *str[2];
  int skin_vt_count;
  if (!PyArg_ParseTuple(args, "iiyyib", &num, &i, &str[0], &str[1],
                        &skin_vt_count, &skin.type))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  if (model->skin.size() <= i)
    Py_RETURN_FALSE;

  strncpy(skin.name, str[0], NAME_LEN);
  strncpy(skin.name_eng, str[1], NAME_LEN);

  // メモリ確保
  skin.skin_vt.resize(skin_vt_count);
  model->skin[i] = skin;
  Py_RETURN_TRUE;
}

static PyObject *setSkindata(PyObject *self, PyObject *args) {
  int num, i, j;
  SKIN_DATA data;
  if (!PyArg_ParseTuple(args, "iiii(fff)", &num, &i, &j, &data.index,
                        &data.loc[0], &data.loc[1], &data.loc[2]))
    Py_RETURN_NONE;

  auto model = g_model[num];
  if (model->skin.size() <= i)
    Py_RETURN_NONE;

  if (model->skin[i].skin_vt.size() <= j)
    Py_RETURN_NONE;

  model->skin[i].skin_vt[j] = data;
  return Py_BuildValue("i", 0);
}

static PyObject *setBone_group(PyObject *self, PyObject *args) {
  int num, i;
  char *str[2];
  if (!PyArg_ParseTuple(args, "iiyy", &num, &i, &str[0], &str[1]))
    Py_RETURN_FALSE;

  auto model = g_model[num];

  BONE_GROUP bone_group;
  strncpy(bone_group.name, str[0], NAME_LEN);
  strncpy(bone_group.name_eng, str[1], NAME_LEN);

  model->bone_group[i] = bone_group;

  return Py_BuildValue("i", 0);
}

static PyObject *setBone_disp(PyObject *self, PyObject *args) {
  int num, i;
  BONE_DISP bone_disp;
  if (!PyArg_ParseTuple(args, "iiii", &num, &i, &bone_disp.index,
                        &bone_disp.bone_group))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  model->bone_disp[i] = bone_disp;

  return Py_BuildValue("i", 0);
}

static PyObject *setToon(PyObject *self, PyObject *args) {
  int num, i;
  PyObject *tmp;
  if (!PyArg_ParseTuple(args, "iO", &num, /*
                                     &model->toon[0],
                                     &model->toon[1],
                                     &model->toon[2],
                                     &model->toon[3],
                                     &model->toon[4],
                                     &model->toon[5],
                                     &model->toon[6],
                                     &model->toon[7],
                                     &model->toon[8],
                                     &model->toon[9]*/
                        &tmp))
    Py_RETURN_FALSE;

  auto list = PyList_to_Array_Str(tmp);

  auto model = g_model[num];
  for (size_t i = 0; i < list.size() && i < 10; ++i) {
    model->toon[i] = list[i];
  }

  Py_RETURN_TRUE;
}

static PyObject *setRb(PyObject *self, PyObject *args) {
  int num = 0, i = 0;
  RIGID_BODY rbody;
  char *str;
  if (!PyArg_ParseTuple(
          args,
          "ii"
          "yHBHB"
          "(fff)(fff)(fff)"
          "fffffB",
          &num, &i, &str, &rbody.bone, &rbody.group, &rbody.target,
          &rbody.shape, &rbody.size[0], &rbody.size[1], &rbody.size[2],
          &rbody.loc[0], &rbody.loc[1], &rbody.loc[2], &rbody.rot[0],
          &rbody.rot[1], &rbody.rot[2],

          &rbody.property[0], &rbody.property[1], &rbody.property[2],
          &rbody.property[3], &rbody.property[4], &rbody.type))
    Py_RETURN_FALSE;

  strncpy(rbody.name, str, NAME_LEN);

  auto model = g_model[num];
  model->rbody[i] = rbody;

  return Py_BuildValue("i", 0);
}

static PyObject *setJoint(PyObject *self, PyObject *args) {
  int num, i;
  JOINT joint;
  char *str;
  if (!PyArg_ParseTuple(args,
                        "ii"
                        "y(II)(fff)(fff)"
                        "(ffffffffffff)"
                        "(ffffff)",
                        &num, &i, &str, &joint.rbody[0], &joint.rbody[1],
                        &joint.loc[0], &joint.loc[1], &joint.loc[2],
                        &joint.rot[0], &joint.rot[1], &joint.rot[2],
                        &joint.limit[0], &joint.limit[1], &joint.limit[2],
                        &joint.limit[3], &joint.limit[4], &joint.limit[5],
                        &joint.limit[6], &joint.limit[7], &joint.limit[8],
                        &joint.limit[9], &joint.limit[10], &joint.limit[11],
                        &joint.spring[0], &joint.spring[1], &joint.spring[2],
                        &joint.spring[3], &joint.spring[4], &joint.spring[5]))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  strncpy(joint.name, str, NAME_LEN);
  model->joint[i] = joint;
  return Py_BuildValue("i", 0);
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
    Py_RETURN_FALSE;
  }

  auto model = MODEL::create();
  if (size) {
    model->load({p, size});
  }
  if (model) {
    g_model[num] = model;
  } else {
    // clear
    g_model[num] = MODEL::create();
  }

  Py_RETURN_TRUE;
}

static PyObject *Add_PMD(PyObject *self, PyObject *args) {
  int num, add;
  if (!PyArg_ParseTuple(args, "ii", &num, &add))
    Py_RETURN_FALSE;

  g_model[num]->add_PMD(g_model[add]);
  Py_RETURN_TRUE;
}

static PyObject *Copy_PMD(PyObject *self, PyObject *args) {
  int src, dst;
  if (!PyArg_ParseTuple(args, "ii", &src, &dst))
    Py_RETURN_FALSE;

  g_model[dst] = g_model[src];
  Py_RETURN_TRUE;
}

static PyObject *Marge_PMD(PyObject *self, PyObject *args) {
  int num;
  if (!PyArg_ParseTuple(args, "i", &num))
    Py_RETURN_FALSE;

  auto model = g_model[num];
  LOGD << "ボーンマージ";
  if (!model->marge_bone()) {
    Py_RETURN_FALSE;
  }

  LOGD << "材質マージ";
  if (!model->marge_mat()) {
    Py_RETURN_FALSE;
  }

  LOGD << "IKマージ";
  model->marge_IK();

  LOGD << "ボーングループマージ";
  model->marge_bone_disp();

  LOGD << "剛体マージ";
  model->marge_rb();

  Py_RETURN_TRUE;
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
    {"Create_FromInfo", Create_FromInfo, METH_VARARGS, "Create PMD"},
    {"setVt", setVt, METH_VARARGS, "Set Vertex of PMD"},
    {"setFace", setFace, METH_VARARGS, "Set Face of PMD"},
    {"setMat", setMat, METH_VARARGS, "Set Material of PMD"},
    {"setBone", setBone, METH_VARARGS, "Set Bone of PMD"},
    {"setIK", setIK, METH_VARARGS, "Set IK_List of PMD"},
    {"setSkin", setSkin, METH_VARARGS, "Set Skin of PMD"},
    {"setSkindata", setSkindata, METH_VARARGS, "Set Skin_data of PMD"},
    {"setBone_group", setBone_group, METH_VARARGS, "Set Bone_group of PMD"},
    {"setBone_disp", setBone_disp, METH_VARARGS, "Set Bone_disp of PMD"},
    {"setToon", setToon, METH_VARARGS, "Set Toon textures of PMD"},
    {"setRb", setRb, METH_VARARGS, "Set Rigid bodies of PMD"},
    {"setJoint", setJoint, METH_VARARGS, "Set Joints of PMD"},
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
