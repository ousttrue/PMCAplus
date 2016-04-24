# distutils: language = c++
# distutils: sources = [mPMD.cpp, mList.cpp, mPMD_rw.cpp, mPMD_edit.cpp]

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool
from cpython cimport array

cdef array_slice(unsigned short *p, offset, count):
    return [p[i] for i in range(offset, offset+count)]

##############################################################################
# mPMD
##############################################################################
cdef extern from "mPMD.h":
    enum:
            NAME_LEN=128
            COMMENT_LEN=256
            PATH_LEN=256

    struct HEADER:
        char magic[4];
        float version;
        char name[NAME_LEN];
        char comment[COMMENT_LEN];
        char name_eng[NAME_LEN];
        char comment_eng[COMMENT_LEN];
        char path[PATH_LEN];

    struct VERTEX:
        float loc[3];
        float nor[3];
        float uv[2];
        unsigned short bone_num[2];
        unsigned char bone_weight;
        unsigned char edge_flag;

    struct MATERIAL:
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

    struct BONE:
        char name[NAME_LEN];
        char name_eng[NAME_LEN];
        unsigned short PBone_index;
        unsigned short TBone_index;
        unsigned char type;
        unsigned short IKBone_index;
        float loc[3];

    struct IK_LIST:
        unsigned short IKBone_index;
        unsigned short IKTBone_index;
        unsigned char IK_chain_len;
        unsigned short iterations;
        float weight;
        unsigned short *IKCBone_index;

    struct SKIN_DATA:
        unsigned int index;
        float loc[3];

    struct SKIN:
        char name[NAME_LEN];
        char name_eng[NAME_LEN];
        unsigned int skin_vt_count;
        unsigned char type;
        SKIN_DATA *data;

    struct BONE_GROUP:
        char name[NAME_LEN];
        char name_eng[NAME_LEN];

    struct BONE_DISP:
        unsigned short index;
        unsigned char bone_group;

    struct RIGID_BODY:
        char name[NAME_LEN];
        unsigned short bone;
        unsigned char group;
        unsigned short target;
        unsigned char shape;
        float size[3];	#w h d
        float loc[3];
        float rot[3];	#radian
        float property[5];	#mass damp rotdamp restitution friction
        unsigned char type;

    struct JOINT:
        char name[NAME_LEN];
        unsigned int rbody[2];
        float loc[3];
        float rot[3];	#radian
        float limit[12];	#lower_limit_loc upper_limit_loc lower_limit_rot upper_limit_rot
        float spring[6];	#loc rot

    struct MODEL:
        HEADER header;
        unsigned int vt_count;
        VERTEX *vt;
        unsigned int vt_index_count;
        unsigned short *vt_index;
        unsigned int mat_count;
        MATERIAL *mat;
        unsigned short bone_count;
        BONE *bone;
        unsigned short IK_count;
        IK_LIST *IK_list;
        unsigned short skin_count;
        SKIN *skin;
        unsigned char skin_disp_count;
        unsigned short *skin_index;
        unsigned char bone_group_count;
        #char (*bone_group)[50];
        #char (*bone_group_eng)[50];
        BONE_GROUP *bone_group;
        unsigned int bone_disp_count;
        BONE_DISP *bone_disp;
        #extention
        unsigned char eng_support;
        #ENGLISH eng;
        char toon[10][100];
        char toon_path[10][PATH_LEN];
        unsigned int rbody_count;
        RIGID_BODY *rbody;
        unsigned int joint_count;
        JOINT *joint;


##############################################################################
# mList
##############################################################################
cdef extern from "mList.h":

    cdef struct NameWithEnglish:
        string name;
        string english;

    cdef cppclass LIST:
        vector[NameWithEnglish] bone;
        vector[NameWithEnglish] skin;
        vector[NameWithEnglish] disp;
        bool load(const string &dir);
        void clear();


##############################################################################
# mPMD_rw
##############################################################################
cdef extern from "mPMD_rw.h":
    cdef int load_PMD(MODEL *model, const char *path);
    cdef int write_PMD(MODEL *model, const char *path);
    cdef int print_PMD(MODEL *model, const char *path);
    cdef int create_PMD(MODEL *model);
    cdef int delete_PMD(MODEL *model);
    cdef int copy_PMD(MODEL *dst, MODEL *src);


