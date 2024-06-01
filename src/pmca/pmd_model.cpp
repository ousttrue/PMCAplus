#define _USE_MATH_DEFINES
#include <math.h>

#include "ioutil.h"
#include "pmd_model.h"
#include <plog/Log.h>
#include <string.h>

double angle_from_vec(double u, double v) {
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

bool MODEL::load(std::span<const uint8_t> bytes) {
  if (bytes.empty()) {
    return false;
  }

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
  PLOG_DEBUG << "頂点数:" << vt_count;
  this->vt.resize(vt_count);
  r.read_vector(this->vt);

  int vt_index_count = r.i32();
  PLOG_DEBUG << "面頂点数:" << vt_index_count;
  this->vt_index.resize(vt_index_count);
  r.read_vector(this->vt_index);

  int mat_count = r.i32();
  PLOG_DEBUG << "材質数:" << mat_count;
  this->mat.resize(mat_count);
  r.read_vector(this->mat);

  uint16_t bone_count = r.u16();
  PLOG_DEBUG << "ボーン数:" << bone_count;
  this->bone.resize(bone_count);
  r.read_vector(this->bone);

  uint16_t IK_count = r.u16();
  PLOG_DEBUG << "IKデータ数:" << IK_count;
  for (int i = 0; i < IK_count; i++) {
    this->IK.push_back({});
    auto &ik = this->IK.back();
    ik.ik_index = r.u16();
    ik.ik_target_index = r.u16();
    char IK_chain_len = r.u8();
    ik.iterations = r.u16();
    ik.weight = r.f32();
    ik.IK_chain.resize(IK_chain_len);
    if (IK_chain_len > 0) {
      r.read(ik.IK_chain.data(), 2 * IK_chain_len);
    }
  }

  uint16_t skin_count = r.u16();
  PLOG_DEBUG << "表情数:" << skin_count;
  for (int i = 0; i < skin_count; i++) {
    this->skin.push_back({});
    auto &morph = this->skin.back();
    r.read(morph.name, 20);
    int skin_vt_count = r.i32();
    morph.type = r.u8();
    morph.skin_vt.resize(skin_vt_count);
    r.read_vector(morph.skin_vt);
  }

  uint8_t skin_disp_count = r.u8();
  PLOG_DEBUG << "表情枠:" << skin_disp_count;
  this->skin_disp.resize(skin_disp_count);
  r.read(this->skin_disp.data(), 2 * this->skin_disp.size());

  uint8_t bone_group_count = r.u8();
  PLOG_DEBUG << "ボーン枠:" << bone_group_count;
  this->bone_group.resize(bone_group_count);
  r.read_vector(this->bone_group);

  int bone_disp_count = r.i32();
  PLOG_DEBUG << "表示ボーン数:" << bone_disp_count;
  this->bone_disp.resize(bone_disp_count);
  r.read_vector(this->bone_disp);

  this->eng_support = r.u8();

  if (r.isend()) {
    PLOG_DEBUG << "拡張部分なし";
    this->eng_support = 0;
    this->toon[0] = "toon01.bmp";
    this->toon[1] = "toon02.bmp";
    this->toon[2] = "toon03.bmp";
    this->toon[3] = "toon04.bmp";
    this->toon[4] = "toon05.bmp";
    this->toon[5] = "toon06.bmp";
    this->toon[6] = "toon07.bmp";
    this->toon[7] = "toon08.bmp";
    this->toon[8] = "toon09.bmp";
    this->toon[9] = "toon10.bmp";
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
      char buf[20];
      r.read(buf, 20);
      // this->bone[i].name_eng[20] = '\0';
    }

    // skin:0
    // if (this->skin.size() > 0) {
    //   strcpy(this->skin[0].name_eng, "base");
    // }
    // skin:1~
    for (int i = 1; i < this->skin.size(); i++) {
      char buf[20];
      r.read(buf, 20);
      // this->skin[i].name_eng[20] = '\0';
    }
    for (int i = 0; i < this->bone_group.size(); i++) {
      char buf[50];
      r.read(buf, 50);
      // this->bone_group[i].name_eng[50] = '\0';
    }
  } else {
    PLOG_DEBUG << "英名非対応PMD";

    this->header.name_eng[0] = '\0';
    this->header.comment_eng[0] = '\0';

    // for (int i = 0; i < this->bone.size(); i++) {
    //   *this->bone[i].name_eng = '\0';
    // }
    //
    // for (int i = 0; i < this->skin.size(); i++) {
    //   *this->skin[i].name_eng = '\0';
    // }
    //
    // for (int i = 0; i < this->bone_group.size(); i++) {
    //   *this->bone_group[i].name_eng = '\0';
    // }
  }

  for (int i = 0; i < 10; i++) {
    char buf[100];
    r.read(buf, 100);
    this->toon[i] = buf;
  }

  int rbody_count = r.i32();
  PLOG_DEBUG << "剛体数:" << rbody_count;
  this->rbody.resize(rbody_count);
  r.read_vector(this->rbody);

  int joint_count = r.i32();
  PLOG_DEBUG << "ジョイント数:" << joint_count;
  this->joint.resize(joint_count);
  r.read_vector(this->joint);

  return true;
}

