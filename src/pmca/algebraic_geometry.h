#pragma once
#include <cmath>

struct float3 {
  float x = 0;
  float y = 0;
  float z = 0;
  // float operator[](size_t index) const {
  //   return reinterpret_cast<const float *>(this)[index];
  // }
  // float &operator[](size_t index) {
  //   return reinterpret_cast<float *>(this)[index];
  // }
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
  float3 scale(const float3 &s) const {
    return {
        .x = x * s.x,
        .y = y * s.y,
        .z = z * s.z,
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
        .row0 = {m00, m10, m20},
        .row1 = {m01, m11, m21},
        .row2 = {m02, m12, m22},
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

struct transform {
  mat3 rotation = {
      .row0 = {1, 0, 0},
      .row1 = {0, 1, 0},
      .row2 = {0, 0, 1},
  };
  float3 translation = {0, 0, 0};
};
