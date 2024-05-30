#define _USE_MATH_DEFINES
#include <math.h>

#include "ioutil.h"
#include "pmd_model.h"
#include <plog/Log.h>
#include <string.h>

static double angle_from_vec(double u, double v) {
  double angle;
  double pi = M_PI;
  // ベクトルがv軸方向を向く回転を求める

  angle = asin(u / sqrt(u * u + v * v));
  // printf("angle %f\n", angle);
  if (v < 0) {
    angle = pi - angle;
  }

  return angle;
}

static void coordtrans(double array[][3], unsigned int len, double loc[],
                       double mtr[3][3]) {
  /*配列は大きさ[len][3]の2次元配列で、点の座標が格納されている
   */
  int i, j, k;
  double tmp[3];

  // 座標変換
  for (i = 0; i < len; i++) {
    if (&loc != 0) {
      for (j = 0; j < 3; j++) {
        tmp[j] = array[i][j] - loc[j];
      }
    }
    for (j = 0; j < 3; j++) {
      array[i][j] = 0;
      for (k = 0; k < 3; k++) {
        array[i][j] = array[i][j] + mtr[j][k] * tmp[k];
      }
    }
  }
}

static void coordtrans_inv(double array[][3], unsigned int len, double loc[],
                           double mtr[3][3]) {
  /*配列は大きさ[len][3]の2次元配列で、点の座標が格納されている
   */
  int i, j, k;
  double tmp[3];
  double inverse_mtr[3][3];

  // 転置行列
  for (i = 0; i < 3; i++) {
    for (j = 0; j < 3; j++) {
      inverse_mtr[i][j] = mtr[j][i];
    }
  }

  // 座標変換
  for (i = 0; i < len; i++) {
    for (j = 0; j < 3; j++) {
      tmp[j] = 0;
      for (k = 0; k < 3; k++) {
        tmp[j] = tmp[j] + inverse_mtr[j][k] * array[i][k];
      }
    }

    if (&loc != 0) {
      for (j = 0; j < 3; j++) {
        array[i][j] = tmp[j] + loc[j];
      }
    }
  }
}
static void *MALLOC(size_t s) {
  auto p = malloc(s);
  if (p == NULL) {
    PLOG_ERROR << "メモリの確保に失敗しました";
    throw std::runtime_error("メモリの確保に失敗しました");
  }

  return p;
}

static void FREE(void *p) {
  if (p == NULL)
    return;
  free(p);
}

MODEL::MODEL() {}

MODEL::~MODEL() {}

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

