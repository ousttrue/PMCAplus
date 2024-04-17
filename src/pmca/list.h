#pragma once
#include <string>

#define NAME_LEN 128

struct LIST {
  unsigned int bone_count;
  char (*bone)[NAME_LEN];
  char (*bone_eng)[NAME_LEN];
  unsigned int skin_count;
  char (*skin)[NAME_LEN];
  char (*skin_eng)[NAME_LEN];
  unsigned int disp_count;
  char (*disp)[NAME_LEN];
  char (*disp_eng)[NAME_LEN];

  int load(const std::string &file_name);
};

// int delete_list(LIST *list);
