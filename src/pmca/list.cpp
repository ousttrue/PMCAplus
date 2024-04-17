#include "list.h"
#include "dbg.h"
#include <plog/Log.h>
#include <stdio.h>

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

  int i = 0;
  while (FGETS(str, 256, lst_file) != NULL) {
    if (strcmp(str, "skin\n") == 0)
      break;
    i++;
  }
  this->bone_count = i;
  i = 0;
  while (FGETS(str, 256, lst_file) != NULL) {
    if (strcmp(str, "bone_disp\n") == 0)
      break;
    i++;
  }
  this->skin_count = i;

  i = 0;
  while (FGETS(str, 256, lst_file) != NULL) {
    if (strcmp(str, "end\n") == 0)
      break;
    i++;
  }
  this->disp_count = i;

  fclose(lst_file);
  lst_file = fopen(file_name.c_str(), "r");
  if (lst_file == NULL) {
    PLOG_ERROR << "ファイルを開けません" << file_name;
    return 1;
  }

  printf("リストボーン数:%d\n", this->bone_count);
  printf("リスト表情数:%d\n", this->skin_count);
  printf("リスト表示枠数:%d\n", this->disp_count);

  this->bone = (char(*)[NAME_LEN])MALLOC((size_t)this->bone_count *
                                         sizeof(char) * NAME_LEN);
  this->bone_eng = (char(*)[NAME_LEN])MALLOC((size_t)this->bone_count *
                                             sizeof(char) * NAME_LEN);
  this->skin = (char(*)[NAME_LEN])MALLOC((size_t)this->skin_count *
                                         sizeof(char) * NAME_LEN);
  this->skin_eng = (char(*)[NAME_LEN])MALLOC((size_t)this->skin_count *
                                             sizeof(char) * NAME_LEN);
  this->disp = (char(*)[NAME_LEN])MALLOC((size_t)this->disp_count *
                                         sizeof(char) * NAME_LEN);
  this->disp_eng = (char(*)[NAME_LEN])MALLOC((size_t)this->disp_count *
                                             sizeof(char) * NAME_LEN);
  if (this->bone == NULL)
    return -1;
  if (this->bone_eng == NULL)
    return -1;
  if (this->skin == NULL)
    return -1;
  if (this->skin_eng == NULL)
    return -1;
  if (this->disp == NULL)
    return -1;
  if (this->disp_eng == NULL)
    return -1;

  FGETS(str, 256, lst_file);
  for (i = 0; i < this->bone_count; i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", this->bone[i], this->bone_eng[i]);
  }

  FGETS(str, 256, lst_file);
  for (i = 0; i < this->skin_count; i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", this->skin[i], this->skin_eng[i]);
  }

  FGETS(str, 256, lst_file);
  for (i = 0; i < this->disp_count; i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", this->disp[i], this->disp_eng[i]);
  }
  fclose(lst_file);

  return 0;
}

int delete_list(LIST *list) {

  list->bone_count = 0;
  list->skin_count = 0;
  list->disp_count = 0;

  FREE(list->bone);
  FREE(list->bone_eng);
  FREE(list->skin);
  FREE(list->skin_eng);
  FREE(list->disp);
  FREE(list->disp_eng);

  list->bone = NULL;
  list->bone_eng = NULL;
  list->skin = NULL;
  list->skin_eng = NULL;
  list->disp = NULL;
  list->disp_eng = NULL;

  return 0;
}