std::shared_ptr<MODEL> MODEL::load(const std::string &file_name) {
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
  auto pre_vt_size = this->vt.size();
  auto pre_bone_size = this->bone.size();
  auto pre_skin_disp_size = this->skin_disp.size();
  auto pre_bone_group_size = this->bone_group.size();
  auto pre_rbody_size = this->rbody.size();

  // 頂点
  this->vt.reserve(this->vt.size() + add->vt.size());
  for (auto &v : add->vt) {
    vt.push_back(v);
    // fix bone index
    vt.back().bone_num[0] += pre_bone_size;
    vt.back().bone_num[1] += pre_bone_size;
  }

  // 面頂点
  this->vt_index.reserve(this->vt_index.size() + add->vt_index.size());
  for (auto index : add->vt_index) {
    // fix index
    vt_index.push_back(index + pre_vt_size);
  }

  // 材質
  this->mat.reserve(this->mat.size() + add->mat.size());
  for (auto &m : add->mat) {
    mat.push_back(m);
  }

  // ボーン
  this->bone.reserve(this->bone.size() + add->bone.size());
  for (auto &b : add->bone) {
    bone.push_back(b);
    // fix bone index
    if (bone.back().PBone_index != USHORT_MAX)
      bone.back().PBone_index += pre_bone_size;
    if (bone.back().TBone_index != 0)
      bone.back().TBone_index += pre_bone_size;
    if (bone.back().IKBone_index != 0)
      bone.back().IKBone_index += pre_bone_size;
  }

  // IKリスト
  this->IK.reserve(this->IK.size() + add->IK.size());
  for (auto &ik : add->IK) {
    IK.push_back(ik);
    IK.back().IKBone_index += pre_bone_size;
    IK.back().IKTBone_index += pre_bone_size;
    for (size_t k = 0; k < IK.back().IK_chain.size(); k++) {
      IK.back().IK_chain[k] += pre_bone_size;
    }
  }

  // 表情
  if (add->skin.size() == 0) {
    // nothing
  } else if (this->skin.size() == 0) {
    // copy
    this->skin.assign(add->skin.begin(), add->skin.end());
  } else if (this->skin.size() != 0 && add->skin.size() != 0) {
    // 0番を合成
    skin[0].skin_vt.reserve(this->skin[0].skin_vt.size() +
                            add->skin[0].skin_vt.size());
    for (auto &skin_vt : add->skin[0].skin_vt) {
      this->skin[0].skin_vt.push_back(skin_vt);
      // index 補正
      this->skin[0].skin_vt.back().index += pre_vt_size;
    }

    // 1以降追加
    this->skin.reserve(this->skin.size() + add->skin.size() - 1);
    for (size_t i = 1; i < add->skin.size(); i++) {
      skin.push_back(add->skin[i]);
      for (size_t k = 0; k < skin.back().skin_vt.size(); k++) {
        // index 補正
        skin.back().skin_vt[k].index += pre_vt_size;
      }
    }
  }

  // 表情表示
  skin_disp.reserve(this->skin_disp.size() + add->skin_disp.size());
  for (auto &sd : add->skin_disp) {
    skin_disp.push_back(sd + pre_skin_disp_size);
  }

  // ボーン表示
  bone_group.reserve(this->bone_group.size() + add->bone_group.size());
  for (auto &bg : add->bone_group) {
    bone_group.push_back(bg);
  }
  bone_disp.reserve(this->bone_disp.size() + add->bone_disp.size());
  for (auto &bd : add->bone_disp) {
    bone_disp.push_back(bd);
    bone_disp.back().index += pre_bone_size;
    bone_disp.back().bone_group += pre_bone_group_size;
  }

  // 英名
  this->eng_support = add->eng_support;

  // 剛体
  rbody.reserve(this->rbody.size() + add->rbody.size());
  for (auto &rb : add->rbody) {
    rbody.push_back(rb);
    rbody.back().bone += pre_bone_group_size;
  }

  // ジョイント
  joint.reserve(this->joint.size() + add->joint.size());
  for (auto &j : add->joint) {
    joint.push_back(j);
    joint.back().rbody[0] += pre_rbody_size;
    joint.back().rbody[1] += pre_rbody_size;
  }

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

void MODEL::translate(NameList *list, short mode) {
  /*
  モード1 英名追加
  モード2 日本語名を英語名に(ボーン、スキンのみ)
  モード3 英語名を日本語名に(ボーン、スキンのみ)
  */

  if (mode == 1) {

    if (this->eng_support != 1) {
      this->eng_support = 1;
      this->header.name_eng = this->header.name;
      this->header.comment_eng = this->header.comment;
    }

    for (int i = 0; i < this->bone.size(); i++) {
      int j = 0;
      for (; j < list->bone.size(); j++) {
        if (strcmp(this->bone[i].name, list->bone[j].data()) == 0) {
          strncpy(this->bone[i].name_eng, list->bone_eng[j].data(), NAME_LEN);
          j = -1;
          break;
        }
      }
      if (j != -1) {
        if (this->bone[i].name[0] == '\0') {
          strncpy(this->bone[i].name_eng, this->bone[i].name, NAME_LEN);
        }
      }
    }

    for (int i = 1; i < this->skin.size(); i++) {
      int j = 1;
      for (; j < list->skin.size(); j++) {
        if (strcmp(this->skin[i].name, list->skin[j].data()) == 0) {
          strncpy(this->skin[i].name_eng, list->skin_eng[j].data(), NAME_LEN);
          j = -1;
          break;
        }
      }
      if (j != -1) {
        strncpy(this->skin[i].name_eng, this->skin[i].name, NAME_LEN);
      }
    }

    for (int i = 0; i < this->bone_group.size(); i++) {
      char str[NAME_LEN];
      strncpy(str, this->bone_group[i].name, NAME_LEN);
      auto p = strchr(str, '\n');
      if (p != NULL)
        *p = '\0';

      int j = 0;
      for (; j < list->disp.size(); j++) {
        if (strcmp(str, list->disp[j].data()) == 0) {
          strncpy(this->bone_group[i].name_eng, list->disp_eng[j].data(),
                  NAME_LEN);
          j = -1;
          break;
        }
      }
#ifdef DEBUG
      printf("%d ", i);
#endif
      if (j != -1) {
        strncpy(this->bone_group[i].name_eng, str, NAME_LEN);
      }
    }

#ifdef DEBUG
    printf("\nbone表示枠\n");
#endif

  } else if (mode == 2) {
    for (int i = 0; i < this->bone.size(); i++) {
      int j = 0;
      for (; j < list->bone.size(); j++) {
        if (strcmp(this->bone[i].name, list->bone[j].data()) == 0) {
          strncpy(this->bone[i].name, list->bone_eng[j].data(), NAME_LEN);
          j = -1;
          break;
        }
      }
      if (j != -1 && this->eng_support == 1) {
        strncpy(this->bone[i].name, this->bone[i].name_eng, NAME_LEN);
      }
    }
    for (int i = 0; i < this->skin.size(); i++) {
      int j = 0;
      for (; j < list->skin.size(); j++) {
        if (strcmp(this->skin[i].name, list->skin[j].data()) == 0) {
          strncpy(this->skin[i].name, list->skin_eng[j].data(), NAME_LEN);
          j = -1;
          break;
        }
      }
      if (j != -1 && this->eng_support == 1) {
        strncpy(this->skin[i].name, this->skin[i].name_eng, NAME_LEN);
      }
    }
  } else if (mode == 3) {
    for (int i = 0; i < this->bone.size(); i++) {
      ;
      for (int j = 0; j < list->bone.size(); j++) {
        if (strcmp(this->bone[i].name, list->bone_eng[j].data()) == 0) {
          strncpy(this->bone[i].name, list->bone[j].data(), NAME_LEN);
          break;
        }
      }
    }
    for (int i = 0; i < this->skin.size(); i++) {
      for (int j = 0; j < list->skin.size(); j++) {
        if (strcmp(this->skin[i].name, list->skin_eng[j].data()) == 0) {
          strncpy(this->skin[i].name, list->skin[j].data(), NAME_LEN);
          break;
        }
      }
    }
  }
}

void MODEL::sort_bone(NameList *list) {
  std::vector<int> index(this->bone.size());
  std::vector<BONE> bone(this->bone.size());

  for (int i = 0; i < this->bone.size(); i++) {
    index[i] = -1; // リストに無いボーンには-1
    for (int j = 0; j < list->bone.size(); j++) {
      if (strcmp(list->bone[j].data(), this->bone[i].name) == 0) {
        index[i] = j; // indexにリスト中の番号を代入
        break;
      }
    }
  }

  int tmp = 0;
  for (int i = 0; i < list->bone.size(); i++) {
    int j = 0;
    for (; j < this->bone.size(); j++) {
      if (index[j] == i) { // indexにiが存在したら
        // printf("index[%d]に%dが存在します\n", j, i);
        index[j] = index[j] - tmp;
        j = -1;
        break;
      }
    }
    if (j != -1) {
      tmp++;
    }
  }
  tmp = -1;
  for (int i = 0; i < this->bone.size(); i++) {
    if (tmp < index[i]) {
      tmp = index[i]; // indexの最大値を見つける
    }
  }
  tmp++;
  for (int i = 0; i < this->bone.size(); i++) {
    if (strcmp(this->bone[i].name, "-0") == 0) {
      index[i] = this->bone.size() - 1;
    } else if (index[i] == -1) {
      index[i] = tmp;
      tmp++;
    }
  }

  // 親子関係修正

  {
    for (int i = 0; i < this->bone.size(); i++) {
      if (this->bone[i].PBone_index != 65535 &&
          index[this->bone[i].PBone_index] > index[i] &&
          strcmp(this->bone[i].name, "-0") != 0) {

        tmp = index[this->bone[i].PBone_index];
        int tmp_PBone_index = index[i];
        for (int j = 0; j < this->bone.size(); j++) {
          if (index[j] >= tmp_PBone_index && index[j] < tmp) {
            index[j]++; // 一つ後ろにずらす
          }
        }
        index[this->bone[i].PBone_index] =
            tmp_PBone_index; // ボーンの一つ前に親ボーンを移動
      }
    }
  }

  for (int i = 0; i < this->bone.size(); i++) { // ボーン並び変え
#ifdef DEBUG
    printf("index[%d]=%d\n", i, index[i]);
#endif
    strcpy(bone[index[i]].name, this->bone[i].name);
    strcpy(bone[index[i]].name_eng, this->bone[i].name_eng);
    if (this->bone[i].PBone_index == 65535) {
      bone[index[i]].PBone_index = 65535;
    } else {
      bone[index[i]].PBone_index = index[this->bone[i].PBone_index];
    }
    if (this->bone[i].TBone_index == 0) {
      bone[index[i]].TBone_index = 0;
    } else {
      bone[index[i]].TBone_index = index[this->bone[i].TBone_index];
    }

    bone[index[i]].type = this->bone[i].type;

    if (this->bone[i].IKBone_index == 0) {
      bone[index[i]].IKBone_index = 0;
    } else {
      bone[index[i]].IKBone_index = index[this->bone[i].IKBone_index];
    }
    for (int j = 0; j < 3; j++) {
      bone[index[i]].loc[j] = this->bone[i].loc[j];
    }
  }

  this->update_bone_index(index);

  std::swap(this->bone, bone);

  if (strcmp(this->bone[this->bone.size() - 1].name, "-0") == 0) {
    this->bone.pop_back();
  }
}

void MODEL::update_bone_index(std::span<int> index) {
  // 頂点のボーン番号を書き換え
  {
    std::vector<std::array<unsigned short, 2>> tmp_vt(this->vt.size());
    for (int i = 0; i < this->vt.size(); i++) {
      for (int j = 0; j < 2; j++) {
        tmp_vt[i][j] = this->vt[i].bone_num[j];
      }
    }
    for (int i = 0; i < this->vt.size(); i++) {
      for (int j = 0; j < 2; j++) {
        this->vt[i].bone_num[j] = index[tmp_vt[i][j]];
      }
    }
  }

  // IKリストのボーン番号を書き換え
  std::vector<IK_LIST> tmp_ik = this->IK;
  for (int i = 0; i < this->IK.size(); i++) {
    // PLOG_DEBUG << i;
    this->IK[i].IKBone_index = index[tmp_ik[i].IKBone_index];
    this->IK[i].IKTBone_index = index[tmp_ik[i].IKTBone_index];
    for (int j = 0; j < tmp_ik[i].IK_chain.size(); j++) {
      this->IK[i].IK_chain[j] = index[tmp_ik[i].IK_chain[j]];
    }
  }

  // 表示ボーン番号を書き換え
  auto tmp_disp = this->bone_disp;
  for (int i = 0; i < this->bone_disp.size(); i++) {
    this->bone_disp[i].index = index[tmp_disp[i].index];
  }

  // 剛体ボーン番号を書き換え
  std::vector<unsigned short> tmp_rb(this->rbody.size());
  for (int i = 0; i < this->rbody.size(); i++) {
    tmp_rb[i] = this->rbody[i].bone;
  }
  for (int i = 0; i < this->rbody.size(); i++) {
    if (tmp_rb[i] == USHORT_MAX) {
      this->rbody[i].bone = USHORT_MAX;
    } else {
      this->rbody[i].bone = index[tmp_rb[i]];
    }
  }

  PLOG_DEBUG << "ボーンインデックス更新完了";
}

void MODEL::sort_skin(NameList *list) {

  std::vector<int> index(this->skin.size());
  std::vector<SKIN> skin(this->skin.size());

  for (int i = 0; i < this->skin.size(); i++) {
    index[i] = -1; // リストに無い表情には-1
    for (int j = 0; j < list->skin.size(); j++) {
      if (strcmp(list->skin[j].data(), this->skin[i].name) == 0) {
        index[i] = j; // indexにリスト中の番号を代入
        break;
      }
    }
    // PLOG_DEBUG << "index[" << i << "]=" << index[i];
  }

  int tmp = 0;
  for (int i = 0; i < list->skin.size(); i++) {
    int j = 0;
    for (; j < this->skin.size(); j++) {
      if (index[j] == i) { // indexにiが存在したら
        // printf("index[%d]に%dが存在します\n", j, i);
        index[j] = index[j] - tmp;
        j = -1;
        break;
      }
    }
    if (j != -1) {
      tmp++;
    }
  }
  tmp = -1;
  for (int i = 0; i < this->skin.size(); i++) {
    if (tmp < index[i]) {
      tmp = index[i]; // indexの最大値を見つける
    }
  }
  tmp++;
  for (int i = 0; i < this->skin.size(); i++) {
    if (index[i] == -1) {
      index[i] = tmp;
      tmp++;
    }
  }

  for (int i = 0; i < this->skin.size(); i++) { // 表情並び変え
    // PLOG_DEBUG << "index[" << i << "]=" << index[i];
    skin[index[i]] = this->skin[i];
  }

  for (int i = 0; i < this->skin_disp.size(); i++) { // 表情並び変え
    this->skin_disp[i] = i + 1;
  }

  std::swap(this->skin, skin);
}

void MODEL::sort_disp(NameList *list) {
  std::vector<int> index(this->bone_group.size());
  std::vector<BONE_GROUP> bone_group(this->bone_group.size());
  std::vector<BONE_DISP> bone_disp(this->bone_disp.size());

  for (int i = 0; i < this->bone_group.size(); i++) {
    index[i] = -1; // リストに無い枠には-1
    auto tmpg = this->bone_group[i];
    auto p = strchr(tmpg.name, '\n');
    if (p != NULL)
      *p = '\0';
    for (int j = 0; j < list->disp.size(); j++) {
      if (strcmp(list->disp[j].data(), tmpg.name) == 0) {
        index[i] = j; // indexにリスト中の番号を代入
        break;
      }
    }
  }

  int tmp = 0;
  for (int i = 0; i < list->disp.size(); i++) {
    int j = 0;
    for (; j < this->bone_group.size(); j++) {
      if (index[j] == i) { // indexにiが存在したら
        // printf("index[%d]に%dが存在します\n", j, i);
        index[j] = index[j] - tmp;
        j = -1;
        break;
      }
    }
    if (j != -1) {
      tmp++;
    }
  }
  tmp = -1;
  for (int i = 0; i < this->bone_group.size(); i++) {
    if (tmp < index[i]) {
      tmp = index[i]; // indexの最大値を見つける
    }
  }
  tmp++;
  for (int i = 0; i < this->bone_group.size(); i++) {
    if (index[i] == -1) {
      index[i] = tmp;
      tmp++;
    }
  }

  for (int i = 0; i < this->bone_group.size(); i++) { // 表示枠並び変え
    bone_group[index[i]] = this->bone_group[i];
  }

  for (int i = 0; i < this->bone_group.size(); i++) { // 表示枠コピー
    this->bone_group[i] = bone_group[i];
  }

  for (int i = 0; i < this->bone_disp.size(); i++) { // 表示ボーン並び変え
    this->bone_disp[i].bone_group =
        index[this->bone_disp[i].bone_group - 1] + 1;
  }

  tmp = 0;
  for (int i = 1; i <= this->bone_group.size(); i++) {
    for (int j = 0; j < this->bone_disp.size(); j++) {
      if (this->bone_disp[j].bone_group == i) {
        bone_disp[tmp] = this->bone_disp[j];
        tmp++;
      }
    }
  }

  std::swap(this->bone_disp, bone_disp);
}

void MODEL::rename_tail() {
  // 全てのbone tailに"-0"の名前をつける
  for (int i = 0; i < this->bone.size(); i++) {
    if (this->bone[i].type == 6 || this->bone[i].type == 7) {
      int flag = 0;
      for (int j = 0; j < this->bone.size(); j++) {
        if (this->bone[j].TBone_index == i) {
          flag = 1;
          break;
        }
      }
      if (flag == 1) {
        strncpy(this->bone[i].name, "-0", 4);
        strncpy(this->bone[i].name_eng, "-0", 4);
      }
    }
  }

  // 子ボーンがtailならば+親ボーン名という名前にする
  for (int i = 0; i < this->bone.size(); i++) {
    int tmp = this->bone[i].TBone_index;
    if (tmp < this->bone.size()) {
      if (this->bone[tmp].type == 6 || this->bone[tmp].type == 7) {
        sprintf(this->bone[tmp].name, "+%s", this->bone[i].name);
        sprintf(this->bone[tmp].name_eng, "+%s", this->bone[i].name_eng);
        // printf("%s\n", this->bone[tmp].name);
      }
    } else {
      printf("範囲外のボーンインデックスを見つけました\n");
    }
  }
}

bool MODEL::scale_bone(int index, double sx, double sy, double sz) {
  int i, j, k, l;
  double vec[3];
  double vec_size;
  double nor_vec[3];
  double mtr[3][3];
  double mtrz[3][3];
  double mtrx[3][3];
  double loc[3] = {0.0, 0.0, 0.0};
  double rot[3]; // ZXY
  double theta;

  double tmp[3];

  double(*tmp_vt)[3];
  unsigned int len_vt;
  unsigned int *index_vt;

  double(*tmp_bone)[3];
  unsigned int len_bone;
  unsigned int *index_bone;
  double(*diff_bone)[3];

  // ベクトルがY軸に沿う向きになるようにする
  if (!this->bone_vec(index, loc, vec)) {
    return false;
  }

  // ベクトルのノーマライズ
  vec_size = 0.0;
  for (i = 0; i < 3; i++) {
    vec_size = vec_size + vec[i] * vec[i];
  }
  vec_size = sqrt(vec_size);
  for (i = 0; i < 3; i++) {
    nor_vec[i] = vec[i] / vec_size;
  }

  // ベクトルのZXY角を求める
  rot[0] = angle_from_vec(vec[0], vec[1]);
  rot[1] = angle_from_vec(vec[2], sqrt(vec[0] * vec[0] + vec[1] * vec[1]));
  rot[2] = 0;

  // printf("%f %f %f\n", rot[0], rot[1], rot[2]);

  // 行列初期化
  memset(mtr, 0, 9 * sizeof(double));
  memset(mtrz, 0, 9 * sizeof(double));
  memset(mtrx, 0, 9 * sizeof(double));

  // 回転行列を求める
  // Z軸
  theta = rot[0];
  mtrz[0][0] = cos(theta);
  mtrz[1][0] = sin(theta);
  mtrz[0][1] = -sin(theta);
  mtrz[1][1] = cos(theta);
  mtrz[2][2] = 1;

  // X軸
  theta = rot[1];
  mtrx[0][0] = 1;
  mtrx[1][1] = cos(theta);
  mtrx[1][2] = sin(theta);
  mtrx[2][1] = -sin(theta);
  mtrx[2][2] = cos(theta);

  // 合成
  for (i = 0; i < 3; i++) {
    for (j = 0; j < 3; j++) {
      for (k = 0; k < 3; k++) {
        mtr[i][j] = mtr[i][j] + mtrx[i][k] * mtrz[k][j];
      }
    }
  }
  /*
  printf("\n");
  for(i=0; i<3; i++){
          for(j=0; j<3; j++){
                  printf("%f ", mtr[i][j]);
          }
          printf("\n");
  }
  printf("\n");
  */
  // 座標変換
  // 変換する頂点をtmp_vtに格納
  len_vt = 0;
  for (i = 0; i < (this->vt.size()); i++) {
    if (this->vt[i].bone_num[0] == index || this->vt[i].bone_num[1] == index) {
      len_vt++;
    }
  }
  tmp_vt = (double(*)[3])MALLOC(sizeof(double) * len_vt * 3);
  index_vt = (unsigned int *)MALLOC(sizeof(unsigned int) * len_vt);
  j = 0;
  for (i = 0; i < this->vt.size(); i++) {
    if (this->vt[i].bone_num[0] == index || this->vt[i].bone_num[1] == index) {
      index_vt[j] = i;
      for (k = 0; k < 3; k++) {
        tmp_vt[j][k] = this->vt[i].loc[k];
      }
      j++;
    }
  }
  // 変換するボーンの子をtmp_boneに格納
  len_bone = 0;
  for (i = 0; i < (this->bone.size()); i++) {
    if (this->bone[i].PBone_index == index) {
      len_bone++;
    }
  }
  tmp_bone = (double(*)[3])MALLOC(sizeof(double) * len_bone * 3);
  diff_bone = (double(*)[3])MALLOC(sizeof(double) * len_bone * 3);
  index_bone = (unsigned int *)MALLOC(sizeof(unsigned int) * len_bone);
  j = 0;
  for (i = 0; i < this->bone.size(); i++) {
    if (this->bone[i].PBone_index == index) {
      index_bone[j] = i;
      for (k = 0; k < 3; k++) {
        tmp_bone[j][k] = this->bone[i].loc[k];
        diff_bone[j][k] = tmp_bone[j][k];
      }
      j++;
    }
  }
  // 変換
  coordtrans(tmp_vt, len_vt, loc, mtr);
  coordtrans(tmp_bone, len_bone, loc, mtr);

  // 変形
  for (i = 0; i < len_vt; i++) {
    tmp_vt[i][0] = sx * tmp_vt[i][0];
    tmp_vt[i][1] = sy * tmp_vt[i][1];
    tmp_vt[i][2] = sz * tmp_vt[i][2];
  }
  for (i = 0; i < len_bone; i++) {
    tmp_bone[i][0] = sx * tmp_bone[i][0];
    tmp_bone[i][1] = sy * tmp_bone[i][1];
    tmp_bone[i][2] = sz * tmp_bone[i][2];
  }
  // 逆変換
  coordtrans_inv(tmp_vt, len_vt, loc, mtr);
  coordtrans_inv(tmp_bone, len_bone, loc, mtr);

  // 変換結果を元のデータに書き込む
  // 頂点
  for (i = 0; i < len_vt; i++) {
    k = index_vt[i];
    tmp[0] = 0.0;
    if (this->vt[k].bone_num[0] == index) {
      tmp[0] += (double)this->vt[k].bone_weight / 100;
    }
    if (this->vt[k].bone_num[1] == index) {
      tmp[0] += 1.0 - (double)this->vt[k].bone_weight / 100;
    }
    // printf("%f %f\n", tmp[0], tmp[1]);

    tmp[1] = 1 - tmp[0];
    for (j = 0; j < 3; j++) {
      this->vt[k].loc[j] = this->vt[k].loc[j] * tmp[1] + tmp_vt[i][j] * tmp[0];
    }
  }

  // ボーン
  for (i = 0; i < len_bone; i++) {
    for (j = 0; j < 3; j++) {
      diff_bone[i][j] = tmp_bone[i][j] - diff_bone[i][j];
    }
  }

  for (i = 0; i < this->bone.size(); i++) {
    l = i;
    for (j = 0; j < this->bone.size(); j++) {
      if (this->bone[l].PBone_index == 65535) {
        break;
      } else if (this->bone[l].PBone_index == index) {
        break;
      }
      l = this->bone[l].PBone_index;
    }
    if (this->bone[l].PBone_index != 65535) {
      for (j = 0; j < len_bone; j++) {
        if (index_bone[j] == l) {
          this->move_bone(i, diff_bone[j]);
          // printf("%d %s %f %f %f\n", j, this->bone[i].name, diff_bone[j][0],
          // diff_bone[j][1], diff_bone[j][2]);
          break;
        }
      }
    }
  }

  return true;
}

bool MODEL::bone_vec(int index, double loc[], double vec[]) {
  for (int i = 0; i < 3; i++) {
    loc[i] = this->bone[index].loc[i];
  }

  int tail = this->bone[index].TBone_index;
  if (tail == 0) {
    for (int i = 0; i < this->bone.size(); i++) {
      if (this->bone[index].PBone_index == index)
        tail = i;
      break;
    }
  }
  if (tail == 0) {
    return false;
  }

  for (int i = 0; i < 3; i++) {
    vec[i] = this->bone[tail].loc[i] - this->bone[index].loc[i];
    // printf("%f ", vec[i]);
  }

  return true;
}

void MODEL::move_bone(unsigned int index, double diff[]) {
  if (index > this->bone.size())
    return;

  for (int i = 0; i < 3; i++) {
    this->bone[index].loc[i] = this->bone[index].loc[i] + diff[i];
  }
  for (int i = 0; i < this->vt.size(); i++) {
    int k = 0;
    double tmp = 0.0;
    if (this->vt[i].bone_num[0] == index) {
      tmp += (double)this->vt[i].bone_weight / 100;
      k = 1;
    }
    if (this->vt[i].bone_num[1] == index) {
      tmp += 1.0 - (double)this->vt[i].bone_weight / 100;
      k = 1;
    }

    if (k == 1) {
      for (int j = 0; j < 3; j++) {
        this->vt[i].loc[j] = this->vt[i].loc[j] + diff[j] * tmp;
      }
    }
  }
}

int MODEL::index_bone(const char bone[]) const {
  int index = -1;
  for (int i = 0; i < this->bone.size(); i++) {
    if (strcmp(this->bone[i].name, bone) == 0) {
      index = i;
      break;
    }
  }
  return index;
}

void MODEL::move_model(double diff[]) {
  for (int i = 0; i < this->bone.size(); i++) {
    for (int j = 0; j < 3; j++) {
      this->bone[i].loc[j] = this->bone[i].loc[j] + diff[j];
    }
  }
  for (int i = 0; i < this->vt.size(); i++) {
    for (int j = 0; j < 3; j++) {
      this->vt[i].loc[j] = this->vt[i].loc[j] + diff[j];
    }
  }
}

void MODEL::resize_model(double size) {
  for (int i = 0; i < this->bone.size(); i++) {
    for (int j = 0; j < 3; j++) {
      this->bone[i].loc[j] = this->bone[i].loc[j] * size;
    }
  }
  for (int i = 0; i < this->vt.size(); i++) {
    for (int j = 0; j < 3; j++) {
      this->vt[i].loc[j] = this->vt[i].loc[j] * size;
    }
  }

  for (int i = 1; i < this->skin.size(); i++) {
    for (int j = 0; j < this->skin[i].skin_vt.size(); j++) {
      for (int k = 0; k < 3; k++) {
        this->skin[i].skin_vt[j].loc[k] =
            this->skin[i].skin_vt[j].loc[k] * size;
      }
    }
  }
}

bool MODEL::marge_bone() {
  std::vector<int> index(this->bone.size());
  std::vector<char> marge(this->bone.size());
  std::vector<BONE> bone(this->bone.size());

  int tmp = 0;
  for (int i = 0; i < this->bone.size(); i++) {
    if (marge[i] == 0) {
      index[i] = i - tmp;
      for (int j = i + 1; j < this->bone.size(); j++) {
        if (strcmp(this->bone[i].name, this->bone[j].name) == 0) {
          if (this->bone[i].type == 7) {
            this->bone[i].TBone_index = this->bone[j].TBone_index;
            this->bone[i].type = this->bone[j].type;
            this->bone[i].IKBone_index = this->bone[j].IKBone_index;
            memcpy(this->bone[i].loc, this->bone[j].loc, sizeof(float) * 3);
          }
          index[j] = i - tmp;
          marge[j] = 1;
        }
      }
    } else {
      tmp++;
    }

    // PLOG_DEBUG << i << ":" << index[i] << " " << marge[i];
  }

  for (int i = 0; i < this->bone.size(); i++) {
    if (index[i] >= this->bone.size()) {
      return false;
    } else if (marge[i] == 0) {
      bone[index[i]] = this->bone[i];
      if (this->bone[i].PBone_index >= this->bone.size()) {
        bone[index[i]].PBone_index = 65535;
      } else {
        // PLOG_DEBUG << i << ":" << this->bone[i].PBone_index << " " <<
        // bone[index[i]].PBone_index;
        bone[index[i]].PBone_index = index[this->bone[i].PBone_index];
      }
      if (this->bone[i].TBone_index == 0 ||
          this->bone[i].TBone_index >= this->bone.size()) {
        bone[index[i]].TBone_index = 0;
      } else {
        bone[index[i]].TBone_index = index[this->bone[i].TBone_index];
      }
      bone[index[i]].type = this->bone[i].type;
      if (this->bone[i].IKBone_index == 0 ||
          this->bone[i].IKBone_index >= this->bone.size()) {
        bone[index[i]].IKBone_index = 0;
      } else {
        bone[index[i]].IKBone_index = index[this->bone[i].IKBone_index];
      }
    }
  }

  PLOG_DEBUG << "ボーンインデックスをアップデート";

  this->update_bone_index(index);
  this->bone.resize(this->bone.size() - tmp);

  std::swap(this->bone, bone);

  return true;
}

bool MODEL::marge_mat() {
  int i, j, k;
  int size;
  int vt_index_count;
  char *p;

  auto index = (int *)MALLOC(this->mat.size() * sizeof(int));
  auto marge = (char *)MALLOC(this->mat.size() * sizeof(char));
  memset(marge, 0, this->mat.size() * sizeof(char));
  std::vector<unsigned short> vt_index(this->vt_index.size());
  auto tmp_count = (int *)MALLOC(this->mat.size() * sizeof(int));
  if (tmp_count == NULL)
    return false;
  memset(tmp_count, 0, this->mat.size() * sizeof(int));
  auto tmp_mat = this->mat;

  // テクスチャ名の同じ材質を探す
  auto tmp = 0;
  auto sum = 0;
  /*
  for(i=0; i<this->mat_count; i++){
          if(marge[i] == 0){

                  if(this->mat[i].alpha >= 0.999){
                          sum++;
                  }
                  if(this->mat[i].tex[0] != '\0'){
                          for(j=i+1; j<this->mat_count; j++){
                                  if(strcmp(this->mat[i].tex,
  this->mat[j].tex) == 0){ p = strrchr(this->mat[i].tex, '.'); if(p != NULL){
                                                  if( strcmp(p, ".sph") ==0 ||
                                                          strcmp(p, ".spa") ==0
  || strcmp(p, ".tga") ==0 || strcmp(p, ".bmp") ==0 || strcmp(p, ".png") ==0 ||
                                                          strcmp(p, ".jpg")
  ==0){ marge[j] = -1; }else{ p = NULL;
                                                  }
                                          }
                                          if(p == NULL){
                                                  marge[j] = 1;
                                          }
                                  }
                          }
                  }
          }else{
                  tmp++;
          }
  }
  */
  // printf("%d %d %d\n", this->mat_count, tmp, sum);
  memset(marge, 0, this->mat.size() * sizeof(char));

  tmp = 0;
  for (i = 0; i < this->mat.size(); i++) {
    if (marge[i] == 0) {
      /*
      if(this->mat[i].alpha >= 0.999){
              index[i] = i - tmp;
      }else{
      */
      index[i] = sum;
      sum++;

      if (this->mat[i].tex[0] != '\0') {
        for (j = i + 1; j < this->mat.size(); j++) {
          if (strcmp(this->mat[i].tex, this->mat[j].tex) == 0) {
            if (0.0001 < abs(this->mat[i].tex - this->mat[j].tex)) {
              p = strrchr(this->mat[i].tex, '.');
              if (p != NULL) {
                if (strcmp(p, ".sph") == 0 || strcmp(p, ".spa") == 0) {
                  marge[j] = 0;
                } else {
                  p = NULL;
                }
              }
              if (p == NULL) {
                index[j] = index[i];
                marge[j] = 1;
              }
            }
          }
        }
      }
    } else {
      tmp++;
    }
#ifdef DEBUG
    printf("%d:%d %d\n", i, index[i], marge[i]);
#endif
  }

  // 面頂点リスト並び替え
  k = 0;

  for (i = 0; i < this->mat.size(); i++) {
    vt_index_count = 0;
    sum = 0;
    for (j = 0; j < this->mat.size(); j++) {
      if (index[j] == i) {
        size = this->mat[j].vt_index_count * sizeof(unsigned short);

        memcpy(&vt_index[k], &this->vt_index[sum], size);
#ifdef DEBUG
        printf("%d <- %d  %d\n", i, j, k);
#endif
        k = k + this->mat[j].vt_index_count;
        vt_index_count = vt_index_count + this->mat[j].vt_index_count;
      }
      sum = sum + this->mat[j].vt_index_count;
    }
    tmp_count[i] = vt_index_count;
#ifdef DEBUG
    printf("%d %d %d\n", i, vt_index_count, this->mat[i].vt_index_count);
#endif
  }

  // 材質並び替え
  for (i = 0; i < this->mat.size(); i++) {
    if (marge[i] == 0) {
      if (index[i] != i)
        this->mat[index[i]] = tmp_mat[i];
      this->mat[index[i]].vt_index_count = tmp_count[index[i]];
    }
  }

  this->mat.resize(this->mat.size() - tmp);

#ifdef MEM_DBG
  printf("FREE %p %p %p %p\n", index, marge, this->vt, tmp_count);
#endif

  FREE(index);
  FREE(marge);
  FREE(tmp_count);
  std::swap(this->vt_index, vt_index);

  return true;
}

void MODEL::marge_IK() {
  // 重複IKを削除
  std::vector<int> index(this->IK.size());
  std::vector<char> marge(this->IK.size());

  int tmp = 0;
  for (int i = 0; i < this->IK.size(); i++) {
    if (marge[i] == 0) {
      index[i] = i - tmp;
      for (int j = i + 1; j < this->IK.size(); j++) {
        if (this->IK[i].IKBone_index == this->IK[j].IKBone_index) {
          index[j] = i - tmp;
          marge[j] = 1;
        }
      }
    } else {
      tmp++;
    }

    // PLOG_DEBUG << i << ":" << index[i] << " " << marge[i];
  }

  for (int i = 0; i < this->IK.size(); i++) {
    if (marge[i] == 0 && index[i] != i) {
      this->IK[index[i]] = this->IK[i];
    }
  }
  this->IK.resize(this->IK.size() - tmp);
}

void MODEL::marge_bone_disp() {
  // 同名枠をマージ
  PLOG_DEBUG << this->bone_group.size();

  std::vector<int> index(this->bone_group.size());
  std::vector<char> marge(this->bone_group.size());
  memset(marge.data(), 0, this->bone_group.size() * sizeof(char));
  std::vector<BONE_DISP> bone_disp(this->bone_disp.size());

  int tmp = 0;
  for (int i = 0; i < this->bone_group.size(); i++) {
    if (marge[i] == 0) {
      index[i] = i - tmp;
      for (int j = i + 1; j < this->bone_group.size(); j++) {
        if (strcmp(this->bone_group[i].name, this->bone_group[j].name) == 0) {
          index[j] = i - tmp;
          marge[j] = 1;
        }
      }
    } else {
      tmp++;
    }
  }

  for (int i = 0; i < this->bone_group.size(); i++) {
    if (marge[i] == 0 && index[i] != i) {
      this->bone_group[index[i]] = this->bone_group[i];
    }
  }

  int k = 0;
  for (int i = 0; i < this->bone_group.size(); i++) {
    for (int j = 0; j < this->bone_disp.size(); j++) {
      if (index[this->bone_disp[j].bone_group - 1] == i) {
        bone_disp[k] = this->bone_disp[j];

        bone_disp[k].bone_group = index[bone_disp[k].bone_group - 1] + 1;

        k++;
      }
    }
  }

  this->bone_group.resize(this->bone_group.size() - tmp);
  this->bone_disp.resize(k);

  this->bone_disp = bone_disp;

  // 重複登録ボーンを削除

  index.resize(this->bone_disp.size());
  marge.resize(this->bone_disp.size());
  memset(marge.data(), 0, this->bone_disp.size() * sizeof(char));

  tmp = 0;
  for (int i = 0; i < this->bone_disp.size(); i++) {
    if (marge[i] == 0) {
      index[i] = i - tmp;
      for (int j = i + 1; j < this->bone_disp.size(); j++) {
        if (this->bone_disp[i].index == this->bone_disp[j].index) {
          index[j] = i - tmp;
          marge[j] = 1;
        }
      }
    } else {
      tmp++;
    }
  }

  for (int i = 0; i < this->bone_disp.size(); i++) {
    if (marge[i] == 0 && index[i] != i) {
      this->bone_disp[index[i]].index = this->bone_disp[i].index;
      this->bone_disp[index[i]].bone_group = this->bone_disp[i].bone_group;
    }
  }

  this->bone_disp.resize(this->bone_disp.size() - tmp);
}

void MODEL::marge_rb() {
  // 同名の剛体を削除

  std::vector<int> index(this->rbody.size());
  std::vector<char> marge(this->rbody.size());

  int tmp = 0;
  for (int i = 0; i < this->rbody.size(); i++) {
    if (marge[i] == 0) {
      index[i] = i - tmp;
      for (int j = i + 1; j < this->rbody.size(); j++) {
        if (strcmp(this->rbody[i].name, this->rbody[j].name) == 0) {
          index[j] = i - tmp;
          marge[j] = 1;
        }
      }
    } else {
      tmp++;
    }
  }

  // ジョイント書き換え
  for (int i = 0; i < this->joint.size(); i++) {
    for (int j = 0; j < 2; j++) {
      this->joint[i].rbody[j] = index[this->joint[i].rbody[j]];
    }
  }

  // 重複削除
  for (int i = 0; i < this->rbody.size(); i++) {
    if (marge[i] == 0 && index[i] != i) {
      this->rbody[index[i]] = this->rbody[i];
    }
  }
  this->rbody.resize(this->rbody.size() - tmp);
}

void MODEL::update_skin() {
  // 表情baseの頂点位置を更新する
  if (this->skin.size()) {
    for (int i = 0; i < this->skin[0].skin_vt.size(); i++) {
      for (int j = 0; j < 3; j++) {
        int k = this->skin[0].skin_vt[i].index;
        this->skin[0].skin_vt[i].loc[j] = this->vt[k].loc[j];
      }
    }
  }
}

void MODEL::adjust_joint() {
  // 同じ名前のボーンにジョイントの位置を合わせる
  for (int i = 0; i < this->joint.size(); i++) {
    for (int j = 0; j < this->bone.size(); j++) {
      if (strcmp(this->joint[i].name, this->bone[j].name) == 0) {
        memcpy(this->joint[i].loc, this->bone[j].loc, sizeof(float) * 3);
      }
    }
  }
}

void MODEL::show_detail() const {
  printf("%s \n %f \n %s \n %s \n", this->header.magic.data(),
         this->header.version, this->header.name.data(),
         this->header.comment.data());
  printf("頂点数:%zu\n", this->vt.size());
  printf("面頂点数:%zu\n", this->vt_index.size());
  printf("材質数:%zu\n", this->mat.size());
  printf("ボーン数:%zu\n", this->bone.size());
  printf("IKデータ数:%zu\n", this->IK.size());
  printf("表情数:%zu\n", this->skin.size());
  printf("表情枠:%zu\n", this->skin_disp.size());
  printf("ボーン枠:%zu\n", this->bone_group.size());
  printf("表示ボーン数:%zu\n", this->bone_disp.size());
  printf("英名対応:%d\n", this->eng_support);
  printf("剛体数:%zu\n", this->rbody.size());
  printf("ジョイント数:%zu\n\n", this->joint.size());
}
