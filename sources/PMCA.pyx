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
cdef extern from "fixed_string.h":
    cdef cppclass fixed_string100:
        const char* c_str();
    cdef cppclass fixed_string128:
        const char* c_str();
    cdef cppclass fixed_string256:
        const char* c_str();


cdef extern from "mPMD.h":
    enum:
        NAME_LEN=128
        COMMENT_LEN=256
        PATH_LEN=256

    cdef cppclass HEADER:
        fixed_string128 name;
        fixed_string256 comment;
        fixed_string128 name_eng;
        fixed_string256 comment_eng;
        fixed_string256 path;

    cdef cppclass VERTEX:
        float loc[3];
        float nor[3];
        float uv[2];
        unsigned short bone_num0;
        unsigned short bone_num1;
        unsigned char bone_weight;
        unsigned char edge_flag;

    cdef cppclass MATERIAL:
        float diffuse[3];
        float alpha;
        float spec;
        float spec_col[3];
        float mirror_col[3];
        unsigned char toon_index;
        unsigned char edge_flag;
        unsigned int vt_index_count;
        fixed_string128 tex;

    cdef cppclass BONE:
        fixed_string128 name;
        fixed_string128 name_eng;
        unsigned short PBone_index;
        unsigned short TBone_index;
        unsigned char type;
        unsigned short IKBone_index;
        float loc[3];

    cdef cppclass IK_LIST:
        unsigned short IKBone_index;
        unsigned short IKTBone_index;
        unsigned short iterations;
        float weight;
        vector[unsigned short] IKCBone_index;

    cdef cppclass SKIN_DATA:
        unsigned int index;
        float loc[3];

    cdef cppclass SKIN:
        fixed_string128 name;
        fixed_string128 name_eng;
        unsigned char type;
        vector[SKIN_DATA] data;

    cdef cppclass BONE_GROUP:
        fixed_string128 name;
        fixed_string128 name_eng;

    cdef cppclass BONE_DISP:
        unsigned short index;
        unsigned char bone_group;

    cdef cppclass RIGID_BODY:
        fixed_string128 name;
        unsigned short bone;
        unsigned char group;
        unsigned short target;
        unsigned char shape;
        float size[3];
        float loc[3];
        float rot[3];
        float property[5];
        unsigned char type;

    cdef cppclass JOINT:
        fixed_string128 name;
        unsigned int rbody[2];
        float loc[3];
        float rot[3];
        float limit[12];
        float spring[6];

    cdef cppclass MODEL:
        HEADER header;
        vector[VERTEX] vt;
        vector[unsigned short] vt_index;
        vector[MATERIAL] mat;
        vector[BONE] bone;
        vector[IK_LIST] IK_list;
        vector[SKIN] skin;
        vector[unsigned short] skin_index;
        vector[BONE_GROUP] bone_group;
        vector[BONE_DISP] bone_disp;
        unsigned char eng_support;
        fixed_string100 toon[10];
        vector[RIGID_BODY] rbody;
        vector[JOINT] joint;
        bool load(const string &path);
        bool save(const string &path);


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
            "name": model.header.name.c_str(),
            "name_eng": model.header.name_eng.c_str(),
            "comment": model.header.comment.c_str(),
            "comment_eng": model.header.comment_eng.c_str(),
            "path": model.header.path.c_str(),
            "vt_count": model.vt.size(),
            "face_count": model.vt_index.size()/3,
            "mat_count": model.mat.size(),
            "bone_count": model.bone.size(),
            "IK_count": model.IK_list.size(),
            "skin_count": model.skin.size(),
            "bone_group_count": model.bone_group.size(),
            "bone_disp_count": model.bone_disp.size(),

            "eng_support": model.eng_support,
            "rb_count": model.rbody.size(),
            "joint_count": model.joint.size(),
            "skin_index": model.skin_index,
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
            "bone_num1": v.bone_num0,
            "bone_num2": v.bone_num1,
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
            "tex": m.tex.c_str(),
    }

