// PMD関係のライブラリ、PMD編集など

#include "dbg.h"
#include <stdio.h>
#define _USE_MATH_DEFINES
#include <plog/Log.h>

#include <array>
#include <math.h>
#include <memory.h>
#include <stdlib.h>
#include <string.h>

// #define DLLExport edit
#include "mPMD.h"

void MODEL::translate(LIST *list, short mode) {
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

void MODEL::sort_bone(LIST *list) {
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

void MODEL::sort_skin(LIST *list) {

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

void MODEL::sort_disp(LIST *list) {
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

void coordtrans(double array[][3], unsigned int len, double loc[],
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

void coordtrans_inv(double array[][3], unsigned int len, double loc[],
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
  for (int i = 0; i < this->skin[0].skin_vt.size(); i++) {
    for (int j = 0; j < 3; j++) {
      int k = this->skin[0].skin_vt[i].index;
      this->skin[0].skin_vt[i].loc[j] = this->vt[k].loc[j];
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
