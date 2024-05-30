#include "list.h"
#include <plog/Log.h>
#include <stdio.h>

void *FGETS(char *p, size_t s, FILE *fp) {
  auto r = fgets(p, s, fp);
  if (r == NULL) {
    PLOG_ERROR << "ファイル読み込みに失敗";
    throw std::runtime_error("ファイル読み込みに失敗");
  }

  return r;
}

int LIST::load(const std::string &file_name) {

  if (file_name.empty()) {
    printf("ファイル名がありません\n");
    return 1;
  }

  auto lst_file = fopen(file_name.c_str(), "r");
  if (lst_file == NULL) {
    LOG_ERROR << "ファイル を開けません:" << file_name;
    return 1;
  }

  char str[256];
  FGETS(str, 256, lst_file);

  {
    int i = 0;
    while (FGETS(str, 256, lst_file) != NULL) {
      if (strcmp(str, "skin\n") == 0)
        break;
      i++;
    }
    this->bone.resize(i);
    this->bone_eng.resize(i);
  }

  {
    int i = 0;
    while (FGETS(str, 256, lst_file) != NULL) {
      if (strcmp(str, "bone_disp\n") == 0)
        break;
      i++;
    }
    this->skin.resize(i);
    this->skin_eng.resize(i);
  }

  {
    int i = 0;
    while (FGETS(str, 256, lst_file) != NULL) {
      if (strcmp(str, "end\n") == 0)
        break;
      i++;
    }
    this->disp.resize(i);
    this->disp_eng.resize(i);
  }

  fclose(lst_file);
  lst_file = fopen(file_name.c_str(), "r");
  if (lst_file == NULL) {
    PLOG_ERROR << "ファイルを開けません" << file_name;
    return 1;
  }

  printf("リストボーン数:%zu\n", this->bone.size());
  printf("リスト表情数:%zu\n", this->skin.size());
  printf("リスト表示枠数:%zu\n", this->disp.size());

  FGETS(str, 256, lst_file);
  for (int i = 0; i < this->bone.size(); i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", this->bone[i].data(), this->bone_eng[i].data());
  }

  FGETS(str, 256, lst_file);
  for (int i = 0; i < this->skin.size(); i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", this->skin[i].data(), this->skin_eng[i].data());
  }

  FGETS(str, 256, lst_file);
  for (int i = 0; i < this->disp.size(); i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", this->disp[i].data(), this->disp_eng[i].data());
  }
  fclose(lst_file);

  return 0;
}

int delete_list(LIST *list) {
  list->bone.clear();
  list->bone_eng.clear();
  list->skin.clear();
  list->skin_eng.clear();
  list->disp.clear();
  list->disp_eng.clear();
  return 0;
}
