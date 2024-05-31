#pragma once
#include <plog/Log.h>
#include <span>
#include <stdexcept>
#include <stdint.h>
#include <string.h>
#include <string>
#include <vector>

namespace ioutil {

std::vector<uint8_t> readfile(const std::string &path);

class binaryreader {
  std::span<const uint8_t> _data;
  int _pos = 0;

public:
  binaryreader(std::span<const uint8_t> data) : _data(data) {}

  bool isend() const { return _pos >= _data.size(); }

  void read(void *buf, int size) {
    if (_pos + size > _data.size()) {
      PLOG_ERROR << _pos << "+" << size << "out of range";
      throw std::runtime_error("out of range");
    }
    memcpy(buf, _data.data() + _pos, size);
    _pos += size;
  }

  template <typename T> void read(T &value) { read(&value, sizeof(value)); }

  std::span<const uint8_t> bytes(int size) {
    if (_pos + size > _data.size()) {
      PLOG_ERROR << _pos << "+" << size << "out of range";
      throw std::runtime_error("out of range");
    }
    auto span = _data.subspan(_pos, size);
    _pos += size;
    return span;
  }

  std::string_view str(int size) {
    if (_pos + size > _data.size()) {
      PLOG_ERROR << _pos << "+" << size << "out of range";
      throw std::runtime_error("out of range");
    }
    auto begin = (const char *)(_data.data() + _pos);
    std::string_view span(begin, begin + size);
    _pos += size;
    return span;
  }

  template <typename T> T value() {
    auto span = bytes(sizeof(T));
    // PLOG_DEBUG << span.size();
    T t;
    memcpy(&t, span.data(), span.size());
    // PLOG_DEBUG << t;
    return t;
  }

  float f32() { return value<float>(); }
  uint8_t u8() { return value<uint8_t>(); }
  uint16_t u16() { return value<uint16_t>(); }
  int32_t i32() { return value<int32_t>(); }
};

} // namespace ioutil
