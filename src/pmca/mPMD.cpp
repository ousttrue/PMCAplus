// PMD関係のライブラリ、読み込み書き込み系

#include <math.h>
#include <memory.h>
#include <plog/Log.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dbg.h"
#include "mPMD.h"

int load_PMD(MODEL *model, const std::string &file_name) {
  static MODEL cache_model[64];
  static unsigned char count[64];
  static unsigned char cur_count = 255;

  // キャッシュまわり初期化
  if (cur_count == 255) {
    for (int i = 0; i < 64; i++) {
      count[i] = 255;
      create_PMD(&cache_model[i]);
    }
    cur_count = 0;
  }

  if (file_name.empty()) {
    PLOG_WARNING << "ファイル名がありません";
    return 1;
  }

  if (cur_count > 64) {
    cur_count = 0;
  } else {
    cur_count++;
  }

  int i = 0;
  for (; i < 64; i++) {
    if (count[i] != 255) {
      // printf("%s, %s\n", cache_model[i].header.path, file_name);
      if (cache_model[i].path == file_name) {
        copy_PMD(model, &cache_model[i]);
        count[i] = cur_count;
        break;
      }
    }
  }

  int tmp = cur_count + 1;
  if (tmp >= 64)
    tmp = 0;
  for (int j = 0; j < 64; j++) {
    if (count[i] == tmp) {
      count[i] = 255;
      delete_PMD(&cache_model[i]);
    }
  }
  if (i != 64) {
    printf("Use Cache\n");
    return 0;
  }

  auto pmd = fopen(file_name.c_str(), "rb");
  if (pmd == NULL) {
    PLOG_ERROR << "Can't open file:" << file_name;
    return 1;
  }

  PLOG_DEBUG << file_name;
  model->path = file_name;

  char magic[4] = {0};
  FREAD(magic, 1, 3, pmd);
  model->header.magic = magic;
  FREAD(&model->header.version, 4, 1, pmd);

  if (model->header.magic != "Pmd" || model->header.version != 1.0) {
    printf("Format error\n");
    return -1;
  }

  FREAD(model->header.name, 1, 20, pmd);
  FREAD(model->header.comment, 1, 256, pmd);

#ifdef DEBUG
  printf("%s \n %f \n %s \n %s \n", model->header.magic, model->header.version,
         model->header.name, model->header.comment);
#endif

  int vt_count;
  FREAD(&vt_count, 4, 1, pmd);
  PLOG_DEBUG << "頂点数:" << vt_count;
  model->vt.resize(vt_count);
  for (i = 0; i < vt_count; i++) {
    // fseek(pmd, 38, SEEK_CUR);
    FREAD(model->vt[i].loc, 4, 3, pmd);
    FREAD(model->vt[i].nor, 4, 3, pmd);
    FREAD(model->vt[i].uv, 4, 2, pmd);
    FREAD(model->vt[i].bone_num, 2, 2, pmd);
    FREAD(&model->vt[i].bone_weight, 1, 1, pmd);
    FREAD(&model->vt[i].edge_flag, 1, 1, pmd);
  }

  int vt_index_count;
  FREAD(&vt_index_count, 4, 1, pmd);
  PLOG_DEBUG << "面頂点数:" << vt_index_count;
  model->vt_index.resize(vt_index_count);
  for (i = 0; i < model->vt_index.size(); i++) {
    FREAD(&model->vt_index[i], 2, 1, pmd);
    if (model->vt_index[i] >= model->vt.size()) {
      printf("頂点インデックスが不正です\n");
      return 1;
    }
  }

  int mat_count;
  FREAD(&mat_count, 4, 1, pmd);
  PLOG_DEBUG << "材質数:" << mat_count;
  model->mat.resize(mat_count);
  for (i = 0; i < model->mat.size(); i++) {
    FREAD(model->mat[i].diffuse, 4, 3, pmd);
    FREAD(&model->mat[i].alpha, 4, 1, pmd);
    FREAD(&model->mat[i].spec, 4, 1, pmd);
    FREAD(&model->mat[i].spec_col, 4, 3, pmd);
    FREAD(&model->mat[i].mirror_col, 4, 3, pmd);
    FREAD(&model->mat[i].toon_index, 1, 1, pmd);
    FREAD(&model->mat[i].edge_flag, 1, 1, pmd);
    FREAD(&model->mat[i].vt_index_count, 4, 1, pmd);
    FREAD(&model->mat[i].tex, 1, 20, pmd);
    model->mat[i].tex[21] = '\0';

    auto str = file_name;
    {
      auto char_p = str.rfind('/');
      if (char_p != std::string::npos) {
        str = str.substr(0, char_p + 1);
      } else {
        str = {};
      }
    }

    {
      auto char_p = strchr(model->mat[i].tex, '*');
      if (char_p != NULL) {
        *char_p = '\0';
        ++char_p;
        strcpy(model->mat[i].sph, char_p);
        sprintf(model->mat[i].sph_path, "%s%s\0", str.c_str(),
                model->mat[i].sph);
      } else {
        *model->mat[i].sph = '\0';
      }
    }
    sprintf(model->mat[i].tex_path, "%s%s\0", str.c_str(), model->mat[i].tex);
  }

  uint16_t bone_count;
  FREAD(&bone_count, 2, 1, pmd);
  PLOG_DEBUG << "ボーン数:" << bone_count;
  model->bone.resize(bone_count);
  for (int i = 0; i < model->bone.size(); i++) {
    FREAD(model->bone[i].name, 1, 20, pmd);
    FREAD(&model->bone[i].PBone_index, 2, 1, pmd);
    FREAD(&model->bone[i].TBone_index, 2, 1, pmd);
    FREAD(&model->bone[i].type, 1, 1, pmd);
    FREAD(&model->bone[i].IKBone_index, 2, 1, pmd);
    FREAD(model->bone[i].loc, 4, 3, pmd);
    model->bone[i].name_eng[0] = '\0';
    model->bone[i].name[21] = '\0';
  }

  uint16_t IK_count;
  FREAD(&IK_count, 2, 1, pmd);
  PLOG_DEBUG << "IKデータ数:" << IK_count;
  model->IK.resize(IK_count);
  for (int i = 0; i < model->IK.size(); i++) {
    FREAD(&model->IK[i].IKBone_index, 2, 1, pmd);
    FREAD(&model->IK[i].IKTBone_index, 2, 1, pmd);
    char IK_chain_len;
    FREAD(&IK_chain_len, 1, 1, pmd);
    FREAD(&model->IK[i].iterations, 2, 1, pmd);
    FREAD(&model->IK[i].weight, 4, 1, pmd);
    model->IK[i].IK_chain.resize(IK_chain_len);
    if (IK_chain_len > 0) {
      FREAD(model->IK[i].IK_chain.data(), 2, IK_chain_len, pmd);
    }
  }

  uint16_t skin_count;
  FREAD(&skin_count, 2, 1, pmd);
  PLOG_DEBUG << "表情数:" << skin_count;
  model->skin.resize(skin_count);
  for (int i = 0; i < skin_count; i++) {
    FREAD(model->skin[i].name, 1, 20, pmd);
    int skin_vt_count;
    FREAD(&skin_vt_count, 4, 1, pmd);
    FREAD(&model->skin[i].type, 1, 1, pmd);
    model->skin[i].skin_vt.resize(skin_vt_count);
    for (int j = 0; j < skin_vt_count; j++) {
      FREAD(&model->skin[i].skin_vt[j].index, 4, 1, pmd);
      if (model->skin[i].skin_vt[j].index > model->vt.size()) {
        exit(1);
      }
      FREAD(&model->skin[i].skin_vt[j].loc, 4, 3, pmd);
    }
    model->skin[i].name_eng[0] = '\0';
    model->skin[i].name[20] = '\0';
  }

  uint8_t skin_disp_count;
  FREAD(&skin_disp_count, 1, 1, pmd);
  PLOG_DEBUG << "表情枠:" << skin_disp_count;
  model->skin_disp.resize(skin_disp_count);
  FREAD(model->skin_disp.data(), 2, model->skin_disp.size(), pmd);

  uint8_t bone_group_count;
  FREAD(&bone_group_count, 1, 1, pmd);
  PLOG_DEBUG << "ボーン枠:" << bone_group_count;
  model->bone_group.resize(bone_group_count);
  for (int i = 0; i < bone_group_count; i++) {
    FREAD(&model->bone_group[i].name, 1, 50, pmd);
    model->bone_group[i].name_eng[0] = '\0';
  }

  int bone_disp_count;
  FREAD(&bone_disp_count, 4, 1, pmd);
  PLOG_DEBUG << "表示ボーン数:" << bone_disp_count;
  model->bone_disp.resize(bone_disp_count);
  for (int i = 0; i < bone_disp_count; i++) {
    FREAD(&model->bone_disp[i].index, 2, 1, pmd);
    FREAD(&model->bone_disp[i].bone_group, 1, 1, pmd);
  }

  FREAD(&model->eng_support, 1, 1, pmd);

  if (feof(pmd) != 0) {
    PLOG_DEBUG << "拡張部分なし";
    model->eng_support = 0;
    for (int i = 0; i < 10; i++) {
      int j = i + 1;
      sprintf(model->toon[i], "toon%02d.bmp\0", j);
      sprintf(model->toon_path[i], "toon%02d.bmp\0", j);
    }
    model->rbody_count = 0;
    model->rbody = NULL;
    model->joint_count = 0;
    model->joint = NULL;
    return 0;
  }

  PLOG_DEBUG << "英名対応:" << model->eng_support;

  if (model->eng_support == 1) {
    printf("英名対応PMD\n");
    FREAD(model->header.name_eng, 1, 20, pmd);
    model->header.name_eng[21] = '\0';

    FREAD(model->header.comment_eng, 1, 256, pmd);
    model->header.comment_eng[255] = '\0';

    for (int i = 0; i < model->bone.size(); i++) {
      FREAD(model->bone[i].name_eng, 1, 20, pmd);
      model->bone[i].name_eng[20] = '\0';
    }

    if (model->skin.size() > 0) {
      strcpy(model->skin[0].name_eng, "base");
    }
    for (int i = 1; i < model->skin.size(); i++) {
      FREAD(model->skin[i].name_eng, 1, 20, pmd);
      model->skin[i].name_eng[20] = '\0';
    }
    for (int i = 0; i < model->bone_group.size(); i++) {
      FREAD(model->bone_group[i].name_eng, 1, 50, pmd);
      model->bone_group[i].name_eng[50] = '\0';
    }
  } else {
    printf("英名非対応PMD\n");

    *model->header.name_eng = '\0';
    *model->header.comment_eng = '\0';

    for (i = 0; i < model->bone.size(); i++) {
      *model->bone[i].name_eng = '\0';
    }

    // strncpy(model->skin[0].name_eng, "base", 20);
    // puts(model->skin[0].name);
    for (i = 0; i < model->skin.size(); i++) {
      *model->skin[i].name_eng = '\0';
    }

    for (i = 0; i < model->bone_group.size(); i++) {
      *model->bone_group[i].name_eng = '\0';
    }
  }

  for (i = 0; i < 10; i++) {
    FREAD(model->toon[i], 1, 100, pmd);
    auto str = file_name;
    auto char_p = str.rfind('/');
    if (char_p != std::string::npos) {
      str = str.substr(0, char_p + 1);
    } else {
      str = {};
    }
    sprintf(model->toon_path[i], "%s%s\0", str.c_str(), model->toon[i]);
#ifdef DEBUG
    printf("%s%s\n", str, model->toon[i]);
#endif
  }

  FREAD(&model->rbody_count, 4, 1, pmd);
#ifdef DEBUG
  printf("剛体数:%d\n", model->rbody_count);
#endif
  model->rbody =
      (RIGID_BODY *)MALLOC((size_t)model->rbody_count * sizeof(RIGID_BODY));

  if (model->rbody == NULL) {
    printf("配列を確保できません\n");
    return 1;
  }
  for (i = 0; i < model->rbody_count; i++) {
    FREAD(model->rbody[i].name, 1, 20, pmd);
    FREAD(&model->rbody[i].bone, 2, 1, pmd);
    FREAD(&model->rbody[i].group, 1, 1, pmd);
    FREAD(&model->rbody[i].target, 2, 1, pmd);
    FREAD(&model->rbody[i].shape, 1, 1, pmd);
    FREAD(model->rbody[i].size, 4, 3, pmd);
    FREAD(model->rbody[i].loc, 4, 3, pmd);
    FREAD(model->rbody[i].rot, 4, 3, pmd);
    FREAD(model->rbody[i].property, 4, 5, pmd);
    FREAD(&model->rbody[i].type, 1, 1, pmd);
    model->rbody[i].name[21] = '\0';
  }

  FREAD(&model->joint_count, 4, 1, pmd);
#ifdef DEBUG
  printf("ジョイント数:%d\n", model->joint_count);
#endif
  model->joint = (JOINT *)MALLOC((size_t)model->joint_count * sizeof(JOINT));
  if (model->joint == NULL) {
    printf("配列を確保できません\n");
    return 1;
  }
  for (i = 0; i < model->joint_count; i++) {
    FREAD(model->joint[i].name, 1, 20, pmd);
    FREAD(model->joint[i].rbody, 4, 2, pmd);
    FREAD(model->joint[i].loc, 4, 3, pmd);
    FREAD(model->joint[i].rot, 4, 3, pmd);
    FREAD(model->joint[i].limit, 4, 12, pmd);
    FREAD(model->joint[i].spring, 4, 6, pmd);
    model->joint[i].name[20] = '\0';
  }

  fclose(pmd);

  // dbg_0check(check,1000);

  // FREE(check);

  // モデルをキャッシュに保存
  for (i = 0; i < 64; i++) {
    if (count[i] == 255) {
      copy_PMD(&cache_model[i], model);
      count[i] = cur_count;
      break;
    }
  }

  return 0;
}