##############################################################################
# mPMD_edit
##############################################################################
cdef extern from "mPMD_edit.h":
    cdef int add_PMD(MODEL *model, MODEL *add);
    cdef int marge_bone(MODEL *model);
    cdef int marge_mat(MODEL *model);
    cdef int marge_IK(MODEL *model);
    cdef int marge_bone_disp(MODEL *model);
    cdef int marge_rb(MODEL *model);
    cdef int translate(MODEL *model, LIST *list, short mode);
    cdef int sort_bone(MODEL *model, LIST *list);
    cdef int update_bone_index(MODEL *model, int *index);
    cdef int sort_skin(MODEL *model, LIST *list);
    cdef int sort_disp(MODEL *model, LIST *list);
    cdef int rename_tail(MODEL *model);
    cdef int scale_bone(MODEL *model, int index, double sx, double sy, double sz);
    cdef int bone_vec(MODEL *model, int index, double loc[], double vec[]);
    cdef double angle_from_vec(double u, double v);
    cdef int coordtrans(double array[][3], unsigned int len, double loc[], double mtr[3][3]);
    cdef int coordtrans_inv(double array[][3], unsigned int len, double loc[], double mtr[3][3]);
    cdef int move_bone(MODEL *model, unsigned int index, double diff[]);
    cdef int resize_model(MODEL *model, double size);
    cdef int index_bone(MODEL *model, const char bone[]);

    cdef int move_model(MODEL *model, double diff[]);
    cdef int update_skin(MODEL *model);
    cdef int adjust_joint(MODEL *model);

    cdef int show_detail(MODEL *model);



##############################################################################
# definition
##############################################################################
cdef vector[MODEL] g_model;

def getInfo(index):
    if index<0 or index>=g_model.size():
        return
    model=g_model[index]
    return {
            "name": model.header.name,
            "name_eng": model.header.name_eng,
            "comment": model.header.comment,
            "comment_eng": model.header.comment_eng,
            "vt_count": model.vt_count,
            "face_count": model.vt_index_count/3,
            "mat_count": model.mat_count,
            "bone_count": model.bone_count,
            "IK_count": model.IK_count,
            "skin_count": model.skin_count,
            "bone_group_count": model.bone_group_count,
            "bone_disp_count": model.bone_disp_count,

            "eng_support": model.eng_support,
            "rb_count": model.rbody_count,
            "joint_count": model.joint_count,
            "skin_index": array_slice(model.skin_index, 0, model.skin_disp_count)
    }

