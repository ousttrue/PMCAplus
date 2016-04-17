#include "mPMD.h"

#ifdef __cplusplus
extern "C" {
#endif

int translate(MODEL *model, LIST *list, short mode);

int sort_bone(MODEL *model, LIST *list);
int update_bone_index(MODEL *model,int index[]);
int sort_skin(MODEL *model, LIST *list);
int sort_disp(MODEL *model, LIST *list);
int rename_tail(MODEL *model);


int scale_bone(MODEL *model, int index, double sx, double sy, double sz);
int bone_vec(MODEL *model, int index, double loc[], double vec[]);
double angle_from_vec(double u, double v);
int coordtrans(double array[][3], unsigned int len, double loc[], double mtr[3][3]);
int coordtrans_inv(double array[][3], unsigned int len, double loc[], double mtr[3][3]);
int move_bone(MODEL *model, unsigned int index, double diff[]);
int resize_model(MODEL *model, double size);
int index_bone(MODEL *model, const char bone[]);

int move_model(MODEL *model, double diff[]);

int marge_bone(MODEL *model);
int marge_mat(MODEL *model);
int marge_IK(MODEL *model);
int marge_bone_disp(MODEL *model);
int marge_rb(MODEL *model);

int update_skin(MODEL *model);
int adjust_joint(MODEL *model);

int show_detail(MODEL *model);


int add_PMD(MODEL *model, MODEL *add);

//dev_tool
int listup_bone(MODEL *model, const char file_name[]);

int get_file_name(char file_name[]);



#ifdef __cplusplus
}
#endif