int write_PMD(MODEL *model, const char file_name[]) {
  int i, j, ret = 0;
  char str[PATH_LEN];

  FILE *pmd;

  if (strcmp(file_name, "") == 0) {
    printf("ファイル名がありません\n");
    return 1;
  }

  pmd = fopen(file_name, "wb");
  if (pmd == NULL) {
    printf("ファイル %s を開けません\n", file_name);
    return 1;
  }

  /*ゼロ埋め*/
  /*{
          int total_bytes;
          char b = '\0';
          total_bytes = 283+4+38*model->vt_count
                                          +4+2*model->vt_index_count
                                          +4*70*model->mat_count;
          for(i=0; i<total_bytes; i++){
                  fwrite(&b,1,1,pmd);
          }
          fseek(pmd, 0, SEEK_SET);
  }*/

  // ヘッダー書き換え
  model->header.magic = "Pmd";
  model->header.version = 1.0;

  fwrite(model->header.magic.c_str(), 3, 1, pmd);
  fwrite(&model->header.version, 4, 1, pmd);
  fwrite(model->header.name, 20, 1, pmd);
  fwrite(model->header.comment, 256, 1, pmd);

  int vt_count = model->vt.size();
  fwrite(&vt_count, 4, 1, pmd);
  for (i = 0; i < (model->vt.size()); i++) {
    fwrite(model->vt[i].loc, 4, 3, pmd);
    fwrite(model->vt[i].nor, 4, 3, pmd);
    fwrite(model->vt[i].uv, 4, 2, pmd);
    fwrite(model->vt[i].bone_num, 2, 2, pmd);
    fwrite(&model->vt[i].bone_weight, 1, 1, pmd);
    fwrite(&model->vt[i].edge_flag, 1, 1, pmd);
  }

  int vt_index_count = model->vt_index.size();
  fwrite(&vt_index_count, 4, 1, pmd);
  for (i = 0; i < model->vt_index.size(); i++) {
    if (model->vt_index[i] >= model->vt.size()) {
      printf("頂点インデックスが不正です :%d\n", model->vt_index[i]);
      return 1;
    }
    fwrite(&model->vt_index[i], 2, 1, pmd);
  }

  int mat_count = model->mat.size();
  fwrite(&mat_count, 4, 1, pmd);
  for (i = 0; i < model->mat.size(); i++) {
    // 70bytes
    fwrite(model->mat[i].diffuse, 4, 3, pmd);
    fwrite(&model->mat[i].alpha, 4, 1, pmd);
    fwrite(&model->mat[i].spec, 4, 1, pmd);
    fwrite(model->mat[i].spec_col, 4, 3, pmd);
    fwrite(model->mat[i].mirror_col, 4, 3, pmd);
    fwrite(&model->mat[i].toon_index, 1, 1, pmd);
    fwrite(&model->mat[i].edge_flag, 1, 1, pmd);
    fwrite(&model->mat[i].vt_index_count, 4, 1, pmd);

    if (*model->mat[i].sph != '\0') {
      sprintf(str, "%s*%s\0", model->mat[i].tex, model->mat[i].sph);
      if (strlen(str) > 20) {
        ret = 2;
      }
      fwrite(str, 1, 20, pmd);
    } else {
      fwrite(model->mat[i].tex, 1, 20, pmd);
    }
  }

  uint16_t bone_count = model->bone.size();
  fwrite(&bone_count, 2, 1, pmd);
  for (i = 0; i < model->bone.size(); i++) {
    fwrite(model->bone[i].name, 1, 20, pmd);
    fwrite(&model->bone[i].PBone_index, 2, 1, pmd);
    fwrite(&model->bone[i].TBone_index, 2, 1, pmd);
    fwrite(&model->bone[i].type, 1, 1, pmd);
    fwrite(&model->bone[i].IKBone_index, 2, 1, pmd);
    fwrite(model->bone[i].loc, 4, 3, pmd);
  }

  uint16_t IK_count = model->IK.size();
  fwrite(&IK_count, 2, 1, pmd);
  for (int i = 0; i < model->IK.size(); i++) {
    fwrite(&model->IK[i].IKBone_index, 2, 1, pmd);
    fwrite(&model->IK[i].IKTBone_index, 2, 1, pmd);
    uint8_t IK_chain_len = model->IK[i].IK_chain.size();
    fwrite(&IK_chain_len, 1, 1, pmd);
    fwrite(&model->IK[i].iterations, 2, 1, pmd);
    fwrite(&model->IK[i].weight, 4, 1, pmd);
    fwrite(model->IK[i].IK_chain.data(), 2, model->IK[i].IK_chain.size(), pmd);
  }
  PLOG_DEBUG << "IKリスト";

  uint16_t skin_count = model->skin.size();
  fwrite(&skin_count, 2, 1, pmd);
  for (i = 0; i < model->skin.size(); i++) {
    fwrite(model->skin[i].name, 1, 20, pmd);
    int skin_vt_count = model->skin[i].skin_vt.size();
    fwrite(&skin_vt_count, 4, 1, pmd);
    fwrite(&model->skin[i].type, 1, 1, pmd);
    for (j = 0; j < model->skin[i].skin_vt.size(); j++) {
      fwrite(&model->skin[i].skin_vt[j].index, 4, 1, pmd);
      fwrite(model->skin[i].skin_vt[j].loc, 4, 3, pmd);
    }
  }
  PLOG_DEBUG << "表情";

  uint8_t skin_disp_count = model->skin_disp.size();
  fwrite(&skin_disp_count, 1, 1, pmd);
  fwrite(model->skin_disp.data(), 2, model->skin_disp.size(), pmd);
  PLOG_DEBUG << "表情表示";

  uint8_t bone_group_count = model->bone_group.size();
  fwrite(&bone_group_count, 1, 1, pmd);
  for (int i = 0; i < model->bone_group.size(); i++) {
    fwrite(model->bone_group[i].name, 1, 50, pmd);
  }

  int bone_disp_count = model->bone_disp.size();
  fwrite(&bone_disp_count, 4, 1, pmd);
  for (int i = 0; i < model->bone_disp.size(); i++) {
    fwrite(&model->bone_disp[i].index, 2, 1, pmd);
    fwrite(&model->bone_disp[i].bone_group, 1, 1, pmd);
  }
  PLOG_DEBUG << "ボーン表示";

  // extension
  fwrite(&model->eng_support, 1, 1, pmd);

  if (model->eng_support == 1) {
    fwrite(model->header.name_eng, 1, 20, pmd);
    fwrite(model->header.comment_eng, 1, 256, pmd);
    for (i = 0; i < model->bone.size(); i++) {
      fwrite(model->bone[i].name_eng, 1, 20, pmd);
    }
    for (i = 1; i < model->skin.size(); i++) {
      fwrite(model->skin[i].name_eng, 1, 20, pmd);
    }
    for (i = 0; i < model->bone_group.size(); i++) {
      fwrite(model->bone_group[i].name_eng, 1, 50, pmd);
    }
  }
  PLOG_DEBUG << "英名";

  for (i = 0; i < 10; i++) {
    fwrite(model->toon[i], 1, 100, pmd);
  }

  fwrite(&model->rbody_count, 4, 1, pmd);

  for (i = 0; i < model->rbody_count; i++) {
    fwrite(model->rbody[i].name, 1, 20, pmd);
    fwrite(&model->rbody[i].bone, 2, 1, pmd);
    fwrite(&model->rbody[i].group, 1, 1, pmd);
    fwrite(&model->rbody[i].target, 2, 1, pmd);
    fwrite(&model->rbody[i].shape, 1, 1, pmd);
    fwrite(model->rbody[i].size, 4, 3, pmd);
    fwrite(model->rbody[i].loc, 4, 3, pmd);
    fwrite(model->rbody[i].rot, 4, 3, pmd);
    fwrite(model->rbody[i].property, 4, 5, pmd);
    fwrite(&model->rbody[i].type, 1, 1, pmd);
  }
#ifdef DEBUG
  printf("剛体\n");
#endif

  fwrite(&model->joint_count, 4, 1, pmd);

  for (i = 0; i < model->joint_count; i++) {
    fwrite(model->joint[i].name, 1, 20, pmd);
    fwrite(model->joint[i].rbody, 4, 2, pmd);
    fwrite(model->joint[i].loc, 4, 3, pmd);
    fwrite(model->joint[i].rot, 4, 3, pmd);
    fwrite(model->joint[i].limit, 4, 12, pmd);
    fwrite(model->joint[i].spring, 4, 6, pmd);
  }
#ifdef DEBUG
  printf("ジョイント\n");
#endif

  fclose(pmd);
  printf("%sへ出力しました。\n", file_name);

  return ret;
}

