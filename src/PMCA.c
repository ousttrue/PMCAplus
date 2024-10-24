#include "PMCA.h"
#include "PMCA_SDLMod.h"
#include "PMCA_view.h"
#include "dbg.h"
#include "mlib_PMD_rw01.h"

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
    strncpy(list.bone[i], *bn, strlen(*bn));
    strncpy(list.bone_eng[i], *bne, strlen(*bne));
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
