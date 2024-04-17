#pragma once
#include <array>
#include <string>
#include <vector>

#define NAME_LEN 128

struct LIST {
  std::vector<std::array<char, NAME_LEN>> bone;
  std::vector<std::array<char, NAME_LEN>> bone_eng;

  std::vector<std::array<char, NAME_LEN>> skin;
  std::vector<std::array<char, NAME_LEN>> skin_eng;

  std::vector<std::array<char, NAME_LEN>> disp;
  std::vector<std::array<char, NAME_LEN>> disp_eng;

  int load(const std::string &file_name);
};

// int delete_list(LIST *list);
