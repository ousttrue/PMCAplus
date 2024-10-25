#include "PMCA.h"
#include "PMCA_SDLMod.h"
#include "PMCA_view.h"
#include "dbg.h"
#include "mlib_PMD_edit01.h"
#include "mlib_PMD_rw01.h"

static void copy_str(char *dst, const char *src) {}

void Init_PMD() {
  for (int i = 0; i < MODEL_COUNT; i++) {
    create_PMD(&g_model[i]);
  }
  model_mgr(-1, 0, NULL);
}

void Set_List(int bone_count, const char **bn, const char **bne, int skin_count,
              const char **sn, const char **sne, int bone_group_count,
              const char **gn, const char **gne) {
  list.bone_count = bone_count;
  list.bone = MALLOC(list.bone_count * sizeof(char) * NAME_LEN);
  list.bone_eng = MALLOC(list.bone_count * sizeof(char) * NAME_LEN);

  list.skin_count = skin_count;
  list.skin = MALLOC(list.skin_count * sizeof(char) * NAME_LEN);
  list.skin_eng = MALLOC(list.skin_count * sizeof(char) * NAME_LEN);

  list.disp_count = bone_group_count;
  list.disp = MALLOC(list.disp_count * sizeof(char) * NAME_LEN);
  list.disp_eng = MALLOC(list.disp_count * sizeof(char) * NAME_LEN);

  /*ボーン*/
  for (int i = 0; i < list.bone_count; ++i, ++bn, ++bne) {
    strncpy(list.bone[i], *bn, NAME_LEN);
    strncpy(list.bone_eng[i], *bne, NAME_LEN);
  }

  // /*表情*/
  // for (i = 0; i < list.skin_count; i++) {
  //   tmp = PyList_GetItem(sn, i);
  //   // strncpy(list.skin[i], PyBytes_AsString(tmp), NAME_LEN);
  //   PyBytes_AsStringAndSize(tmp, &p, &len);
  //   strncpy(list.skin[i], p, NAME_LEN);
  //
  //   tmp = PyList_GetItem(sne, i);
  //   // strncpy(list.skin_eng[i], PyBytes_AsString(tmp), NAME_LEN);
  //   PyBytes_AsStringAndSize(tmp, &p, &len);
  //   strncpy(list.skin_eng[i], p, NAME_LEN);
  // }
  //
  // /*ボーングループ*/
  // for (i = 0; i < list.disp_count; i++) {
  //   tmp = PyList_GetItem(gn, i);
  //   // strncpy(list.disp[i], PyBytes_AsString(tmp), NAME_LEN);
  //   PyBytes_AsStringAndSize(tmp, &p, &len);
  //   strncpy(list.disp[i], p, NAME_LEN);
  //
  //   tmp = PyList_GetItem(gne, i);
  //   // strncpy(list.disp_eng[i], PyBytes_AsString(tmp), NAME_LEN);
  //   PyBytes_AsStringAndSize(tmp, &p, &len);
  //   strncpy(list.disp_eng[i], p, NAME_LEN);
  // }
}

void CreateViewerThread() {
  viewer_th = SDL_CreateThread(&viewer_thread, NULL);
}

void MODEL_LOCK(int num) {
  if (num == 1) {
    while (myflags.model_lock != 0) {
      SDL_Delay(30);
    }
    myflags.model_lock = 1;
  } else {
    myflags.model_lock = 0;
  }
}

void Create_PMD(int num) { delete_PMD(&g_model[num]); }

void Load_PMD(int num, const char *str) {
  delete_PMD(&g_model[num]);
  load_PMD(&g_model[num], str);
}

void getInfo(int num, const char **name, const char **name_eng,
             const char **comment, const char **comment_eng, int *vt_count,
             int *face_count, int *mat_count, int *bone_count, int *IK_count,
             int *skin_count, int *bone_group_count, int *bone_disp_count,
             int *eng_support, int *rb_count, int *joint_count,
             unsigned short **skin_index) {
  auto model = &g_model[num];
  *name = model->header.name;
  *name_eng = model->header.name_eng;
  *comment = model->header.comment;
  *comment_eng = model->header.comment_eng;
  *vt_count = model->vt_count;
  *face_count = model->vt_index_count / 3;
  *mat_count = model->mat_count;
  *bone_count = model->bone_count;
  *IK_count = model->IK_count;
  *skin_count = model->skin_count;
  *bone_group_count = model->bone_group_count;
  *bone_disp_count = model->bone_disp_count;
  *eng_support = model->eng_support;
  *rb_count = model->rbody_count;
  *joint_count = model->joint_count;
  *skin_index = model->skin_index;
}