std::vector<uint8_t> MODEL::to_bytes() const {
  // ヘッダー書き換え
  this->header.magic = {'P', 'm', 'd', '\0'};
  this->header.version = 1.0;

  ioutil::Writer w;

  w.write(this->header.magic.data(), 3);
  w.write(&this->header.version, 4);
  w.write(this->header.name.data(), 20);
  w.write(this->header.comment.data(), 256);

  int vt_count = this->vt.size();
  w.write(&vt_count, 4);
  w.write_vector(this->vt);

  int vt_index_count = this->vt_index.size();
  w.write(&vt_index_count, 4);
  for (size_t i = 0; i < this->vt_index.size(); i++) {
    if (this->vt_index[i] >= this->vt.size()) {
      printf("頂点インデックスが不正です :%d\n", this->vt_index[i]);
      return {};
    }
    w.write(&this->vt_index[i], 2);
  }

  int mat_count = this->mat.size();
  w.write(&mat_count, 4);
  w.write_vector(this->mat);

  uint16_t bone_count = this->bone.size();
  w.write(&bone_count, 2);
  w.write_vector(this->bone);

  uint16_t IK_count = this->IK.size();
  w.write(&IK_count, 2);
  for (int i = 0; i < this->IK.size(); i++) {
    w.write(&this->IK[i].ik_index, 2);
    w.write(&this->IK[i].ik_target_index, 2);
    uint8_t IK_chain_len = this->IK[i].IK_chain.size();
    w.write(&IK_chain_len, 1);
    w.write(&this->IK[i].iterations, 2);
    w.write(&this->IK[i].weight, 4);
    w.write(this->IK[i].IK_chain.data(), 2, this->IK[i].IK_chain.size());
  }
  PLOG_DEBUG << "IKリスト";

  uint16_t skin_count = this->skin.size();
  w.write(&skin_count, 2);
  for (size_t i = 0; i < this->skin.size(); i++) {
    w.write(this->skin[i].name, 1, 20);
    int skin_vt_count = this->skin[i].skin_vt.size();
    w.write(&skin_vt_count, 4);
    w.write(&this->skin[i].type, 1);
    for (size_t j = 0; j < this->skin[i].skin_vt.size(); j++) {
      w.write(&this->skin[i].skin_vt[j].index, 4);
      w.write_value(this->skin[i].skin_vt[j].loc);
    }
  }
  PLOG_DEBUG << "表情";

  uint8_t skin_disp_count = this->skin_disp.size();
  w.write(&skin_disp_count, 1);
  w.write(this->skin_disp.data(), 2, this->skin_disp.size());
  PLOG_DEBUG << "表情表示";

  uint8_t bone_group_count = this->bone_group.size();
  w.write(&bone_group_count, 1);
  for (int i = 0; i < this->bone_group.size(); i++) {
    w.write(this->bone_group[i].name, 1, 50);
  }

  int bone_disp_count = this->bone_disp.size();
  w.write(&bone_disp_count, 4);
  for (int i = 0; i < this->bone_disp.size(); i++) {
    w.write(&this->bone_disp[i].bone_index, 2);
    w.write(&this->bone_disp[i].bone_group_index, 1);
  }
  PLOG_DEBUG << "ボーン表示";

  // extension
  w.write(&this->eng_support, 1);

  if (this->eng_support == 1) {
    w.write(this->header.name_eng.data(), 1, 20);
    w.write(this->header.comment_eng.data(), 1, 256);
    for (size_t i = 0; i < this->bone.size(); i++) {
      char buf[20];
      w.write(buf, 1, 20);
    }
    for (size_t i = 1; i < this->skin.size(); i++) {
      char buf[20];
      w.write(buf, 1, 20);
    }
    for (size_t i = 0; i < this->bone_group.size(); i++) {
      char buf[50];
      w.write(buf, 1, 50);
    }
  }
  PLOG_DEBUG << "英名";

  for (int i = 0; i < 10; i++) {
    assert(this->toon[i].size() < 100);
    char buf[100] = {0};
    memcpy(buf, this->toon[i].data(), this->toon[i].size());
    w.write(buf, 1, 100);
  }

  int rbody_count = this->rbody.size();
  w.write(&rbody_count, 4);
  w.write_vector(this->rbody);
  PLOG_DEBUG << "剛体";

  int joint_count = this->joint.size();
  w.write(&joint_count, 4);
  w.write_vector(this->joint);
  PLOG_DEBUG << "ジョイント";

  return w.buffer;
}