int print_PMD(MODEL *model, const char file_name[]) {
  int i;

  if (strcmp(file_name, "") == 0) {
    printf("ファイル名がありません\n");
    return 1;
  }

  auto txt = fopen(file_name, "w");
  if (txt == NULL) {
    fprintf(txt, "出力テキストファイルを開けません\n");
    return 1;
  }

  fprintf(txt, "%s \n %f \n %s \n %s \n", model->header.magic.c_str(),
          model->header.version, model->header.name, model->header.comment);

  for (i = 0; i < model->vt.size(); i++) {
    fprintf(txt, "No:%d\n", i);
    fprintf(txt, "Loc:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->vt[i].loc[j]);
    }
    fprintf(txt, "\nNor:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->vt[i].nor[j]);
    }
    fprintf(txt, "\nUV:");
    for (int j = 0; j < 2; j++) {
      fprintf(txt, "%f ", model->vt[i].uv[j]);
    }
    fprintf(txt, "\nBONE:");
    for (int j = 0; j < 2; j++) {
      fprintf(txt, "%d ", model->vt[i].bone_num[j]);
    }
    fprintf(txt, "\nbone_weight:%d\n", model->vt[i].bone_weight);
    fprintf(txt, "edge_flag:%d\n\n", model->vt[i].edge_flag);
  }

  fprintf(txt, "面頂点数:%zu\n", model->vt_index.size());

  for (i = 0; i < model->vt_index.size(); i++) {
    fprintf(txt, "%d\n", model->vt_index[i]);
  }
  fprintf(txt, "\n");

  fprintf(txt, "材質数:%zu\n", model->mat.size());
  for (i = 0; i < model->mat.size(); i++) {
    fprintf(txt, "No:%d\n", i);
    fprintf(txt, "diffuse:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->mat[i].diffuse[j]);
    }
    fprintf(txt, "\n%f", model->mat[i].alpha);
    fprintf(txt, "\n%f", model->mat[i].spec);
    fprintf(txt, "\nspec_col:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->mat[i].spec_col[j]);
    }
    fprintf(txt, "\nmirror_col:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->mat[i].mirror_col[j]);
    }
    fprintf(txt, "\ntoon_index:%d\n", model->mat[i].toon_index);
    fprintf(txt, "edge_flag:%d\n", model->mat[i].edge_flag);
    fprintf(txt, "vt_index_count:%d\n", model->mat[i].vt_index_count);
    fprintf(txt, "texture:%s\n\n", model->mat[i].tex);
  }

  fprintf(txt, "ボーン数:%zu\n", model->bone.size());
  for (i = 0; i < model->bone.size(); i++) {
    fprintf(txt, "ボーン名:%s\n", model->bone[i].name);
    fprintf(txt, "親ボーン:%d\n", model->bone[i].PBone_index);
    fprintf(txt, "テイルボーン:%d\n", model->bone[i].TBone_index);
    fprintf(txt, "タイプ:%d\n", model->bone[i].type);
    fprintf(txt, "IKボーン:%d\n", model->bone[i].IKBone_index);
    fprintf(txt, "位置:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->bone[i].loc[j]);
    }
    fprintf(txt, "\n\n");
  }

  fprintf(txt, "IKデータ数:%zu\n", model->IK.size());
  for (int i = 0; i < model->IK.size(); i++) {
    fprintf(txt, "IKボーン:%d\n", model->IK[i].IKBone_index);
    fprintf(txt, "IKテイルボーン:%d\n", model->IK[i].IKTBone_index);
    fprintf(txt, "IKチェーン長:%zu\n", model->IK[i].IK_chain.size());
    fprintf(txt, "iteration:%d\n", model->IK[i].iterations);
    fprintf(txt, "ウエイト:%f\n", model->IK[i].weight);
    for (int j = 0; j < model->IK[i].IK_chain.size(); j++) {
      fprintf(txt, "IK子 %d:%d\n", j, model->IK[i].IK_chain[j]);
    }
    fprintf(txt, "\n");
  }

  fprintf(txt, "表情数:%zu\n", model->skin.size());
  for (i = 0; i < model->skin.size(); i++) {
    fprintf(txt, "表情名:%s\n", model->skin[i].name);
    fprintf(txt, "表情頂点数:%zu\n", model->skin[i].skin_vt.size());
    fprintf(txt, "表情タイプ:%d\n", model->skin[i].type);
    for (int j = 0; j < model->skin[i].skin_vt.size(); j++) {
      fprintf(txt, "%d ", model->skin[i].skin_vt[j].index);
      for (int k = 0; k < 3; k++) {
        fprintf(txt, "%f ", model->skin[i].skin_vt[j].loc[k]);
      }
      fprintf(txt, "\n");
    }
    fprintf(txt, "\n");
  }

  fprintf(txt, "\n表情枠:%zu\n", model->skin_disp.size());
  for (int i = 0; i < model->skin_disp.size(); i++) {
    fprintf(txt, "%d\n", model->skin_disp[i]);
  }

  fprintf(txt, "\nボーン枠:%zu\n", model->bone_group.size());

  for (int i = 0; i < model->bone_group.size(); i++) {
    fprintf(txt, "%d %s", i, model->bone_group[i].name);
  }

  fprintf(txt, "\n表示ボーン数:%zu\n", model->bone_disp.size());

  for (i = 0; i < model->bone_disp.size(); i++) {
    fprintf(txt, "ボーン番号:%d\n", model->bone_disp[i].index);
    fprintf(txt, "表示番号:%d\n", model->bone_disp[i].bone_group);
  }

  fprintf(txt, "英名対応:%d\n", model->eng_support);
  if (model->eng_support == 1) {
    fprintf(txt, "%s\n", model->header.name_eng);
    fprintf(txt, "%s\n", model->header.comment_eng);
    for (i = 0; i < model->bone.size(); i++) {
      fprintf(txt, "%s\n", model->bone[i].name_eng);
    }
    for (i = 0; i < model->skin.size(); i++) {
      fprintf(txt, "%s\n", model->skin[i].name_eng);
    }
    for (i = 0; i < model->bone_group.size(); i++) {
      fprintf(txt, "%s\n", model->bone_group[i].name_eng);
    }
  }

  for (i = 0; i < 10; i++) {
    fprintf(txt, "%s\n", model->toon[i]);
  }

  fprintf(txt, "剛体数:%d\n", model->rbody_count);

  for (i = 0; i < model->rbody_count; i++) {
    fprintf(txt, "%s\n", model->rbody[i].name);
    fprintf(txt, "ボーン:%d\n", model->rbody[i].bone);
    fprintf(txt, "グループ:%d\n", model->rbody[i].group);
    fprintf(txt, "ターゲット:%d\n", model->rbody[i].target);
    fprintf(txt, "形状:%d\n", model->rbody[i].shape);
    fprintf(txt, "size:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->rbody[i].size[j]);
    }
    fprintf(txt, "\nloc:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->rbody[i].loc[j]);
    }
    fprintf(txt, "\nrot:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->rbody[i].rot[j]);
    }
    fprintf(txt, "\nproperty:");
    for (int j = 0; j < 5; j++) {
      fprintf(txt, "%f ", model->rbody[i].property[j]);
    }
    fprintf(txt, "\n");
    fprintf(txt, "タイプ:%d\n\n", model->rbody[i].type);
  }

  fprintf(txt, "ジョイント数:%d\n", model->joint_count);
  for (i = 0; i < model->joint_count; i++) {
    fprintf(txt, "%s\n", model->joint[i].name);
    fprintf(txt, "剛体:");
    for (int j = 0; j < 2; j++) {
      fprintf(txt, "%d ", model->joint[i].rbody[j]);
    }
    fprintf(txt, "\nloc:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->joint[i].loc[j]);
    }
    fprintf(txt, "\nrot:");
    for (int j = 0; j < 3; j++) {
      fprintf(txt, "%f ", model->joint[i].rot[j]);
    }
    fprintf(txt, "\nlimit:");
    for (int j = 0; j < 12; j++) {
      fprintf(txt, "%f ", model->joint[i].limit[j]);
    }
    fprintf(txt, "\nspring:");
    for (int j = 0; j < 6; j++) {
      fprintf(txt, "%f ", model->joint[i].spring[j]);
    }
    fprintf(txt, "\n");
  }

  fclose(txt);

  return 0;
}

