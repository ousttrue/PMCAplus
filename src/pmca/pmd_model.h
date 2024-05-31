#pragma once
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

struct float3 {
  float x = 0;
  float y = 0;
  float z = 0;
  float operator[](size_t index) const {
    return reinterpret_cast<const float *>(this)[index];
  }
  float &operator[](size_t index) {
    return reinterpret_cast<float *>(this)[index];
  }
  float3 operator+(const float3 &rhs) const {
    return {
        .x = x + rhs.x,
        .y = y + rhs.y,
        .z = z + rhs.z,
    };
  }
  float3 operator-(const float3 &rhs) const {
    return {
        .x = x - rhs.x,
        .y = y - rhs.y,
        .z = z - rhs.z,
    };
  }
  float3 operator*(float f) const {
    return {
        .x = x * f,
        .y = y * f,
        .z = z * f,
    };
  }
  static float dot(const float3 &lhs, const float3 &rhs) {
    return lhs.x * rhs.x + lhs.y * rhs.y + lhs.z * rhs.z;
  }
  float len() const { return std::sqrt(dot(*this, *this)); }
  float3 normalized() const { return *this * (1.0f / len()); }
};
static_assert(sizeof(float3) == 12, "sizeof float3");

union mat3 {
  struct {
    float m00;
    float m01;
    float m02;
    float m10;
    float m11;
    float m12;
    float m20;
    float m21;
    float m22;
  };
  struct {
    float3 row0;
    float3 row1;
    float3 row2;
  };
  float3 col0() const { return {m00, m10, m20}; }
  float3 col1() const { return {m01, m11, m21}; }
  float3 col2() const { return {m02, m12, m22}; }
  mat3 transposed() const {
    return {
        .m00 = m00,
        .m01 = m10,
        .m02 = m20,

        .m10 = m01,
        .m11 = m11,
        .m12 = m21,

        .m20 = m02,
        .m21 = m12,
        .m22 = m22,
    };
  }
  float3 rotate(const float3 &rhs) const {
    return {
        float3::dot(row0, rhs),
        float3::dot(row1, rhs),
        float3::dot(row2, rhs),
    };
  }
  static mat3 rotate_z(float theta) {
    auto c = std::cos(theta);
    auto s = std::sin(theta);
    return {
        .row0 = {c, -s, 0},
        .row1 = {s, c, 0},
        .row2 = {0, 0, 1},
    };
  }
  static mat3 rotate_x(float theta) {
    auto c = std::cos(theta);
    auto s = std::sin(theta);
    return {
        .row0 = {1, 0, 0},
        .row1 = {0, c, s},
        .row2 = {0, -s, c},
    };
  }
  mat3 operator*(const mat3 &rhs) const {
    return {
        .row0 =
            {
                float3::dot(row0, rhs.col0()),
                float3::dot(row0, rhs.col1()),
                float3::dot(row0, rhs.col2()),
            },
        .row1 =
            {
                float3::dot(row1, rhs.col0()),
                float3::dot(row1, rhs.col1()),
                float3::dot(row1, rhs.col2()),
            },
        .row2 =
            {
                float3::dot(row2, rhs.col0()),
                float3::dot(row2, rhs.col1()),
                float3::dot(row2, rhs.col2()),
            },
    };
  }
};
static_assert(sizeof(mat3) == 36, "sizeof mat3");

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
  float loc[3];
  float nor[3];
  float uv[2];
  unsigned short bone_num[2];
  unsigned char bone_weight;
  unsigned char edge_flag;
};
#pragma pack(pop)
static_assert(sizeof(VERTEX) == 38, "sizeof VERTEX");

#pragma pack(push, r1, 1)
struct MATERIAL {
  float diffuse[3];
  float alpha;
  float spec;
  float spec_col[3];
  float mirror_col[3];
  unsigned char toon_index;
  unsigned char edge_flag;
  unsigned int vt_index_count;
  char tex[NAME_LEN];
  char sph[NAME_LEN];
  char tex_path[PATH_LEN];
  char sph_path[PATH_LEN];
};
#pragma pack(pop)
static_assert(offsetof(MATERIAL, tex) == 50, "sizeof MATERIAL");

struct BONE { /*39byte*/
  char name[NAME_LEN];
  char name_eng[NAME_LEN];
  unsigned short PBone_index;
  unsigned short TBone_index;
  unsigned char type;
  unsigned short IKBone_index;
  float3 loc;
};

struct IK_LIST { /*11+2*IK_chain_len byte*/
  unsigned short IKBone_index;
  unsigned short IKTBone_index;
  unsigned short iterations;
  float weight;
  std::vector<unsigned short> IK_chain;
};

struct SKIN_DATA { /*16byte*/
  unsigned int index;
  float loc[3];
};

struct SKIN { /*25+16*skin_vt_count byte*/
  char name[NAME_LEN];
  char name_eng[NAME_LEN];
  unsigned char type;
  std::vector<SKIN_DATA> skin_vt;
};

struct BONE_GROUP { /*3 byte*/
  char name[NAME_LEN];
  char name_eng[NAME_LEN];
};

struct BONE_DISP { /*3 byte*/
  unsigned short index;
  unsigned char bone_group;
};

struct RIGID_BODY { // 83byte
  char name[NAME_LEN];
  unsigned short bone;
  unsigned char group;
  unsigned short target;
  unsigned char shape;
  float size[3]; // w h d
  float loc[3];
  float rot[3];      // radian
  float property[5]; // mass damp rotdamp restitution friction
  unsigned char type;
};

struct JOINT { // 124byte
  char name[NAME_LEN];
  unsigned int rbody[2];
  float3 loc;
  float rot[3];    // radian
  float limit[12]; // lower_limit_loc upper_limit_loc lower_limit_rot
                   // upper_limit_rot
  float spring[6]; // loc rot
};

struct MODEL {
  HEADER header;
  std::vector<VERTEX> vt;
  std::vector<unsigned short> vt_index;
  std::vector<MATERIAL> mat;
  std::vector<BONE> bone;
  std::vector<IK_LIST> IK;
  std::vector<SKIN> skin;
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
  void translate(struct NameList *list, short mode);
  void sort_bone(struct NameList *list);
  void sort_skin(struct NameList *list);
  void sort_disp(struct NameList *list);
  void rename_tail();
  bool scale_bone(int index, double sx, double sy, double sz);
  std::optional<int> find_tail(int index) const;
  void move_bone(unsigned int index, const float3 &diff);
  void resize_model(double size);
  int index_bone(const char bone[]) const;
  void move_model(double diff[]);
  void update_skin();
  void adjust_joint();
  void show_detail() const;
  int print_PMD(const std::string &file_name);
  int listup_bone(const std::string &file_name);
};
