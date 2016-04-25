#pragma once
#include <string>
#include <vector>
#include <algorithm>
#define USHORT_MAX 65535

#define PATH_LEN 256
#define NAME_LEN 128
#define COMMENT_LEN 256

#include "fixed_string.h"


struct HEADER 
{
	fixed_string<NAME_LEN> name;
	fixed_string<COMMENT_LEN> comment;
	fixed_string<NAME_LEN> name_eng;
	fixed_string<COMMENT_LEN> comment_eng;
	fixed_string<PATH_LEN> path;
};

struct VERTEX
{
	float loc[3];
	float nor[3];
	float uv[2];
	unsigned short bone_num0;
	unsigned short bone_num1;
	unsigned char bone_weight;
	unsigned char edge_flag;

    VERTEX()
		: bone_num0(0), bone_num1(1)
    {
    }
};

struct MATERIAL 
{
	float diffuse[3];
	float alpha;
	float spec;
	float spec_col[3];
	float mirror_col[3];
	unsigned char toon_index;
	unsigned char edge_flag;
	unsigned int vt_index_count;
	fixed_string<NAME_LEN> tex;
};

struct BONE 
{
	fixed_string<NAME_LEN> name;
	fixed_string<NAME_LEN> name_eng;
	unsigned short PBone_index;
	unsigned short TBone_index;
	unsigned char type;
	unsigned short IKBone_index;
	float loc[3];

    BONE()
        : PBone_index(0), TBone_index(0), IKBone_index(0)
    {}
};

struct IK_LIST 
{
	unsigned short IKBone_index;
	unsigned short IKTBone_index;
	unsigned short iterations;
	float weight;
	std::vector<unsigned short> IKCBone_index;

    IK_LIST()
        : IKCBone_index(0), IKTBone_index(0)
    {}
};

struct SKIN_DATA 
{
	unsigned int index;
	float loc[3];

    SKIN_DATA()
        : index(0)
    {}
};

struct SKIN 
{
	fixed_string<NAME_LEN> name;
	fixed_string<NAME_LEN> name_eng;
	unsigned char type;
	std::vector<SKIN_DATA> data;

	SKIN()
		: type(0)
	{}
};

struct BONE_GROUP 
{
	fixed_string<NAME_LEN> name;
	fixed_string<NAME_LEN> name_eng;
};

struct BONE_DISP 
{
	unsigned short index;
	unsigned char bone_group;

    BONE_DISP()
        : index(0)
    {}
};

struct RIGID_BODY 
{
	fixed_string<NAME_LEN> name;
	unsigned short bone;
	unsigned char group;
	unsigned short target;
	unsigned char shape;
	float size[3];	//w h d
	float loc[3];
	float rot[3];	//radian
	float property[5];	//mass damp rotdamp restitution friction
	unsigned char type;

    RIGID_BODY()
        : bone(0), group(0), target(0), shape(0), type(0)
    {}
};

struct JOINT 
{
	fixed_string<NAME_LEN> name;
	unsigned int rbody[2];
	float loc[3];
	float rot[3];	//radian
	float limit[12];	//lower_limit_loc upper_limit_loc lower_limit_rot upper_limit_rot
	float spring[6];	//loc rot

    JOINT()
    {
        rbody[0]=rbody[1]=0;
    }
};


struct MODEL 
{
	HEADER header;

	std::vector<VERTEX> vt;
	std::vector<unsigned short> vt_index;
	std::vector<MATERIAL> mat;
	std::vector<BONE> bone;
	std::vector<IK_LIST> IK_list;
	std::vector<SKIN> skin;
	std::vector<unsigned short> skin_index;
	std::vector<BONE_GROUP> bone_group;

	unsigned int bone_disp_count;
	BONE_DISP *bone_disp;
	//extention
	unsigned char eng_support;
	//ENGLISH eng;
	char toon[10][100];
	char toon_path[10][PATH_LEN];
	unsigned int rbody_count;
	RIGID_BODY *rbody;
	unsigned int joint_count;
	JOINT *joint;

    MODEL()
        : eng_support(0)
    {}
};
