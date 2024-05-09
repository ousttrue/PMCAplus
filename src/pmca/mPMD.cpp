// PMD関係のライブラリ、読み込み書き込み系

#include "mPMD.h"
#include "ioutil.h"
#include <plog/Log.h>
#include <string.h>

bool MODEL::load(std::span<uint8_t> bytes, const std::string &file_name) {
  this->path = file_name;

  ioutil::binaryreader r(bytes);

  r.read(this->header.magic.data(), 3);
  if (this->header.magic != std::array<char, 4>{'P', 'm', 'd', '\0'}) {
    PLOG_ERROR << "invalid magic:" << this->header.magic;
    return false;
  }

  this->header.version = r.f32();
  if (this->header.version != 1.0) {
    PLOG_ERROR << "invalid version:" << this->header.version;
    return false;
  }

  r.read(this->header.name.data(), 20);
  PLOG_DEBUG << this->header.name.data();

  r.read(this->header.comment.data(), 256);
  PLOG_DEBUG << this->header.comment.data();

  int vt_count = r.i32();
  ;
  PLOG_DEBUG << "頂点数:" << vt_count;
  this->vt.resize(vt_count);
  r.read(this->vt.data(), vt_count * sizeof(VERTEX));

  int vt_index_count = r.i32();
  ;
  PLOG_DEBUG << "面頂点数:" << vt_index_count;
  this->vt_index.resize(vt_index_count);
  r.read(this->vt_index.data(), vt_index_count * 2);

  int mat_count = r.i32();
  ;
  PLOG_DEBUG << "材質数:" << mat_count;
  this->mat.resize(mat_count);
  for (int i = 0; i < this->mat.size(); i++) {
    r.read(&this->mat[i], 70);
    this->mat[i].tex[21] = '\0';

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
      auto char_p = strchr(this->mat[i].tex, '*');
      if (char_p != NULL) {
        *char_p = '\0';
        ++char_p;
        strcpy(this->mat[i].sph, char_p);
        sprintf(this->mat[i].sph_path, "%s%s\0", str.c_str(), this->mat[i].sph);
      } else {
        *this->mat[i].sph = '\0';
      }
    }
    sprintf(this->mat[i].tex_path, "%s%s\0", str.c_str(), this->mat[i].tex);
  }

  uint16_t bone_count = r.u16();
  PLOG_DEBUG << "ボーン数:" << bone_count;
  this->bone.resize(bone_count);
  for (int i = 0; i < this->bone.size(); i++) {
    r.read(this->bone[i].name, 20);
    this->bone[i].PBone_index = r.u16();
    this->bone[i].TBone_index = r.u16();
    this->bone[i].type = r.u8();
    this->bone[i].IKBone_index = r.u16();
    r.read(this->bone[i].loc, 12);
    this->bone[i].name_eng[0] = '\0';
    this->bone[i].name[21] = '\0';
  }

  uint16_t IK_count = r.u16();
  PLOG_DEBUG << "IKデータ数:" << IK_count;
  this->IK.resize(IK_count);
  for (int i = 0; i < this->IK.size(); i++) {
    this->IK[i].IKBone_index = r.u16();
    this->IK[i].IKTBone_index = r.u16();
    char IK_chain_len = r.u8();
    ;
    this->IK[i].iterations = r.u16();
    this->IK[i].weight = r.f32();
    this->IK[i].IK_chain.resize(IK_chain_len);
    if (IK_chain_len > 0) {
      r.read(this->IK[i].IK_chain.data(), 2 * IK_chain_len);
    }
  }

  uint16_t skin_count = r.u16();
  PLOG_DEBUG << "表情数:" << skin_count;
  this->skin.resize(skin_count);
  for (int i = 0; i < skin_count; i++) {
    r.read(this->skin[i].name, 20);
    int skin_vt_count = r.i32();
    this->skin[i].type = r.u8();
    this->skin[i].skin_vt.resize(skin_vt_count);
    for (int j = 0; j < skin_vt_count; j++) {
      this->skin[i].skin_vt[j].index = r.i32();
      if (this->skin[i].skin_vt[j].index > this->vt.size()) {
        exit(1);
      }
      r.read(this->skin[i].skin_vt[j].loc, 12);
    }
    this->skin[i].name_eng[0] = '\0';
    this->skin[i].name[20] = '\0';
  }

  uint8_t skin_disp_count = r.u8();
  PLOG_DEBUG << "表情枠:" << skin_disp_count;
  this->skin_disp.resize(skin_disp_count);
  r.read(this->skin_disp.data(), 2 * this->skin_disp.size());

  uint8_t bone_group_count = r.u8();
  PLOG_DEBUG << "ボーン枠:" << bone_group_count;
  this->bone_group.resize(bone_group_count);
  for (int i = 0; i < bone_group_count; i++) {
    r.read(&this->bone_group[i].name, 50);
    this->bone_group[i].name_eng[0] = '\0';
  }

  int bone_disp_count = r.i32();
  PLOG_DEBUG << "表示ボーン数:" << bone_disp_count;
  this->bone_disp.resize(bone_disp_count);
  for (int i = 0; i < bone_disp_count; i++) {
    this->bone_disp[i].index = r.u16();
    this->bone_disp[i].bone_group = r.u8();
  }

  this->eng_support = r.u8();

  if (r.isend()) {
    PLOG_DEBUG << "拡張部分なし";
    this->eng_support = 0;
    this->toon_path[0] = this->toon[0] = "toon01.bmp";
    this->toon_path[1] = this->toon[1] = "toon02.bmp";
    this->toon_path[2] = this->toon[2] = "toon03.bmp";
    this->toon_path[3] = this->toon[3] = "toon04.bmp";
    this->toon_path[4] = this->toon[4] = "toon05.bmp";
    this->toon_path[5] = this->toon[5] = "toon06.bmp";
    this->toon_path[6] = this->toon[6] = "toon07.bmp";
    this->toon_path[7] = this->toon[7] = "toon08.bmp";
    this->toon_path[8] = this->toon[8] = "toon09.bmp";
    this->toon_path[9] = this->toon[9] = "toon10.bmp";
    this->rbody.clear();
    this->joint.clear();
    return 0;
  }

  PLOG_DEBUG << "英名対応:" << (int)this->eng_support;

  if (this->eng_support == 1) {
    PLOG_DEBUG << "英名対応PMD";
    r.read(this->header.name_eng.data(), 20);
    this->header.name_eng[21] = '\0';

    r.read(this->header.comment_eng.data(), 256);
    this->header.comment_eng[255] = '\0';

    for (int i = 0; i < this->bone.size(); i++) {
      r.read(this->bone[i].name_eng, 20);
      this->bone[i].name_eng[20] = '\0';
    }

    // skin:0
    if (this->skin.size() > 0) {
      strcpy(this->skin[0].name_eng, "base");
    }
    // skin:1~
    for (int i = 1; i < this->skin.size(); i++) {
      r.read(this->skin[i].name_eng, 20);
      this->skin[i].name_eng[20] = '\0';
    }
    for (int i = 0; i < this->bone_group.size(); i++) {
      r.read(this->bone_group[i].name_eng, 50);
      this->bone_group[i].name_eng[50] = '\0';
    }
  } else {
    PLOG_DEBUG << "英名非対応PMD";

    this->header.name_eng[0] = '\0';
    this->header.comment_eng[0] = '\0';

    for (int i = 0; i < this->bone.size(); i++) {
      *this->bone[i].name_eng = '\0';
    }

    for (int i = 0; i < this->skin.size(); i++) {
      *this->skin[i].name_eng = '\0';
    }

    for (int i = 0; i < this->bone_group.size(); i++) {
      *this->bone_group[i].name_eng = '\0';
    }
  }

  for (int i = 0; i < 10; i++) {
    char buf[100];
    r.read(buf, 100);
    this->toon[i] = buf;
    auto str = file_name;
    auto char_p = str.rfind('/');
    if (char_p != std::string::npos) {
      str = str.substr(0, char_p + 1);
    } else {
      str = {};
    }
    this->toon_path[i] = (str + this->toon[i]);
  }

  int rbody_count = r.i32();
  PLOG_DEBUG << "剛体数:" << rbody_count;
  this->rbody.resize(rbody_count);
  for (int i = 0; i < this->rbody.size(); i++) {
    r.read(this->rbody[i].name, 20);
    this->rbody[i].bone = r.u16();
    this->rbody[i].group = r.u8();
    this->rbody[i].target = r.u16();
    this->rbody[i].shape = r.u8();
    r.read(this->rbody[i].size, 12);
    r.read(this->rbody[i].loc, 12);
    r.read(this->rbody[i].rot, 12);
    r.read(this->rbody[i].property, 20);
    this->rbody[i].type = r.u8();
    this->rbody[i].name[21] = '\0';
  }

  int joint_count = r.i32();
  PLOG_DEBUG << "ジョイント数:" << joint_count;
  this->joint.resize(joint_count);
  for (int i = 0; i < joint_count; i++) {
    r.read(this->joint[i].name, 20);
    r.read(this->joint[i].rbody, 8);
    r.read(this->joint[i].loc, 12);
    r.read(this->joint[i].rot, 12);
    r.read(this->joint[i].limit, 4 * 12);
    r.read(this->joint[i].spring, 4 * 6);
    this->joint[i].name[20] = '\0';
  }

  return true;
}

