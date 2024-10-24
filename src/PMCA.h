#pragma once

#ifdef PMCA_BUILD
#define DLL __declspec(dllexport)
#else
#define DLL __declspec(dllimport)
#endif

DLL void Init_PMD();
DLL void Set_List(int bone_count, const char **bn, const char **bne,
                  int skin_count, const char **sn, const char **sne,
                  int bone_group_count, const char **gn, const char **gne);
