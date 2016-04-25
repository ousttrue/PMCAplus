#pragma once
#include <string>
#include <vector>
#include <algorithm>
#define USHORT_MAX 65535

#define PATH_LEN 256
#define NAME_LEN 128
#define COMMENT_LEN 256


template<int N>
class fixed_string
{
	static_assert(N > 0, "0 size");
	char m_str[N + 1];

public:
	fixed_string()
	{
		memset(m_str, 0, sizeof(m_str));
	}

	fixed_string(const fixed_string &src)
	{
		*this = src.c_str();
	}

	fixed_string(const char *src)
	{
		*this = src;
	}

	fixed_string& operator=(const char *src)
	{
		for (int i = 0; i < N; ++i) {
			m_str[i] = src[i];
			if (m_str[i] == '\0') {
				break;
			}
		}
		return *this;
	}

	bool operator==(const char *src)const
	{
		for (int i = 0; i < N; ++i) {
			if (m_str[i] != src[i]) {
				return false;
			}
			if (m_str[i] == '\0')break;
		}
		return true;
	}

	int capacity()const { return N; }

	int size()const {
		int i = 0;
		for (; i < N; ++i) {
			if (m_str[i] == '\0') {
				break;
			}
		}
		return i;
	}

	void clear()
	{
		m_str[0] = '\0';
	}

	const char *c_str()const { return m_str; }

	template<int M>
	int fread(FILE *fp)
	{
		char buf[M];
		int m = ::fread(buf, 1, M, fp);
		int i = 0;
		for (; i < std::min(N, m); ++i)
		{
			m_str[i] = buf[i];
			if (m_str[i] == '\0') {
				break;
			}
		}
		return i;
	}
};


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
	unsigned short bone_num[2];
	unsigned char bone_weight;
	unsigned char edge_flag;

    VERTEX()
    {
        bone_num[0]=bone_num[1]=0;
    }
};

struct MATERIAL 
{	/*70byte*/
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

struct BONE 
{	/*39byte*/
	char name[NAME_LEN];
	char name_eng[NAME_LEN];
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
{	/*11+2*IK_chain_len byte*/
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
{	/*25+16*skin_vt_count byte*/
	char name[NAME_LEN];
	char name_eng[NAME_LEN];
	unsigned char type;
	std::vector<SKIN_DATA> data;
};

struct BONE_GROUP 
{	/*3 byte*/
	char name[NAME_LEN];
	char name_eng[NAME_LEN];
};

struct BONE_DISP 
{	/*3 byte*/
	unsigned short index;
	unsigned char bone_group;

    BONE_DISP()
        : index(0)
    {}
};

struct RIGID_BODY 
{	//83byte
	char name[NAME_LEN];
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
{	//124byte
	char name[NAME_LEN];
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

	unsigned char bone_group_count;
	//char (*bone_group)[50];
	//char (*bone_group_eng)[50];
	BONE_GROUP *bone_group;
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