int print_PMD(MODEL *model, const char file_name[]) {
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

  int i = 0;
  for (auto &v : model->vt) {
    fprintf(txt, "No: %d\n", i++);
    fprintf(txt, "Loc: %f, %f, %f\n", v.loc.x, v.loc.y, v.loc.z);
    fprintf(txt, "Nor: %f, %f, %f\n", v.nor.x, v.nor.y, v.nor.z);
    fprintf(txt, "UV: %f, %f\n", v.uv.x, v.uv.y);
    fprintf(txt, "BONE: %d, %d\n", v.bone0, v.bone1);
    fprintf(txt, "bone_weight:%d\n", v.bone_weight);
    fprintf(txt, "edge_flag:%d\n\n", v.edge_flag);
  }

  fprintf(txt, "面頂点数:%zu\n", model->vt_index.size());

  for (i = 0; i < model->vt_index.size(); i++) {
    fprintf(txt, "%d\n", model->vt_index[i]);
  }
  fprintf(txt, "\n");

  fprintf(txt, "材質数: %zu\n", model->mat.size());
  for (auto &m : model->mat) {
    fprintf(txt, "No: %d\n", i);
    fprintf(txt, "diffuse: %f, %f, %f\n", m.diffuse.x, m.diffuse.y,
            m.diffuse.z);
    fprintf(txt, "alpha: %f\n", m.alpha);
    fprintf(txt, "specularity: %f\n", m.spec);
    fprintf(txt, "spec_col: %f, %f, %f\n", m.spec_col.x, m.spec_col.y,
            m.spec_col.z);
    fprintf(txt, "mirror_col: %f, %f, %f\n", m.mirror_col.x, m.mirror_col.y,
            m.mirror_col.z);
    fprintf(txt, "toon_index: %d\n", m.toon_index);
    fprintf(txt, "edge_flag:%d\n", m.edge_flag);
    fprintf(txt, "vt_index_count:%d\n", m.vt_index_count);
    fprintf(txt, "texture:%s\n\n", m.tex);
  }

  fprintf(txt, "ボーン数:%zu\n", model->bone.size());
  for (auto &b : model->bone) {
    fprintf(txt, "ボーン名:%s\n", b.name);
    fprintf(txt, "親ボーン:%d\n", b.parent_index);
    fprintf(txt, "テイルボーン:%d\n", b.tail_index);
    fprintf(txt, "タイプ:%d\n", b.type);
    fprintf(txt, "IKボーン:%d\n", b.ik_index);
    fprintf(txt, "位置: %f, %f, %f", b.loc.x, b.loc.y, b.loc.z);
    fprintf(txt, "\n\n");
  }

  fprintf(txt, "IKデータ数:%zu\n", model->IK.size());
  for (int i = 0; i < model->IK.size(); i++) {
    fprintf(txt, "IKボーン:%d\n", model->IK[i].ik_index);
    fprintf(txt, "IKテイルボーン:%d\n", model->IK[i].ik_target_index);
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
    for (auto &skin_vt : model->skin[i].skin_vt) {
      fprintf(txt, "%d ", skin_vt.index);
      fprintf(txt, "%f, %f, %f ", skin_vt.loc.x, skin_vt.loc.y, skin_vt.loc.z);
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

  for (auto &bd : model->bone_disp) {
    fprintf(txt, "ボーン番号:%d\n", bd.bone_index);
    fprintf(txt, "表示番号:%d\n", bd.bone_group_index);
  }

  fprintf(txt, "英名対応:%d\n", model->eng_support);
  if (model->eng_support == 1) {
    fprintf(txt, "%s\n", model->header.name_eng.data());
    fprintf(txt, "%s\n", model->header.comment_eng.data());
    // for (i = 0; i < model->bone.size(); i++) {
    //   fprintf(txt, "%s\n", model->bone[i].name_eng);
    // }
    // for (i = 0; i < model->skin.size(); i++) {
    //   fprintf(txt, "%s\n", model->skin[i].name_eng);
    // }
    // for (i = 0; i < model->bone_group.size(); i++) {
    //   fprintf(txt, "%s\n", model->bone_group[i].name_eng);
    // }
  }

  for (i = 0; i < 10; i++) {
    fprintf(txt, "%s\n", model->toon[i].c_str());
  }

  fprintf(txt, "剛体数:%zu\n", model->rbody.size());
  for (auto &rb : model->rbody) {
    fprintf(txt, "%s\n", rb.name);
    fprintf(txt, "ボーン:%d\n", rb.bone);
    fprintf(txt, "グループ:%d\n", rb.group);
    fprintf(txt, "ターゲット:%d\n", rb.target);
    fprintf(txt, "形状:%d\n", rb.shape);
    fprintf(txt, "size: %f, %f, %f\n", rb.size.x, rb.size.y, rb.size.z);
    fprintf(txt, "loc: %f, %f, %f\n", rb.loc.x, rb.loc.y, rb.loc.z);
    fprintf(txt, "rot: %f, %f, %f\n", rb.rot.x, rb.rot.y, rb.rot.z);
    fprintf(txt, "property: %f, %f, %f, %f, %f\n", rb.mass, rb.dump, rb.rotdamp,
            rb.restitution, rb.friction);
    fprintf(txt, "タイプ:%d\n\n", rb.type);
  }

  fprintf(txt, "ジョイント数:%zu\n", model->joint.size());
  for (auto &joint : model->joint) {
    fprintf(txt, "%s\n", joint.name);
    fprintf(txt, "剛体 : %d, %d\n", joint.rigidbody_a, joint.rigidbody_b);
    fprintf(txt, "loc: %f, %f, %f\n", joint.loc.x, joint.loc.y, joint.loc.z);
    fprintf(txt, "rot: %f, %f, %f\n", joint.rot.x, joint.rot.y, joint.rot.z);
    fprintf(txt,
            "limit: (%f, %f, %f), (%f, %f, %f), (%f, %f, %f), (%f, %f, %f)\n",
            joint.loc_lower_limit.x, joint.loc_lower_limit.y,
            joint.loc_lower_limit.z, joint.loc_upper_limit.x,
            joint.loc_upper_limit.y, joint.loc_upper_limit.z,
            joint.rot_lower_limit.x, joint.rot_lower_limit.y,
            joint.rot_lower_limit.z, joint.rot_upper_limit.x,
            joint.rot_upper_limit.y, joint.rot_upper_limit.z);
    fprintf(txt, "spring: (%f, %f, %f), (%f, %f, %f)\n", joint.loc_spring.x,
            joint.loc_spring.y, joint.loc_spring.z, joint.rot_spring.x,
            joint.rot_spring.y, joint.rot_spring.z);
    fprintf(txt, "\n");
  }

  fclose(txt);

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
    vt.back().bone0 += pre_bone_size;
    vt.back().bone1 += pre_bone_size;
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
    if (bone.back().parent_index != USHORT_MAX)
      bone.back().parent_index += pre_bone_size;
    if (bone.back().tail_index != 0)
      bone.back().tail_index += pre_bone_size;
    if (bone.back().ik_index != 0)
      bone.back().ik_index += pre_bone_size;
  }

  // IKリスト
  this->IK.reserve(this->IK.size() + add->IK.size());
  for (auto &ik : add->IK) {
    IK.push_back(ik);
    IK.back().ik_index += pre_bone_size;
    IK.back().ik_target_index += pre_bone_size;
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
    bone_disp.back().bone_index += pre_bone_size;
    bone_disp.back().bone_group_index += pre_bone_group_size;
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
    joint.back().rigidbody_a += pre_rbody_size;
    joint.back().rigidbody_b += pre_rbody_size;
  }

  return 0;
}

void MODEL::sort_bone(NameList *list) {
  std::vector<int> index(this->bone.size());
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
      if (this->bone[i].parent_index != 65535 &&
          index[this->bone[i].parent_index] > index[i] &&
          strcmp(this->bone[i].name, "-0") != 0) {

        tmp = index[this->bone[i].parent_index];
        int tmp_PBone_index = index[i];
        for (int j = 0; j < this->bone.size(); j++) {
          if (index[j] >= tmp_PBone_index && index[j] < tmp) {
            index[j]++; // 一つ後ろにずらす
          }
        }
        index[this->bone[i].parent_index] =
            tmp_PBone_index; // ボーンの一つ前に親ボーンを移動
      }
    }
  }

  for (int i = 0; i < this->bone.size(); i++) { // ボーン並び変え
#ifdef DEBUG
    printf("index[%d]=%d\n", i, index[i]);
#endif
    strcpy(bone[index[i]].name, this->bone[i].name);
    // strcpy(bone[index[i]].name_eng, this->bone[i].name_eng);
    if (this->bone[i].parent_index == 65535) {
      bone[index[i]].parent_index = 65535;
    } else {
      bone[index[i]].parent_index = index[this->bone[i].parent_index];
    }
    if (this->bone[i].tail_index == 0) {
      bone[index[i]].tail_index = 0;
    } else {
      bone[index[i]].tail_index = index[this->bone[i].tail_index];
    }

    bone[index[i]].type = this->bone[i].type;

    if (this->bone[i].ik_index == 0) {
      bone[index[i]].ik_index = 0;
    } else {
      bone[index[i]].ik_index = index[this->bone[i].ik_index];
    }
    bone[index[i]].loc = this->bone[i].loc;
  }

  this->update_bone_index(index);

  std::swap(this->bone, bone);

  if (strcmp(this->bone[this->bone.size() - 1].name, "-0") == 0) {
    this->bone.pop_back();
  }
}

