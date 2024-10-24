#pragma once
#include "mPMD.h"
#include <stddef.h>

DLL int translate(struct MODEL *model, struct LIST *list, short mode);

DLL int sort_bone(struct MODEL *model, struct LIST *list);
DLL int update_bone_index(struct MODEL *model, int index[]);
DLL int sort_skin(struct MODEL *model, struct LIST *list);
DLL int sort_disp(struct MODEL *model, struct LIST *list);
DLL int rename_tail(struct MODEL *model);

DLL int scale_bone(struct MODEL *model, int index, double sx, double sy,
                   double sz);
DLL int bone_vec(struct MODEL *model, int index, double loc[], double vec[]);
DLL double angle_from_vec(double u, double v);
DLL int coordtrans(double array[][3], unsigned int len, double loc[],
                   double mtr[3][3]);
DLL int coordtrans_inv(double array[][3], unsigned int len, double loc[],
                       double mtr[3][3]);
DLL int move_bone(struct MODEL *model, unsigned int index, double diff[]);
DLL int resize_model(struct MODEL *model, double size);
DLL int index_bone(struct MODEL *model, const char bone[]);

DLL int move_model(struct MODEL *model, double diff[]);

DLL int marge_bone(struct MODEL *model);
DLL int marge_mat(struct MODEL *model);
DLL int marge_IK(struct MODEL *model);
DLL int marge_bone_disp(struct MODEL *model);
DLL int marge_rb(struct MODEL *model);

DLL int update_skin(struct MODEL *model);
DLL int adjust_joint(struct MODEL *model);

DLL int show_detail(struct MODEL *model);