std::shared_ptr<MODEL> load_PMD(const std::string &file_name) {
  if (file_name.empty()) {
    PLOG_WARNING << "ファイル名がありません";
    return nullptr;
  }

  auto bytes = ioutil::readfile(file_name);
  if (bytes.empty()) {
    PLOG_ERROR << "Can't open file:" << file_name;
    return nullptr;
  }

  PLOG_DEBUG << file_name;
  auto model = MODEL::create();
  if (!model->load(bytes, file_name)) {
    return nullptr;
  }

  return model;
}

bool MODEL::write(const std::string &file_name) const {
  if (file_name.empty()) {
    printf("ファイル名がありません\n");
    return false;
  }

  auto pmd = fopen(file_name.c_str(), "wb");
  if (!pmd) {
    printf("ファイル %s を開けません\n", file_name.c_str());
    return false;
  }

  // ヘッダー書き換え
  this->header.magic = {'P', 'm', 'd', '\0'};
  this->header.version = 1.0;

  fwrite(this->header.magic.data(), 3, 1, pmd);
  fwrite(&this->header.version, 4, 1, pmd);
  fwrite(this->header.name.data(), 20, 1, pmd);
  fwrite(this->header.comment.data(), 256, 1, pmd);

  int vt_count = this->vt.size();
  fwrite(&vt_count, 4, 1, pmd);
  for (size_t i = 0; i < this->vt.size(); i++) {
    fwrite(this->vt[i].loc, 4, 3, pmd);
    fwrite(this->vt[i].nor, 4, 3, pmd);
    fwrite(this->vt[i].uv, 4, 2, pmd);
    fwrite(this->vt[i].bone_num, 2, 2, pmd);
    fwrite(&this->vt[i].bone_weight, 1, 1, pmd);
    fwrite(&this->vt[i].edge_flag, 1, 1, pmd);
  }

  int vt_index_count = this->vt_index.size();
  fwrite(&vt_index_count, 4, 1, pmd);
  for (size_t i = 0; i < this->vt_index.size(); i++) {
    if (this->vt_index[i] >= this->vt.size()) {
      printf("頂点インデックスが不正です :%d\n", this->vt_index[i]);
      return 1;
    }
    fwrite(&this->vt_index[i], 2, 1, pmd);
  }

  int mat_count = this->mat.size();
  fwrite(&mat_count, 4, 1, pmd);
  for (size_t i = 0; i < this->mat.size(); i++) {
    // 70bytes
    fwrite(this->mat[i].diffuse, 4, 3, pmd);
    fwrite(&this->mat[i].alpha, 4, 1, pmd);
    fwrite(&this->mat[i].spec, 4, 1, pmd);
    fwrite(this->mat[i].spec_col, 4, 3, pmd);
    fwrite(this->mat[i].mirror_col, 4, 3, pmd);
    fwrite(&this->mat[i].toon_index, 1, 1, pmd);
    fwrite(&this->mat[i].edge_flag, 1, 1, pmd);
    fwrite(&this->mat[i].vt_index_count, 4, 1, pmd);

    if (*this->mat[i].sph != '\0') {
      char str[PATH_LEN];
      sprintf(str, "%s*%s\0", this->mat[i].tex, this->mat[i].sph);
      if (strlen(str) > 20) {
        PLOGW << "not zero terminated";
        // ret = 2;
      }
      fwrite(str, 1, 20, pmd);
    } else {
      fwrite(this->mat[i].tex, 1, 20, pmd);
    }
  }

  uint16_t bone_count = this->bone.size();
  fwrite(&bone_count, 2, 1, pmd);
  for (size_t i = 0; i < this->bone.size(); i++) {
    fwrite(this->bone[i].name, 1, 20, pmd);
    fwrite(&this->bone[i].PBone_index, 2, 1, pmd);
    fwrite(&this->bone[i].TBone_index, 2, 1, pmd);
    fwrite(&this->bone[i].type, 1, 1, pmd);
    fwrite(&this->bone[i].IKBone_index, 2, 1, pmd);
    fwrite(this->bone[i].loc, 4, 3, pmd);
  }

  uint16_t IK_count = this->IK.size();
  fwrite(&IK_count, 2, 1, pmd);
  for (int i = 0; i < this->IK.size(); i++) {
    fwrite(&this->IK[i].IKBone_index, 2, 1, pmd);
    fwrite(&this->IK[i].IKTBone_index, 2, 1, pmd);
    uint8_t IK_chain_len = this->IK[i].IK_chain.size();
    fwrite(&IK_chain_len, 1, 1, pmd);
    fwrite(&this->IK[i].iterations, 2, 1, pmd);
    fwrite(&this->IK[i].weight, 4, 1, pmd);
    fwrite(this->IK[i].IK_chain.data(), 2, this->IK[i].IK_chain.size(), pmd);
  }
  PLOG_DEBUG << "IKリスト";

  uint16_t skin_count = this->skin.size();
  fwrite(&skin_count, 2, 1, pmd);
  for (size_t i = 0; i < this->skin.size(); i++) {
    fwrite(this->skin[i].name, 1, 20, pmd);
    int skin_vt_count = this->skin[i].skin_vt.size();
    fwrite(&skin_vt_count, 4, 1, pmd);
    fwrite(&this->skin[i].type, 1, 1, pmd);
    for (size_t j = 0; j < this->skin[i].skin_vt.size(); j++) {
      fwrite(&this->skin[i].skin_vt[j].index, 4, 1, pmd);
      fwrite(this->skin[i].skin_vt[j].loc, 4, 3, pmd);
    }
  }
  PLOG_DEBUG << "表情";

  uint8_t skin_disp_count = this->skin_disp.size();
  fwrite(&skin_disp_count, 1, 1, pmd);
  fwrite(this->skin_disp.data(), 2, this->skin_disp.size(), pmd);
  PLOG_DEBUG << "表情表示";

  uint8_t bone_group_count = this->bone_group.size();
  fwrite(&bone_group_count, 1, 1, pmd);
  for (int i = 0; i < this->bone_group.size(); i++) {
    fwrite(this->bone_group[i].name, 1, 50, pmd);
  }

  int bone_disp_count = this->bone_disp.size();
  fwrite(&bone_disp_count, 4, 1, pmd);
  for (int i = 0; i < this->bone_disp.size(); i++) {
    fwrite(&this->bone_disp[i].index, 2, 1, pmd);
    fwrite(&this->bone_disp[i].bone_group, 1, 1, pmd);
  }
  PLOG_DEBUG << "ボーン表示";

  // extension
  fwrite(&this->eng_support, 1, 1, pmd);

  if (this->eng_support == 1) {
    fwrite(this->header.name_eng.data(), 1, 20, pmd);
    fwrite(this->header.comment_eng.data(), 1, 256, pmd);
    for (size_t i = 0; i < this->bone.size(); i++) {
      fwrite(this->bone[i].name_eng, 1, 20, pmd);
    }
    for (size_t i = 1; i < this->skin.size(); i++) {
      fwrite(this->skin[i].name_eng, 1, 20, pmd);
    }
    for (size_t i = 0; i < this->bone_group.size(); i++) {
      fwrite(this->bone_group[i].name_eng, 1, 50, pmd);
    }
  }
  PLOG_DEBUG << "英名";

  for (int i = 0; i < 10; i++) {
    assert(this->toon[i].size() < 100);
    char buf[100] = {0};
    memcpy(buf, this->toon[i].data(), this->toon[i].size());
    fwrite(buf, 1, 100, pmd);
  }

  int rbody_count = this->rbody.size();
  fwrite(&rbody_count, 4, 1, pmd);
  for (int i = 0; i < this->rbody.size(); i++) {
    fwrite(this->rbody[i].name, 1, 20, pmd);
    fwrite(&this->rbody[i].bone, 2, 1, pmd);
    fwrite(&this->rbody[i].group, 1, 1, pmd);
    fwrite(&this->rbody[i].target, 2, 1, pmd);
    fwrite(&this->rbody[i].shape, 1, 1, pmd);
    fwrite(this->rbody[i].size, 4, 3, pmd);
    fwrite(this->rbody[i].loc, 4, 3, pmd);
    fwrite(this->rbody[i].rot, 4, 3, pmd);
    fwrite(this->rbody[i].property, 4, 5, pmd);
    fwrite(&this->rbody[i].type, 1, 1, pmd);
  }
  PLOG_DEBUG << "剛体";

  int joint_count;
  fwrite(&joint_count, 4, 1, pmd);
  for (int i = 0; i < this->joint.size(); i++) {
    fwrite(this->joint[i].name, 1, 20, pmd);
    fwrite(this->joint[i].rbody, 4, 2, pmd);
    fwrite(this->joint[i].loc, 4, 3, pmd);
    fwrite(this->joint[i].rot, 4, 3, pmd);
    fwrite(this->joint[i].limit, 4, 12, pmd);
    fwrite(this->joint[i].spring, 4, 6, pmd);
  }
  PLOG_DEBUG << "ジョイント";

  fclose(pmd);
  PLOG_INFO << file_name << "へ出力しました。";

  return true;
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

  fprintf(txt, "%s \n %f \n %s \n %s \n", model->header.magic.data(),
          model->header.version, model->header.name.data(),
          model->header.comment.data());

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
    fprintf(txt, "%s\n", model->header.name_eng.data());
    fprintf(txt, "%s\n", model->header.comment_eng.data());
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
    fprintf(txt, "%s\n", model->toon[i].c_str());
  }

  fprintf(txt, "剛体数:%zu\n", model->rbody.size());
  for (int i = 0; i < model->rbody.size(); i++) {
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

  fprintf(txt, "ジョイント数:%zu\n", model->joint.size());
  for (int i = 0; i < model->joint.size(); i++) {
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

  out->rbody = model->rbody;
  out->joint = model->joint;

  return 0;
}

bool MODEL::add_PMD(const std::shared_ptr<MODEL> &add) {
  // 頂点
  std::vector<VERTEX> vt(this->vt.size() + add->vt.size());
  for (size_t i = 0; i < this->vt.size(); i++) {
    vt[i] = this->vt[i];
  }
  size_t j = 0;
  for (size_t i = this->vt.size(); i < vt.size(); i++) {
    vt[i] = add->vt[j];
    for (size_t k = 0; k < 2; k++) {
      vt[i].bone_num[k] += this->bone.size();
    }
    j++;
  }

  // 面頂点
  std::vector<unsigned short> vt_index(this->vt_index.size() +
                                       add->vt_index.size());
  for (size_t i = 0; i < this->vt_index.size(); i++) {
    vt_index[i] = this->vt_index[i];
  }
  j = 0;
  for (size_t i = this->vt_index.size(); i < vt_index.size(); i++) {
    vt_index[i] = add->vt_index[j] + this->vt.size();
    j++;
  }

  // 材質
  std::vector<MATERIAL> mat(this->mat.size() + add->mat.size());
  for (size_t i = 0; i < this->mat.size(); i++) {
    mat[i] = this->mat[i];
  }
  j = 0;
  for (size_t i = this->mat.size(); i < mat.size(); i++) {
    mat[i] = add->mat[j];
    j++;
  }

  // ボーン
  std::vector<BONE> bone(this->bone.size() + add->bone.size());
  for (size_t i = 0; i < this->bone.size(); i++) {
    bone[i] = this->bone[i];
  }
  j = 0;
  for (size_t i = this->bone.size(); i < bone.size(); i++) {
    bone[i] = add->bone[j];
    if (bone[i].PBone_index != USHORT_MAX)
      bone[i].PBone_index = bone[i].PBone_index + this->bone.size();
    if (bone[i].TBone_index != 0)
      bone[i].TBone_index = bone[i].TBone_index + this->bone.size();
    if (bone[i].IKBone_index != 0)
      bone[i].IKBone_index = bone[i].IKBone_index + this->bone.size();
    j++;
  }

  // IKリスト
  std::vector<IK_LIST> IK(this->IK.size() + add->IK.size());
  for (int i = 0; i < this->IK.size(); i++) {
    IK[i] = this->IK[i];
  }
  j = 0;
  for (size_t i = this->IK.size(); i < IK.size(); i++) {
    IK[i] = add->IK[j];
    IK[i].IKBone_index = IK[i].IKBone_index + this->bone.size();
    IK[i].IKTBone_index = IK[i].IKTBone_index + this->bone.size();
    for (size_t k = 0; k < IK[i].IK_chain.size(); k++) {
      IK[i].IK_chain[k] = IK[i].IK_chain[k] + this->bone.size();
    }
    j++;
  }

  // 表情
  std::vector<SKIN> skin(this->skin.size() + add->skin.size());
  if (add->skin.size() == 0) {
    for (size_t i = 0; i < skin.size(); i++) {
      skin[i] = this->skin[i];
    }
  } else if (this->skin.size() == 0) {
    for (size_t i = 0; i < skin.size(); i++) {
      skin[i] = add->skin[i];
    }
  } else if (this->skin.size() != 0 && add->skin.size() != 0) {
    skin.pop_back();
    skin[0] = this->skin[0];
    skin[0].skin_vt.resize(this->skin[0].skin_vt.size() +
                           add->skin[0].skin_vt.size());
    auto tmp = this->skin[0].skin_vt.size();
    memcpy(skin[0].skin_vt.data(), this->skin[0].skin_vt.data(),
           tmp * sizeof(SKIN_DATA));
    memcpy(&skin[0].skin_vt[tmp], add->skin[0].skin_vt.data(),
           add->skin[0].skin_vt.size() * sizeof(SKIN_DATA));
    // baseの合成

    for (size_t i = 0; i < this->skin[0].skin_vt.size(); i++) {
      skin[0].skin_vt[i].index = this->skin[0].skin_vt[i].index;
    }
    // printf("%d %d %d\n", skin[0].skin_vt_count, this->skin[0].skin_vt_count,
    // add->skin[0].skin_vt_count);
    j = 0;
    for (size_t i = this->skin[0].skin_vt.size(); i < skin[0].skin_vt.size();
         i++) {
      // printf("%d \n", i);
      skin[0].skin_vt[i].index =
          add->skin[0].skin_vt[j].index + this->vt.size();
      j++;
    }
    // 表情追加
    for (size_t i = 1; i < this->skin.size(); i++) {
      skin[i] = this->skin[i];
      // printf("%d %d \n", i, size);
    }
    j = 1;
    for (size_t i = this->skin.size(); i < skin.size(); i++) {
      // printf("%d\n", j);
      skin[i] = add->skin[j];
      for (size_t k = 0; k < skin[i].skin_vt.size(); k++) {
        skin[i].skin_vt[k].index =
            skin[i].skin_vt[k].index + this->skin[0].skin_vt.size();
      }
      j++;
    }
  }

  // 表情表示
  std::vector<unsigned short> skin_disp(this->skin_disp.size() +
                                        add->skin_disp.size());
  memcpy(skin_disp.data(), this->skin_disp.data(),
         this->skin_disp.size() * sizeof(unsigned short));
  j = 0;
  for (int i = this->skin_disp.size(); i < skin_disp.size(); i++) {
    skin_disp[i] = add->skin_disp[j] + this->skin_disp.size();
    j++;
  }

  // ボーン表示
  std::vector<BONE_GROUP> bone_group(this->bone_group.size() +
                                     add->bone_group.size());
  for (int i = 0; i < this->bone_group.size(); i++) {
    bone_group[i] = this->bone_group[i];
  }
  j = 0;
  for (int i = this->bone_group.size(); i < bone_group.size(); i++) {
    bone_group[i] = add->bone_group[j];
    j++;
  }

  std::vector<BONE_DISP> bone_disp(this->bone_disp.size() +
                                   add->bone_disp.size());
  for (int i = 0; i < this->bone_disp.size(); i++) {
    bone_disp[i] = this->bone_disp[i];
  }
  j = 0;
  for (size_t i = this->bone_disp.size(); i < bone_disp.size(); i++) {
    bone_disp[i].index = add->bone_disp[j].index + this->bone.size();
    bone_disp[i].bone_group =
        add->bone_disp[j].bone_group + this->bone_group.size();
    j++;
  }

  // 英名
  this->eng_support = add->eng_support;

  // 剛体
  std::vector<RIGID_BODY> rbody(this->rbody.size() + add->rbody.size());
  for (int i = 0; i < this->rbody.size(); i++) {
    rbody[i] = this->rbody[i];
  }
  j = 0;
  for (size_t i = this->rbody.size(); i < rbody.size(); i++) {
    rbody[i] = add->rbody[j];
    rbody[i].bone = rbody[i].bone + this->bone.size();
    j++;
  }

  // ジョイント
  std::vector<JOINT> joint(this->joint.size() + add->joint.size());
  for (int i = 0; i < this->joint.size(); i++) {
    joint[i] = this->joint[i];
  }
  j = 0;
  for (size_t i = this->joint.size(); i < joint.size(); i++) {
    joint[i] = add->joint[j];
    for (size_t k = 0; k < 2; k++) {
      joint[i].rbody[k] = joint[i].rbody[k] + this->rbody.size();
    }
    j++;
  }

  std::swap(this->vt, vt);
  std::swap(this->vt_index, vt_index);
  std::swap(this->mat, mat);
  std::swap(this->bone, bone);
  std::swap(this->IK, IK);
  std::swap(this->skin, skin);
  std::swap(this->skin_disp, skin_disp);
  std::swap(this->bone_group, bone_group);
  std::swap(this->bone_disp, bone_disp);
  std::swap(this->rbody, rbody);
  std::swap(this->joint, joint);

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

  fprintf(txt, "%s \n %f \n %s \n %s \n", model->header.magic.data(),
          model->header.version, model->header.name.data(),
          model->header.comment.data());

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
