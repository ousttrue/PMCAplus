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
  list->bone_count = i;
  i = 0;
  while (FGETS(str, 256, lst_file) != NULL) {
    if (strcmp(str, "bone_disp\n") == 0)
      break;
    i++;
  }
  list->skin_count = i;

  i = 0;
  while (FGETS(str, 256, lst_file) != NULL) {
    if (strcmp(str, "end\n") == 0)
      break;
    i++;
  }
  list->disp_count = i;

  fclose(lst_file);
  lst_file = fopen(file_name, "r");
  if (lst_file == NULL) {
    printf("ファイル %s を開けません\n", file_name);
    return 1;
  }

  printf("リストボーン数:%d\n", list->bone_count);
  printf("リスト表情数:%d\n", list->skin_count);
  printf("リスト表示枠数:%d\n", list->disp_count);

  list->bone = (char(*)[NAME_LEN])MALLOC((size_t)list->bone_count *
                                         sizeof(char) * NAME_LEN);
  list->bone_eng = (char(*)[NAME_LEN])MALLOC((size_t)list->bone_count *
                                             sizeof(char) * NAME_LEN);
  list->skin = (char(*)[NAME_LEN])MALLOC((size_t)list->skin_count *
                                         sizeof(char) * NAME_LEN);
  list->skin_eng = (char(*)[NAME_LEN])MALLOC((size_t)list->skin_count *
                                             sizeof(char) * NAME_LEN);
  list->disp = (char(*)[NAME_LEN])MALLOC((size_t)list->disp_count *
                                         sizeof(char) * NAME_LEN);
  list->disp_eng = (char(*)[NAME_LEN])MALLOC((size_t)list->disp_count *
                                             sizeof(char) * NAME_LEN);
  if (list->bone == NULL)
    return -1;
  if (list->bone_eng == NULL)
    return -1;
  if (list->skin == NULL)
    return -1;
  if (list->skin_eng == NULL)
    return -1;
  if (list->disp == NULL)
    return -1;
  if (list->disp_eng == NULL)
    return -1;

  FGETS(str, 256, lst_file);
  for (i = 0; i < list->bone_count; i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", list->bone[i], list->bone_eng[i]);
  }

  FGETS(str, 256, lst_file);
  for (i = 0; i < list->skin_count; i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", list->skin[i], list->skin_eng[i]);
  }

  FGETS(str, 256, lst_file);
  for (i = 0; i < list->disp_count; i++) {
    FGETS(str, 256, lst_file);
    sscanf(str, "%s %s\n", list->disp[i], list->disp_eng[i]);
  }
  fclose(lst_file);

  return 0;
}