int create_PMD(MODEL *model) {
  strcpy(model->header.name, "");
  strcpy(model->header.comment, "");
  model->vt.clear();
  model->vt_index.clear();
  model->mat.clear();
  model->bone.clear();
  model->IK.clear();
  model->skin.clear();
  model->skin_disp.clear();
  model->bone_group.clear();
  model->bone_disp.clear();
  model->eng_support = 0;

  for (int i = 0; i < 10; i++) {
    int j = i + 1;
    //*model->toon[i] = '\0';
    //*model->toon_path[i] = '\0';
    sprintf(model->toon[i], "toon%02d.bmp\0", j);
    sprintf(model->toon_path[i], "toon%02d.bmp\0", j);
  }

  model->rbody_count = 0;
  model->rbody = NULL;
  model->joint_count = 0;
  model->joint = NULL;

  return 0;
}

int delete_PMD(MODEL *model) {
  model->header.name[0] = '\0';
  model->header.comment[0] = '\0';

  model->vt.clear();
  model->vt_index.clear();
  model->mat.clear();
  model->bone.clear();
  model->IK.clear();
  model->skin.clear();
  model->skin_disp.clear();
  model->bone_group.clear();
  model->bone_disp.clear();
  model->eng_support = 0;

  for (int i = 0; i < 10; i++) {
    int j = i + 1;
    /**model->toon[i] = '\0';
     *model->toon_path[i] = '\0';
     */
    sprintf(model->toon[i], "toon%02d.bmp\0", j);
    sprintf(model->toon_path[i], "toon%02d.bmp\0", j);
  }

  FREE(model->rbody);
  model->rbody_count = 0;
  model->rbody = NULL;

  FREE(model->joint);
  model->joint_count = 0;
  model->joint = NULL;

  return 0;
}

