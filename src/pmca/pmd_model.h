#pragma once
#include "algebraic_geometry.h"
#include <array>
#include <cmath>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <vector>

#define USHORT_MAX 65535

#define PATH_LEN 256
#define NAME_LEN 128
#define COMMENT_LEN 256

struct NameList {
  std::vector<std::array<char, NAME_LEN>> bone;
  std::vector<std::array<char, NAME_LEN>> bone_eng;

  std::vector<std::array<char, NAME_LEN>> skin;
  std::vector<std::array<char, NAME_LEN>> skin_eng;

  std::vector<std::array<char, NAME_LEN>> disp;
  std::vector<std::array<char, NAME_LEN>> disp_eng;
};

struct HEADER { /*283byte*/
  mutable std::array<char, 4> magic = {0};
  mutable float version;
  std::array<char, NAME_LEN> name = {0};
  std::array<char, COMMENT_LEN> comment = {0};
  std::array<char, NAME_LEN> name_eng = {0};
  std::array<char, COMMENT_LEN> comment_eng = {0};
};

#pragma pack(push, r1, 1)
struct VERTEX {
  float3 loc;
  float3 nor;
  float2 uv;
  uint16_t bone0;
  uint16_t bone1;
  uint8_t bone_weight;
  uint8_t edge_flag;
};
#pragma pack(pop)
static_assert(sizeof(VERTEX) == 38, "sizeof VERTEX");

#pragma pack(push, r1, 1)
struct MATERIAL {
  float3 diffuse;
  float alpha;
  float spec;
  float3 spec_col;
  float3 mirror_col;
  unsigned char toon_index;
  unsigned char edge_flag;
  unsigned int vt_index_count;
  char tex[20];
};
#pragma pack(pop)
static_assert(sizeof(MATERIAL) == 70, "sizeof MATERIAL");

double angle_from_vec(double u, double v);

#pragma pack(push, r1, 1)
struct BONE { /*39byte*/
  char name[20];
  uint16_t parent_index;
  uint16_t tail_index;
  uint8_t type;
  uint16_t ik_index;
  float3 loc;

  mat3 rotationToTail(const float3 &tail) const {
    // head => tail ベクトル
    auto vec = (tail - this->loc).normalized();

    // ベクトルのZXY角を求める
    auto rot_z = angle_from_vec(vec.x, vec.y);
    auto rot_x = angle_from_vec(vec.z, sqrt(vec.x * vec.x + vec.y * vec.y));
    // 回転行列を求める
    return mat3::rotation_x(rot_x) * mat3::rotation_z(rot_z);
  }
};
#pragma pack(pop)
static_assert(sizeof(BONE) == 39, "sizeof BONE");

struct IK_LIST { /*11+2*IK_chain_len byte*/
  uint16_t ik_index;
  uint16_t ik_target_index;
  uint16_t iterations;
  float weight;
  std::vector<uint16_t> IK_chain;
};

struct MORPH_DATA { /*16byte*/
  uint32_t index;
  float3 loc;
};
static_assert(sizeof(MORPH_DATA) == 16, "sizeof MORPH_DATA");

struct MORPH { /*25+16*skin_vt_count byte*/
  char name[20];
  uint8_t type;
  std::vector<MORPH_DATA> skin_vt;
};

struct BONE_GROUP { /*3 byte*/
  char name[50];
};

#pragma pack(push, r1, 1)
struct BONE_DISP { /*3 byte*/
  uint16_t bone_index;
  uint8_t bone_group_index;
};
#pragma pack(pop)
static_assert(sizeof(BONE_DISP) == 3, "sizeof BONE_DISP");

#pragma pack(push, r1, 1)
struct RIGID_BODY { // 83byte
  char name[20];
  uint16_t bone;
  uint8_t group;
  uint16_t target;
  uint8_t shape;
  float3 size; // w h d
  float3 loc;
  float3 rot; // radian
  float mass;
  float dump;
  float rotdamp;
  float restitution;
  float friction;
  uint8_t type;
};
#pragma pack(pop)
static_assert(sizeof(RIGID_BODY) == 83, "sizeof RIGID_BODY");

#pragma pack(push, r1, 1)
struct JOINT { // 124byte
  char name[20];
  uint32_t rigidbody_a;
  uint32_t rigidbody_b;
  float3 loc;
  float3 rot; // radian
  float3 loc_lower_limit;
  float3 loc_upper_limit;
  float3 rot_lower_limit;
  float3 rot_upper_limit;
  float3 loc_spring;
  float3 rot_spring;
};
#pragma pack(pop)
static_assert(sizeof(JOINT) == 124, "sizeof JOINT");

struct MODEL {
  HEADER header;
  std::vector<VERTEX> vt;
  std::vector<unsigned short> vt_index;
  std::vector<MATERIAL> mat;
  std::vector<BONE> bone;
  std::vector<IK_LIST> IK;
  std::vector<MORPH> skin;
  std::vector<unsigned short> skin_disp;
  std::vector<BONE_GROUP> bone_group;
  std::vector<BONE_DISP> bone_disp;
  unsigned char eng_support = 0;
  std::string toon[10];
  std::vector<RIGID_BODY> rbody;
  std::vector<JOINT> joint;

private:
  MODEL();

public:
  ~MODEL();
  static std::shared_ptr<MODEL> create() {
    return std::shared_ptr<MODEL>(new MODEL);
  }
  static std::shared_ptr<MODEL> from_bytes(std::span<const uint8_t> bytes) {
    auto model = create();
    if (model->load(bytes)) {
      return model;
    }
    return model;
    // return {};
  }
  bool load(std::span<const uint8_t> bytes);
  std::vector<uint8_t> to_bytes() const;
  bool add_PMD(const std::shared_ptr<MODEL> &add);

  bool marge_bone();
  bool marge_mat();
  void marge_IK();
  void marge_bone_disp();
  void marge_rb();
  void update_bone_index(std::span<int> index);
  // void translate(struct NameList *list, short mode);
  void sort_bone(struct NameList *list);
  void sort_skin(struct NameList *list);
  void sort_disp(struct NameList *list);
  void rename_tail();
  bool scale_bone(int index, const float3 &scale) {
    auto tail_index = this->find_tail(index);
    if (!tail_index) {
      return false;
    }

    auto rot = this->bone[index].rotationToTail(this->bone[*tail_index].loc);
    scale_vertices(index, rot, scale);
    scale_bones(index, rot, scale);

    return true;
  }
  void scale_vertices(int bone_index, const mat3 &mtr, const float3 &scale);
  void scale_bones(int bone_index, const mat3 &mtr, const float3 &scale);
  bool has_parent(int bone_index, int parent_index, bool recursive) {
    auto current = &this->bone[bone_index];
    while (current->parent_index != USHORT_MAX) {
      if (current->parent_index == parent_index) {
        return true;
      }
      if (!recursive) {
        return false;
      }
      current = &this->bone[current->parent_index];
    }
    return false;
  }
  std::optional<int> find_tail(int index) const;
  void move_bone(unsigned int index, const float3 &diff);
  void resize_model(double size);
  int index_bone(const char bone[]) const;
  void move_model(const float3 &diff);
  void update_skin();
  void adjust_joint();
  void show_detail() const;
  int print_PMD(const std::string &file_name);
  int listup_bone(const std::string &file_name);
};