void Add_PMD(int num, int add) {
  struct MODEL model;
  create_PMD(&model);
  add_PMD(&g_model[num], &g_model[add]);
  delete_PMD(&model);
}

int Marge_PMD(int num) {
  int ret = marge_bone(&g_model[num]);
  ret += marge_mat(&g_model[num]);
  ret += marge_IK(&g_model[num]);
  ret += marge_bone_disp(&g_model[num]);
  ret += marge_rb(&g_model[num]);
  return ret;
}

int Sort_PMD(int num) {
  rename_tail(&g_model[num]);
  auto ret = marge_bone(&g_model[num]);

  ret = sort_bone(&g_model[num], &list);
  ret += sort_skin(&g_model[num], &list);
  ret += sort_disp(&g_model[num], &list);

  //-0ボーン削除
  if (strcmp(g_model[num].bone[g_model[num].bone_count - 1].name, "-0") == 0) {
    g_model[num].bone_count--;
  }
  translate(&g_model[num], &list, 1);
  return ret;
}

int Copy_PMD(int src, int dst) {
  delete_PMD(&g_model[dst]);
  auto ret = copy_PMD(&g_model[dst], &g_model[src]);
  return ret;
}

void getMat(int num, int i, float *diff_col, float *alpha, float *spec,
            float *spec_col, float *mirr_col, int *toon, int *edge,
            int *face_count, const char **tex, const char **sph,
            const char **tex_path, const char **sph_path) {
  auto model = &g_model[num];
  auto mat = &model->mat[i];
  diff_col[0] = mat->diffuse[0];
  diff_col[1] = mat->diffuse[1];
  diff_col[2] = mat->diffuse[2];
  *alpha = mat->alpha;
  *spec = mat->spec;
  spec_col[0] = mat->spec_col[0];
  spec_col[1] = mat->spec_col[1];
  spec_col[2] = mat->spec_col[2];
  mirr_col[0] = mat->mirror_col[0];
  mirr_col[1] = mat->mirror_col[1];
  mirr_col[2] = mat->mirror_col[2];
  *toon = (int)mat->toon_index;
  *edge = (int)mat->edge_flag;
  *face_count = (int)mat->vt_index_count / 3;
  *tex = mat->tex;
  *sph = mat->sph;
  *tex_path = mat->tex_path;
  *sph_path = mat->sph_path;
}

void setMat(int num, int i, const float *diff_col, float alpha, float spec,
            const float *spec_col, const float *mirr_col, int toon, int edge,
            int face_count, const char *tex, const char *sph,
            const char *tex_path, const char *sph_path) {

  auto model = &g_model[num];
  if (model->mat_count <= i) {
    return;
  }

  struct MATERIAL mat;
  mat.vt_index_count = mat.vt_index_count * 3;
  mat.diffuse[0] = diff_col[0];
  mat.diffuse[1] = diff_col[1];
  mat.diffuse[2] = diff_col[2];
  mat.spec_col[0] = spec_col[0];
  mat.spec_col[1] = spec_col[1];
  mat.spec_col[2] = spec_col[2];
  mat.mirror_col[0] = mirr_col[0];
  mat.mirror_col[1] = mirr_col[1];
  mat.mirror_col[2] = mirr_col[2];
  strncpy(mat.tex, tex, NAME_LEN);
  strncpy(mat.sph, sph, NAME_LEN);
  strncpy(mat.tex_path, tex_path, PATH_LEN);
  strncpy(mat.sph_path, sph_path, PATH_LEN);
  model->mat[i] = mat;
}

void getToon(int num, char **toon) {
  auto model = &g_model[num];
  toon[0] = model->toon[0];
  toon[1] = model->toon[1];
  toon[2] = model->toon[2];
  toon[3] = model->toon[3];
  toon[4] = model->toon[4];
  toon[5] = model->toon[5];
  toon[6] = model->toon[6];
  toon[7] = model->toon[7];
  toon[8] = model->toon[8];
  toon[9] = model->toon[9];
}