int copy_PMD(MODEL *out, MODEL *model) {
  out->header = model->header;
  out->vt = model->vt;
  out->vt_index = model->vt_index;
  out->mat = model->mat;
  out->bone = model->bone;
  out->IK = model->IK;
  out->skin = model->skin;
  out->skin_disp = model->skin_disp;
  out->bone_group = model->bone_group;
  out->bone_disp = model->bone_disp;

  memcpy(out->toon, model->toon, sizeof(char) * 10 * 100);
  memcpy(out->toon_path, model->toon_path, sizeof(char) * 10 * NAME_LEN);

  // 英名
  out->eng_support = model->eng_support;
#ifdef DEBUG
  printf("英名\n");
#endif

  // 剛体
  out->rbody_count = model->rbody_count;
  out->rbody =
      (RIGID_BODY *)MALLOC((size_t)model->rbody_count * sizeof(RIGID_BODY));
  if (out->rbody == NULL)
    return -1;
  for (int i = 0; i < model->rbody_count; i++) {
    out->rbody[i] = model->rbody[i];
  }
#ifdef DEBUG
  printf("剛体\n");
#endif
  // ジョイント
  out->joint_count = model->joint_count;
  out->joint = (JOINT *)MALLOC((size_t)model->joint_count * sizeof(JOINT));
  if (out->joint == NULL)
    return -1;
  for (int i = 0; i < model->joint_count; i++) {
    out->joint[i] = model->joint[i];
  }
#ifdef DEBUG
  printf("ジョイント\n");
#endif

  return 0;
}