void MODEL::update_bone_index(std::span<int> index) {
  // 頂点のボーン番号を書き換え
  for (auto &v : this->vt) {
    v.bone0 = index[v.bone0];
    v.bone1 = index[v.bone1];
  }

  // IKリストのボーン番号を書き換え
  for (auto &ik : this->IK) {
    // PLOG_DEBUG << i;
    ik.ik_index = index[ik.ik_index];
    ik.ik_target_index = index[ik.ik_target_index];
    for (int j = 0; j < ik.IK_chain.size(); j++) {
      ik.IK_chain[j] = index[ik.IK_chain[j]];
    }
  }

  // 表示ボーン番号を書き換え
  for (auto &bd : this->bone_disp) {
    bd.bone_index = index[bd.bone_index];
  }

  // 剛体ボーン番号を書き換え
  for (auto &rb : this->rbody) {
    if (rb.bone != USHORT_MAX) {
      rb.bone = index[rb.bone];
    }
  }

  PLOG_DEBUG << "ボーンインデックス更新完了";
}

void MODEL::sort_skin(NameList *list) {

  std::vector<int> index(this->skin.size());
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
    this->bone_disp[i].bone_group_index =
        index[this->bone_disp[i].bone_group_index - 1] + 1;
  }

  tmp = 0;
  for (int i = 1; i <= this->bone_group.size(); i++) {
    for (int j = 0; j < this->bone_disp.size(); j++) {
      if (this->bone_disp[j].bone_group_index == i) {
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
        if (this->bone[j].tail_index == i) {
          flag = 1;
          break;
        }
      }
      if (flag == 1) {
        strncpy(this->bone[i].name, "-0", 4);
        // strncpy(this->bone[i].name_eng, "-0", 4);
      }
    }
  }

  // 子ボーンがtailならば+親ボーン名という名前にする
  for (int i = 0; i < this->bone.size(); i++) {
    int tmp = this->bone[i].tail_index;
    if (tmp < this->bone.size()) {
      if (this->bone[tmp].type == 6 || this->bone[tmp].type == 7) {
        sprintf(this->bone[tmp].name, "+%s", this->bone[i].name);
        // sprintf(this->bone[tmp].name_eng, "+%s", this->bone[i].name_eng);
        // printf("%s\n", this->bone[tmp].name);
      }
    } else {
      printf("範囲外のボーンインデックスを見つけました\n");
    }
  }
}