def getBone(index, b_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    b=model.bone[b_index]
    return {
            "name": b.name.c_str(),
            "name_eng": b.name_eng.c_str(),
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
            "len": ik.IKCBone_index.size(),
            "ite": ik.iterations,
            "weight": ik.weight,
            "child": ik.IKCBone_index
    }

def getSkin(index, s_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    cdef SKIN* s=&model.skin[s_index]
    return {
            "name": s.name.c_str(),
            "name_eng": s.name_eng.c_str(),
            "count": s.data.size(),
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
            "name": g.name.c_str(),
            "name_eng": g.name_eng.c_str()
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
    #return [x.c_str() for x in model.toon]

def getRb(index, rb_index):
    if index<0 or index>=g_model.size():
        return
    model = g_model[index];
    rb=model.rbody[rb_index]
    return {
            "name": rb.name.c_str(),
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
            "name": j.name.c_str(),
            "rbody": j.rbody,
            "loc": j.loc,
            "rot": j.rot,
            "limit": j.limit,
            "spring": j.spring,
            }

def setMat(index, m_index, 
        diffuse, alpha, 
        specularity, specular,
        ambient, toon_index,
        edge_flag, vt_index_count,
        name, comment, name_english, comment_english
        ):
    if index<0 or index>=g_model.size():
        return
    model = &g_model[index];

    cdef MATERIAL mat;
    mat.vt_index_count = vt_index_count*3;
    mat.diffuse=diffuse
    #mat.specular=specular
    #mat.ambient=ambient
    #strncpy(mat.tex, str[0], NAME_LEN);
    #strncpy(mat.sph, str[1], NAME_LEN);
    #strncpy(mat.tex_path, str[2], PATH_LEN);
    #strncpy(mat.sph_path, str[3], PATH_LEN);
    model.mat[m_index] = mat;

def setToon(index, toon):
    pass


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
    #model.header.name= name
    #model.header.comment= comment
    #model.header.name_eng= name_english
    #model.header.comment_eng= comment_english

def Init_PMD():
    g_model.resize(16)
    cdef MODEL model;
    for i in range(g_model.size()):
        g_model[i]=model

def Load_PMD(index, path):
    if index<0 or index>=g_model.size():
        return
    return g_model[index].load(path);

def Write_PMD(index, path):
    if index<0 or index>=g_model.size():
        return
    return g_model[index].save(path);

def Add_PMD(dst, src):
    if src<0 or src>=g_model.size():
        return
    if dst<0 or dst>=g_model.size():
        return
    add_PMD(&g_model[dst], &g_model[src]);

def Copy_PMD(src, dst):
    if src<0 or src>=g_model.size():
        return
    if dst<0 or dst>=g_model.size():
        return
    g_model[dst]=g_model[src]

def Create_PMD(index):
    if index<0 or index>=g_model.size():
        return
    cdef MODEL model;
    g_model[index]=model

def Marge_PMD(index):
    if index<0 or index>=g_model.size():
        return
    m=g_model[index]
    marge_bone(&m);
    marge_mat(&m);
    marge_IK(&m);
    marge_bone_disp(&m);
    marge_rb(&m);

def Sort_PMD(index):
    if index<0 or index>=g_model.size():
        return
    m=g_model[index]
    rename_tail(&m);
    marge_bone(&m);
    sort_bone(&m, &g_list);
    sort_skin(&m, &g_list);
    sort_disp(&m, &g_list);
    if m.bone[m.bone.size()-1].name.c_str()==b"-0":
        m.bone.resize(m.bone.size()-1);
    translate(&m, &g_list, 1);

def Resize_Model(index, scale):
    if index<0 or index>=g_model.size():
        return
    return resize_model(&g_model[index], scale);

def Move_Model(index, x, y, z):
    if index<0 or index>=g_model.size():
        return
    cdef array.array v=array.array('d', [x, y, z])
    return move_model(&g_model[index], v.data.as_doubles);

def Resize_Bone(index, name, length, thickness):
    if index<0 or index>=g_model.size():
        return
    m=g_model[index]
    for i in range(m.bone.size()):
        if m.bone[i].name.c_str()==name:
            return scale_bone(&m, i, thickness, length, thickness);

def Move_Bone(index, name, x, y, z):
    if index<0 or index>=g_model.size():
        return
    cdef array.array v=array.array('d', [x, y, z])
    m=g_model[index]
    for i in range(m.bone.size()):
        if m.bone[i].name.c_str()==name:
            return move_bone(&m, i, v.data.as_doubles);

def Update_Skin(index):
    if index<0 or index>=g_model.size():
        return
    return update_skin(&g_model[index]);

def Adjust_Joints(index):
    if index<0 or index>=g_model.size():
        return
    return adjust_joint(&g_model[index]);

def getWHT(index):
    if index<0 or index>=g_model.size():
        return
    cdef array.array min=array.array('d', [0, 0, 0])
    cdef array.array max=array.array('d', [0, 0, 0])
    m=g_model[index]
    for i in range(m.vt.size()):
        for j in range(3):
            value=m.vt[i].loc[j]
            if value<min[j]: min[j]=value
            elif value>max[j]: max[j]=value

    return [max[0]-min[0], max[1]-min[1], max[2]-min[2]]