int add_PMD(MODEL *model, MODEL *add) {

  int i, j, k;
  int size;
  int tmp[3];

  // ENGLISH eg;
  unsigned int rbody_count;
  RIGID_BODY *rbody;
  unsigned int joint_count;
  JOINT *joint;

  // 頂点
  std::vector<VERTEX> vt(model->vt.size() + add->vt.size());
  for (i = 0; i < model->vt.size(); i++) {
    vt[i] = model->vt[i];
  }
  j = 0;
  for (i = model->vt.size(); i < vt.size(); i++) {
    vt[i] = add->vt[j];
    for (k = 0; k < 2; k++) {
      vt[i].bone_num[k] += model->bone.size();
    }
    j++;
  }

  // 面頂点
  std::vector<unsigned short> vt_index(model->vt_index.size() +
                                       add->vt_index.size());
  for (i = 0; i < model->vt_index.size(); i++) {
    vt_index[i] = model->vt_index[i];
  }
  j = 0;
  for (i = model->vt_index.size(); i < vt_index.size(); i++) {
    vt_index[i] = add->vt_index[j] + model->vt.size();
    j++;
  }

  // 材質
  std::vector<MATERIAL> mat(model->mat.size() + add->mat.size());
  for (i = 0; i < model->mat.size(); i++) {
    mat[i] = model->mat[i];
  }
  j = 0;
  for (i = model->mat.size(); i < mat.size(); i++) {
    mat[i] = add->mat[j];
    j++;
  }

  // ボーン
  std::vector<BONE> bone(model->bone.size() + add->bone.size());
  for (i = 0; i < model->bone.size(); i++) {
    bone[i] = model->bone[i];
  }
  j = 0;
  for (i = model->bone.size(); i < bone.size(); i++) {
    bone[i] = add->bone[j];
    if (bone[i].PBone_index != USHORT_MAX)
      bone[i].PBone_index = bone[i].PBone_index + model->bone.size();
    if (bone[i].TBone_index != 0)
      bone[i].TBone_index = bone[i].TBone_index + model->bone.size();
    if (bone[i].IKBone_index != 0)
      bone[i].IKBone_index = bone[i].IKBone_index + model->bone.size();
    j++;
  }

  // IKリスト
  std::vector<IK_LIST> IK(model->IK.size() + add->IK.size());
  for (int i = 0; i < model->IK.size(); i++) {
    IK[i] = model->IK[i];
  }
  j = 0;
  for (i = model->IK.size(); i < IK.size(); i++) {
    IK[i] = add->IK[j];
    IK[i].IKBone_index = IK[i].IKBone_index + model->bone.size();
    IK[i].IKTBone_index = IK[i].IKTBone_index + model->bone.size();
    for (k = 0; k < IK[i].IK_chain.size(); k++) {
      IK[i].IK_chain[k] = IK[i].IK_chain[k] + model->bone.size();
    }
    j++;
  }

  // 表情
  std::vector<SKIN> skin(model->skin.size() + add->skin.size());
  if (add->skin.size() == 0) {
    for (i = 0; i < skin.size(); i++) {
      skin[i] = model->skin[i];
    }
  } else if (model->skin.size() == 0) {
    for (i = 0; i < skin.size(); i++) {
      skin[i] = add->skin[i];
    }
  } else if (model->skin.size() != 0 && add->skin.size() != 0) {
    skin.pop_back();
    skin[0] = model->skin[0];
    skin[0].skin_vt.resize(model->skin[0].skin_vt.size() +
                           add->skin[0].skin_vt.size());
    auto tmp = model->skin[0].skin_vt.size();
    memcpy(skin[0].skin_vt.data(), model->skin[0].skin_vt.data(),
           tmp * sizeof(SKIN_DATA));
    memcpy(&skin[0].skin_vt[tmp], add->skin[0].skin_vt.data(),
           add->skin[0].skin_vt.size() * sizeof(SKIN_DATA));
    // baseの合成

    for (i = 0; i < model->skin[0].skin_vt.size(); i++) {
      skin[0].skin_vt[i].index = model->skin[0].skin_vt[i].index;
    }
    // printf("%d %d %d\n", skin[0].skin_vt_count, model->skin[0].skin_vt_count,
    // add->skin[0].skin_vt_count);
    j = 0;
    for (i = model->skin[0].skin_vt.size(); i < skin[0].skin_vt.size(); i++) {
      // printf("%d \n", i);
      skin[0].skin_vt[i].index =
          add->skin[0].skin_vt[j].index + model->vt.size();
      j++;
    }
    // 表情追加
    for (i = 1; i < model->skin.size(); i++) {
      skin[i] = model->skin[i];
      // printf("%d %d \n", i, size);
    }
    j = 1;
    for (i = model->skin.size(); i < skin.size(); i++) {
      // printf("%d\n", j);
      skin[i] = add->skin[j];
      for (k = 0; k < skin[i].skin_vt.size(); k++) {
        skin[i].skin_vt[k].index =
            skin[i].skin_vt[k].index + model->skin[0].skin_vt.size();
      }
      j++;
    }
  }

  // 表情表示
  std::vector<unsigned short> skin_disp(model->skin_disp.size() +
                                        add->skin_disp.size());
  memcpy(skin_disp.data(), model->skin_disp.data(),
         model->skin_disp.size() * sizeof(unsigned short));
  j = 0;
  for (int i = model->skin_disp.size(); i < skin_disp.size(); i++) {
    skin_disp[i] = add->skin_disp[j] + model->skin_disp.size();
    j++;
  }

  // ボーン表示
  std::vector<BONE_GROUP> bone_group(model->bone_group.size() +
                                     add->bone_group.size());
  for (int i = 0; i < model->bone_group.size(); i++) {
    bone_group[i] = model->bone_group[i];
  }
  j = 0;
  for (int i = model->bone_group.size(); i < bone_group.size(); i++) {
    bone_group[i] = add->bone_group[j];
    j++;
  }

  std::vector<BONE_DISP> bone_disp(model->bone_disp.size() +
                                   add->bone_disp.size());
  for (int i = 0; i < model->bone_disp.size(); i++) {
    bone_disp[i] = model->bone_disp[i];
  }
  j = 0;
  for (i = model->bone_disp.size(); i < bone_disp.size(); i++) {
    bone_disp[i].index = add->bone_disp[j].index + model->bone.size();
    bone_disp[i].bone_group =
        add->bone_disp[j].bone_group + model->bone_group.size();
    j++;
  }

  // 英名
  model->eng_support = add->eng_support;

  // 剛体
  rbody_count = model->rbody_count + add->rbody_count;
  rbody = (RIGID_BODY *)MALLOC((size_t)rbody_count * sizeof(RIGID_BODY));

  for (i = 0; i < model->rbody_count; i++) {
    rbody[i] = model->rbody[i];
  }
  j = 0;
  for (i = model->rbody_count; i < rbody_count; i++) {
    rbody[i] = add->rbody[j];
    rbody[i].bone = rbody[i].bone + model->bone.size();
    j++;
  }
#ifdef DEBUG
  printf("剛体\n");
#endif
  // ジョイント
  joint_count = model->joint_count + add->joint_count;
  joint = (JOINT *)MALLOC((size_t)joint_count * sizeof(JOINT));

  for (i = 0; i < model->joint_count; i++) {
    joint[i] = model->joint[i];
  }
  j = 0;
  for (i = model->joint_count; i < joint_count; i++) {
    joint[i] = add->joint[j];
    for (k = 0; k < 2; k++) {
      joint[i].rbody[k] = joint[i].rbody[k] + model->rbody_count;
    }
    j++;
  }

#ifdef DEBUG
  printf("ジョイント\n");
#endif

  std::swap(model->vt, vt);
  std::swap(model->vt_index, vt_index);
  std::swap(model->mat, mat);
  std::swap(model->bone, bone);
  std::swap(model->IK, IK);
  std::swap(model->skin, skin);
  std::swap(model->skin_disp, skin_disp);
  std::swap(model->bone_group, bone_group);
  std::swap(model->bone_disp, bone_disp);

#ifdef MEM_DBG
  printf("free %p\n", model->rbody);
#endif
  FREE(model->rbody);
  model->rbody = rbody;
  model->rbody_count = rbody_count;

#ifdef MEM_DBG
  printf("free %p\n", model->joint);
#endif
  FREE(model->joint);
  model->joint = joint;
  model->joint_count = joint_count;

  return 0;
}