def getVt(index, v_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    v=model.vt[v_index]
    return {
            "loc": v.loc,
            "nor": v.nor,
            "uv": v.uv,
            "bone_num1": v.bone_num[0],
            "bone_num2": v.bone_num[1],
            "weight": v.bone_weight,
            "edge": v.edge_flag
    }

def getFace(index, i_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    i=i_index*3
    return model.vt_index[i], model.vt_index[i+1], model.vt_index[i+2]

def getMat(index, m_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    m=model.mat[m_index]
    return {
            "diff_col": m.diffuse,
            "alpha": m.alpha,
            "spec": m.spec,
            "spec_col": m.spec_col,
            "mirr_col": m.mirror_col,
            "toon": m.toon_index,
            "edge": m.edge_flag,
            "face_count": m.vt_index_count/3,
            "tex": m.tex,
            "sph": m.sph,
            "tex_path": m.tex_path,
            "sph_path": m.sph_path
    }

def getBone(index, b_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    b=model.bone[b_index]
    return {
            "name": b.name,
            "name_eng": b.name_eng,
            "parent": b.PBone_index,
            "tail": b.TBone_index,
            "type": b.type,
            "IK": b.IKBone_index,
            "loc": b.loc
    }

def getIK(index, ik_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    cdef IK_LIST* ik=&model.IK_list[ik_index]
    return {
            "index": ik.IKBone_index,
            "tail": ik.IKTBone_index,
            "len": ik.IK_chain_len,
            "ite": ik.iterations,
            "weight": ik.weight,
            "child": array_slice(ik.IKCBone_index, 0, ik.IK_chain_len)
    }

def getSkin(index, s_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    cdef SKIN* s=&model.skin[s_index]
    return {
            "name": s.name,
            "name_eng": s.name_eng,
            "count": s.skin_vt_count,
            "type": s.type
    }

def getSkindata(index, s_index, offset_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    sd=model.skin[s_index].data[offset_index]
    return {
            "index": sd.index,
            "loc": sd.loc,
    }

def getBone_group(index, g_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    g=model.bone_group[g_index]
    return {
            "name": g.name,
            "name_eng": g.name_eng
    }

def getBone_disp(index, d_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    d=model.bone_disp[d_index]
    return {
            "index": d.index,
            "bone_group": d.bone_group
    }

def getToon(index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    return model.toon

def getToonPath(index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    return model.toon_path

def getRb(index, rb_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    rb=model.rbody[rb_index]
    return {
            "name": rb.name,
            "bone": rb.bone,
            "group": rb.group,
            "target": rb.target,
            "shape": rb.shape,
            "size": rb.size,
            "loc": rb.loc,
            "rot": rb.rot,
            "prop": rb.property,
            "t": rb.type
            }

def getJoint(index, j_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    j=model.joint[j_index]
    return {
            "name": j.name,
            "rbody": j.rbody,
            "loc": j.loc,
            "rot": j.rot,
            "limit": j.limit,
            "spring": j.spring,
            }

cdef LIST g_list

def Set_List(bone_count, bone_names, bone_english_names,
        skin_count, skin_names, skin_english_names,
        disp_count, disp_names, disp_english_names):

    g_list.clear();

    g_list.bone.resize(bone_count)
    for i in range(bone_count):
        g_list.bone[i].name=bone_names[i]
        g_list.bone[i].english=bone_english_names[i]

    g_list.skin.resize(skin_count)
    for i in range(skin_count):
        g_list.skin[i].name=skin_names[i]
        g_list.skin[i].english=skin_english_names[i]

    g_list.disp.resize(disp_count)
    for i in range(disp_count):
        g_list.disp[i].name=disp_names[i]
        g_list.disp[i].english=disp_english_names[i]

def Set_Name_Comment(index, name, comment, name_english, comment_english):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index]
    model.header.name= name
    model.header.comment= comment
    model.header.name_eng= name_english
    model.header.comment_eng= comment_english

def Init_PMD():
    g_model.resize(16)
    for i in range(g_model.size()):
        create_PMD(&g_model[i]);

def Load_PMD(index, path):
    delete_PMD(&g_model[index]);
    return load_PMD(&g_model[index], path);

def Write_PMD(index, path):
    return write_PMD(&g_model[index], path);

def Add_PMD(dst, src):
    cdef MODEL model;
    create_PMD(&model);
    add_PMD(&g_model[dst], &g_model[src]);
    delete_PMD(&model);

def Copy_PMD(src, dst):
    delete_PMD(&g_model[dst]);
    return copy_PMD(&g_model[dst], &g_model[src]);

def Create_PMD(index):
    return delete_PMD(&g_model[index]);

def Marge_PMD(index):
    m=g_model[index]
    marge_bone(&m);
    marge_mat(&m);
    marge_IK(&m);
    marge_bone_disp(&m);
    marge_rb(&m);

def Sort_PMD(index):
    m=g_model[index]
    rename_tail(&m);
    marge_bone(&m);
    sort_bone(&m, &g_list);
    sort_skin(&m, &g_list);
    sort_disp(&m, &g_list);
    if m.bone[m.bone_count-1].name==b"-0":
        m.bone_count-=1;
    translate(&m, &g_list, 1);

def Resize_Model(index, scale):
    return resize_model(&g_model[index], scale);

def Move_Model(index, x, y, z):
    cdef array.array v=array.array('d', [x, y, z])
    return move_model(&g_model[index], v.data.as_doubles);

def Resize_Bone(index, name, length, thickness):
    m=g_model[index]
    for i in range(m.bone_count):
        if m.bone[i].name==name:
            return scale_bone(&m, i, thickness, length, thickness);

def Move_Bone(index, name, x, y, z):
    cdef array.array v=array.array('d', [x, y, z])
    m=g_model[index]
    for i in range(m.bone_count):
        if m.bone[i].name==name:
            return move_bone(&m, i, v.data.as_doubles);

def Update_Skin(index):
    return update_skin(&g_model[index]);

def Adjust_Joints(index):
    return adjust_joint(&g_model[index]);

def getWHT(index):
    cdef array.array min=array.array('d', [0, 0, 0])
    cdef array.array max=array.array('d', [0, 0, 0])
    m=g_model[index]
    for i in range(m.vt_count):
        for j in range(3):
            value=m.vt[i].loc[j]
            if value<min[j]: min[j]=value
            elif value>max[j]: max[j]=value

    return [max[0]-min[0], max[1]-min[1], max[2]-min[2]]