void MODEL::scale_vertices(int index, const mat3 &mtr, const float3 &scale) {
  auto loc = this->bone[index].loc;
  for (auto &v : this->vt) {
    if (v.bone0 == index || v.bone1 == index) {
      // to bone local
      auto local = mtr.rotate(v.loc - loc);
      // scale
      local = local.scale(scale);
      // to world
      auto world = mtr.transposed().rotate(local) + loc;
      // weight for bone index
      auto weight = 0.0f;
      if (v.bone0 == index) {
        weight += v.bone_weight / 0.01f;
      }
      if (v.bone1 == index) {
        weight += 1.0f - v.bone_weight * 0.01f;
      }
      // blend
      v.loc = v.loc * (1 - weight) + world * weight;
    }
  }
}

void MODEL::scale_bones(int index, const mat3 &mtr, const float3 &scale) {
  auto loc = this->bone[index].loc;
  for (int i = 0; i < this->bone.size(); ++i) {
    auto &b = this->bone[i];
    if (b.parent_index == index) {
      // to local
      auto local = mtr.rotate(b.loc - loc);
      // scale
      local = local.scale(scale);
      // to world
      auto world = mtr.transposed().rotate(local) + loc;
      // diff in world
      auto diff = world - b.loc;
      this->move_bone(i, diff);
      // apply descendants
      for (int j = 0; j < this->bone.size(); ++j) {
        if (has_parent(j, i, true)) {
          this->move_bone(j, diff);
        }
      }
    }
  }
}