int listup_bone(MODEL *model, const char file_name[]) {
  int i;
  char str[64], *p;

  FILE *txt;

  if (strcmp(file_name, "") == 0) {
    printf("ファイル名がありません\n");
    return 1;
  }
  txt = fopen(file_name, "w");
  if (txt == NULL) {
    fprintf(txt, "出力テキストファイルを開けません\n");
    return 1;
  }

  if (model->eng_support == 0) {
    printf("リスト出力ができるのは英名対応モデルのみです\n");
    return 1;
  }

  fprintf(txt, "%s \n %f \n %s \n %s \n", model->header.magic.c_str(),
          model->header.version, model->header.name, model->header.comment);

  fprintf(txt, "ボーン数:%zu\n", model->bone.size());

  for (i = 0; i < model->bone.size(); i++) {
    fprintf(txt, "%s %s\n", model->bone[i].name, model->bone[i].name_eng);
  }

  fprintf(txt, "表情数:%zu\n", model->skin.size());
  for (i = 0; i < model->skin.size(); i++) {
    fprintf(txt, "%s %s\n", model->skin[i].name, model->skin[i].name_eng);
  }
  fprintf(txt, "ボーン枠数:%zu\n", model->bone_group.size());
  for (i = 0; i < model->bone_group.size(); i++) {
    strcpy(str, model->bone_group[i].name);
    p = strchr(str, '\n');
    if (p != NULL)
      *p = '\0';
    fprintf(txt, "%s %s\n", str, model->bone_group[i].name_eng);
  }

  fclose(txt);

  return 0;
}

int get_file_name(char file_name[]) {
  int i;
  char input[256];
  printf("ファイル名:");
  gets_s(input);
  if (input[0] == '\"') {
    for (i = 1; i < 256; i++) {
      file_name[i - 1] = input[i];
      if (input[i] == '\"') {
        file_name[i - 1] = '\0';
        input[i] = '\0';
        break;
      } else if (input[i] == '\0') {
        break;
      }
    }
  } else {
    strcpy(file_name, input);
  }

  return 0;
}
