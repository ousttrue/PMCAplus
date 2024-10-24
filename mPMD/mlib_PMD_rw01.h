#pragma once
#include "mPMD.h"
#define DLL

DLL int load_list(struct LIST *list, const char dir[]);
DLL int delete_list(struct LIST *list);
DLL int load_PMD(struct MODEL *model, const char file_name[]);
DLL int write_PMD(struct MODEL *model, const char file_name[]);
DLL int print_PMD(struct MODEL *model, const char file_name[]);
DLL int create_PMD(struct MODEL *model);
DLL int delete_PMD(struct MODEL *model);
DLL int copy_PMD(struct MODEL *out, struct MODEL *model);
DLL int add_PMD(struct MODEL *model, struct MODEL *add);
DLL int listup_bone(struct MODEL *model, const char file_name[]);
DLL int get_file_name(char file_name[]);
