#pragma once
#include <span>
#include <stdint.h>
#include <string>
#include <vector>

namespace ioutil {

std::vector<uint8_t> readfile(const std::string &path);

class binaryreader {
  std::span<uint8_t> _data;
  int _pps = 0;

public:
  binaryreader(std::span<uint8_t> data);

  std::span<uint8_t> bytes(int size);
  std::string_view str(int size);
  template <typename T, size_t N> std::string_view array(T (&buf)[N]);
  float f32();
  uint8_t uint8();
  int32_t int32();
};

} // namespace ioutil