void getToonPath(int num, char **toon_path) {
  auto model = &g_model[num];
  toon_path[0] = model->toon_path[0];
  toon_path[1] = model->toon_path[1];
  toon_path[2] = model->toon_path[2];
  toon_path[3] = model->toon_path[3];
  toon_path[4] = model->toon_path[4];
  toon_path[5] = model->toon_path[5];
  toon_path[6] = model->toon_path[6];
  toon_path[7] = model->toon_path[7];
  toon_path[8] = model->toon_path[8];
  toon_path[9] = model->toon_path[9];
}

void setToon(int num, const char **p) {
  auto model = &g_model[num];
  for (int i = 0; i < 10; i++) {
    memcpy(model->toon[i], p[i], 100);
  }
}

void setToonPath(int num, const char **p) {
  auto model = &g_model[num];
  for (int i = 0; i < 10; i++) {
    memcpy(model->toon[i], p[i], 100);
  }
}

bool getBone(int num, int i, const char **name, const char **name_eng,
             int *parent, int *tail, int *type, int *IK, float *loc) {
  auto model = &g_model[num];
  if (model->bone_count <= i) {
    return false;
  }

  auto bone = &model->bone[i];
  *name = bone->name;
  *name_eng = bone->name_eng;
  *parent = bone->PBone_index;
  *tail = bone->TBone_index;
  *type = bone->type;
  *IK = bone->IKBone_index;
  loc[0] = bone->loc[0];
  loc[1] = bone->loc[1];
  loc[2] = bone->loc[2];
  return true;
}

void Resize_Model(int num, float size) { resize_model(&g_model[num], size); }

void Resize_Bone(int num, const char *str, float len, float thi) {
  int index = 0;
  for (; index < g_model[num].bone_count; index++) {
    if (strcmp(g_model[num].bone[index].name, str) == 0) {
      break;
    }
  }
  if (index == g_model[num].bone_count) {
    return;
  }
  scale_bone(&g_model[num], index, thi, len, thi);
}

void Move_Bone(int num, const char *str, float x, float y, float z) {
  int index = 0;
  for (; index < g_model[num].bone_count; index++) {
    if (strcmp(g_model[num].bone[index].name, str) == 0) {
      break;
    }
  }
  if (index == g_model[num].bone_count) {
    return;
  }
  double pos[3] = {x, y, z};
  move_bone(&g_model[num], index, pos);
}

void Move_Model(int num, float x, float y, float z) {
  double s[3] = {x, y, z};
  move_model(&g_model[num], s);
}

void Update_Skin(int num) { update_skin(&g_model[num]); }

void Adjust_Joints(int num) { adjust_joint(&g_model[num]); }

void Set_Name_Comment(int num, const char *name, const char *name_eng,
                      const char *comment, const char *comment_eng) {
  strncpy(g_model[num].header.name, name, NAME_LEN);
  strncpy(g_model[num].header.name_eng, name_eng, NAME_LEN);
  strncpy(g_model[num].header.comment, comment, COMMENT_LEN);
  strncpy(g_model[num].header.comment_eng, comment_eng, COMMENT_LEN);
}

void PMD_view_set(int num, const char *str) {
  if (strcmp(str, "replace") == 0) {
    model_mgr(0, 0, &g_model[num]);
  }
}

void getWHT(int num, float *wht) {
  double min[3] = {0.0, 0.0, 0.0};
  double max[3] = {0.0, 0.0, 0.0};

  for (int i = 0; i < g_model[num].vt_count; i++) {
    for (int j = 0; j < 3; j++) {
      if (g_model[num].vt[i].loc[j] > max[j]) {
        max[j] = g_model[num].vt[i].loc[j];
      } else if (g_model[num].vt[i].loc[j] < min[j]) {
        min[j] = g_model[num].vt[i].loc[j];
      }
    }
  }

  for (int i = 0; i < 3; i++) {
    wht[i] = (max[i] - min[i]) * 8;
  }
}

void QuitViewerThread() {
  myflags.quit = 1;
  SDL_WaitThread(viewer_th, NULL);
}
