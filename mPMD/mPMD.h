#pragma once
#define USHORT_MAX 65535

#define PATH_LEN 256
#define NAME_LEN 128
#define COMMENT_LEN 256

#ifdef PMCA_BUILD
#define DLL __declspec(dllexport)
#else
#define DLL __declspec(dllimport)
#endif

struct HEADER { /*283byte*/
  char magic[4];
  float version;
  char name[NAME_LEN];
  char comment[COMMENT_LEN];
  char name_eng[NAME_LEN];
  char comment_eng[COMMENT_LEN];
  char path[PATH_LEN];
};

struct VERTEX { /*38byte*/
  float loc[3];
  float nor[3];
  float uv[2];
  unsigned short bone_num[2];
  unsigned char bone_weight;
  unsigned char edge_flag;
};

struct MATERIAL { /*70byte*/
  float diffuse[3];
  float alpha;
  float spec;
  float spec_col[3];
  float mirror_col[3];
  unsigned char toon_index;
  unsigned char edge_flag;
  unsigned int vt_index_count;
  char tex[NAME_LEN];
  char sph[NAME_LEN];
  char tex_path[PATH_LEN];
  char sph_path[PATH_LEN];
};

struct BONE { /*39byte*/
  char name[NAME_LEN];
  char name_eng[NAME_LEN];
  unsigned short PBone_index;
  unsigned short TBone_index;
  unsigned char type;
  unsigned short IKBone_index;
  float loc[3];
};

struct IK_LIST { /*11+2*IK_chain_len byte*/
  unsigned short IKBone_index;
  unsigned short IKTBone_index;
  unsigned char IK_chain_len;
  unsigned short iterations;
  float weight;
  unsigned short *IKCBone_index;
};

struct SKIN_DATA { /*16byte*/
  unsigned int index;
  float loc[3];
};

struct SKIN { /*25+16*skin_vt_count byte*/
  char name[NAME_LEN];
  char name_eng[NAME_LEN];
  unsigned int skin_vt_count;
  unsigned char type;
  struct SKIN_DATA *data;
};

struct BONE_GROUP { /*3 byte*/
  char name[NAME_LEN];
  char name_eng[NAME_LEN];
};

struct BONE_DISP { /*3 byte*/
  unsigned short index;
  unsigned char bone_group;
};

struct RIGID_BODY { // 83byte
  char name[NAME_LEN];
  unsigned short bone;
  unsigned char group;
  unsigned short target;
  unsigned char shape;
  float size[3]; // w h d
  float loc[3];
  float rot[3];      // radian
  float property[5]; // mass damp rotdamp restitution friction
  unsigned char type;
};

struct JOINT { // 124byte
  char name[NAME_LEN];
  unsigned int rbody[2];
  float loc[3];
  float rot[3];    // radian
  float limit[12]; // lower_limit_loc upper_limit_loc lower_limit_rot
                   // upper_limit_rot
  float spring[6]; // loc rot
};

struct MODEL {
  struct HEADER header;
  unsigned int vt_count;
  struct VERTEX *vt;
  unsigned int vt_index_count;
  unsigned short *vt_index;
  unsigned int mat_count;
  struct MATERIAL *mat;
  unsigned short bone_count;
  struct BONE *bone;
  unsigned short IK_count;
  struct IK_LIST *IK_list;
  unsigned short skin_count;
  struct SKIN *skin;
  unsigned char skin_disp_count;
  unsigned short *skin_index;
  unsigned char bone_group_count;
  // char (*bone_group)[50];
  // char (*bone_group_eng)[50];
  struct BONE_GROUP *bone_group;
  unsigned int bone_disp_count;
  struct BONE_DISP *bone_disp;
  // extention
  unsigned char eng_support;
  // ENGLISH eng;
  char toon[10][100];
  char toon_path[10][PATH_LEN];
  unsigned int rbody_count;
  struct RIGID_BODY *rbody;
  unsigned int joint_count;
  struct JOINT *joint;
};

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
};