std::optional<int> MODEL::find_tail(int index) const {
  int tail = this->bone[index].tail_index;
  if (tail != 0) {
    return tail;
  }

  for (int i = 0; i < this->bone.size(); i++) {
    if (this->bone[index].parent_index == index) {
      return i;
    }
  }

  return {};
}

void MODEL::move_bone(unsigned int index, const float3 &diff) {
  if (index > this->bone.size())
    return;

  this->bone[index].loc = this->bone[index].loc + diff;
  for (int i = 0; i < this->vt.size(); i++) {
    int k = 0;
    double tmp = 0.0;
    if (this->vt[i].bone0 == index) {
      tmp += (double)this->vt[i].bone_weight / 100;
      k = 1;
    }
    if (this->vt[i].bone1 == index) {
      tmp += 1.0 - (double)this->vt[i].bone_weight / 100;
      k = 1;
    }

    if (k == 1) {
      this->vt[i].loc = this->vt[i].loc + diff * tmp;
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

void MODEL::move_model(const float3 &diff) {
  for (int i = 0; i < this->bone.size(); i++) {
    this->bone[i].loc = this->bone[i].loc + diff;
  }
  for (int i = 0; i < this->vt.size(); i++) {
    this->vt[i].loc = this->vt[i].loc + diff;
  }
}

void MODEL::resize_model(double size) {
  for (auto &b : this->bone) {
    b.loc = b.loc * size;
  }
  for (auto &v : this->vt) {
    v.loc = v.loc * size;
  }
  for (auto &s : this->skin) {
    for (auto &sv : s.skin_vt) {
      sv.loc = sv.loc * size;
    }
  }
}

bool MODEL::marge_bone() {
  std::vector<int> index(this->bone.size());
  std::vector<char> marge(this->bone.size());

  int tmp = 0;
  for (int i = 0; i < this->bone.size(); i++) {
    if (marge[i] == 0) {
      index[i] = i - tmp;
      for (int j = i + 1; j < this->bone.size(); j++) {
        if (strcmp(this->bone[i].name, this->bone[j].name) == 0) {
          if (this->bone[i].type == 7) {
            this->bone[i].tail_index = this->bone[j].tail_index;
            this->bone[i].type = this->bone[j].type;
            this->bone[i].ik_index = this->bone[j].ik_index;
            this->bone[i].loc = this->bone[j].loc;
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
      if (this->bone[i].parent_index >= this->bone.size()) {
        bone[index[i]].parent_index = 65535;
      } else {
        // PLOG_DEBUG << i << ":" << this->bone[i].parent_index << " " <<
        // bone[index[i]].parent_index;
        bone[index[i]].parent_index = index[this->bone[i].parent_index];
      }
      if (this->bone[i].tail_index == 0 ||
          this->bone[i].tail_index >= this->bone.size()) {
        bone[index[i]].tail_index = 0;
      } else {
        bone[index[i]].tail_index = index[this->bone[i].tail_index];
      }
      bone[index[i]].type = this->bone[i].type;
      if (this->bone[i].ik_index == 0 ||
          this->bone[i].ik_index >= this->bone.size()) {
        bone[index[i]].ik_index = 0;
      } else {
        bone[index[i]].ik_index = index[this->bone[i].ik_index];
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
        if (this->IK[i].ik_index == this->IK[j].ik_index) {
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
      if (index[this->bone_disp[j].bone_group_index - 1] == i) {
        bone_disp[k] = this->bone_disp[j];

        bone_disp[k].bone_group_index =
            index[bone_disp[k].bone_group_index - 1] + 1;

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
        if (this->bone_disp[i].bone_index == this->bone_disp[j].bone_index) {
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
      this->bone_disp[index[i]].bone_index = this->bone_disp[i].bone_index;
      this->bone_disp[index[i]].bone_group_index =
          this->bone_disp[i].bone_group_index;
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
    this->joint[i].rigidbody_a = index[this->joint[i].rigidbody_a];
    this->joint[i].rigidbody_b = index[this->joint[i].rigidbody_b];
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
      int k = this->skin[0].skin_vt[i].index;
      this->skin[0].skin_vt[i].loc = this->vt[k].loc;
    }
  }
}

void MODEL::adjust_joint() {
  // 同じ名前のボーンにジョイントの位置を合わせる
  for (int i = 0; i < this->joint.size(); i++) {
    for (int j = 0; j < this->bone.size(); j++) {
      if (strcmp(this->joint[i].name, this->bone[j].name) == 0) {
        this->joint[i].loc = this->bone[j].loc;
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
