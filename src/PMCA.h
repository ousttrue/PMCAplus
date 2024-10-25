#pragma once
#include "mPMD.h"

DLL void Init_PMD();
DLL void Set_List(int bone_count, const char **bn, const char **bne,
                  int skin_count, const char **sn, const char **sne,
                  int bone_group_count, const char **gn, const char **gne);
DLL void CreateViewerThread();
DLL void MODEL_LOCK(int num);
DLL void Create_PMD(int num);
DLL void Load_PMD(int num, const char *str);
DLL void getInfo(int num, const char **name, const char **name_eng,
                 const char **comment, const char **comment_eng, int *vt_count,
                 int *face_count, int *mat_count, int *bone_count,
                 int *IK_count, int *skin_count, int *bone_group_count,
                 int *bone_disp_count, int *eng_support, int *rb_count,
                 int *joint_count, unsigned short **skin_index);
DLL void Add_PMD(int num, int add);
DLL int Marge_PMD(int num);
DLL int Sort_PMD(int num);
DLL int Copy_PMD(int src, int dst);
DLL void getMat(int num, int i, float *diff_col, float *alpha, float *spec,
                float *spec_col, float *mirr_col, int *toon, int *edge,
                int *face_count, const char **tex, const char **sph,
                const char **tex_path, const char **sph_path);
DLL void setMat(int num, int i, const float *diff_col, float alpha, float spec,
                const float *spec_col, const float *mirr_col, int toon,
                int edge, int face_count, const char *tex, const char *sph,
                const char *tex_path, const char *sph_path);
DLL void getToon(int num, char **toon);
DLL void getToonPath(int num, char **toon_path);
DLL void setToon(int num, const char **p);
DLL void setToonPath(int num, const char **p);
DLL bool getBone(int num, int i, const char **name, const char **name_eng,
                 int *parent, int *tail, int *type, int *IK, float *loc);
DLL void Resize_Model(int num, float size);
DLL void Resize_Bone(int num, const char *str, float len, float thi);
DLL void Move_Bone(int num, const char *str, float x, float y, float z);
DLL void Move_Model(int num, float x, float y, float z);
DLL void Update_Skin(int num);
DLL void Adjust_Joints(int num);
DLL void Set_Name_Comment(int num, const char *name, const char *name_eng,
                          const char *comment, const char *comment_eng);
DLL void PMD_view_set(int num, const char *str);
DLL void getWHT(int num, float *wht);
DLL void QuitViewerThread() ;
