# distutils: language = c++
# distutils: sources = [mPMD.cpp, mPMD_rw.cpp, mPMD_edit.cpp]
# cython: c_string_type=bytes, c_string_encoding=cp932

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
# mPMD_edit
##############################################################################
cdef extern from "mPMD_edit.h":
    cdef int add_PMD(MODEL *model, MODEL *add);
    cdef int marge_bone(MODEL *model);
    cdef int marge_mat(MODEL *model);
    cdef int marge_IK(MODEL *model);
    cdef int marge_bone_disp(MODEL *model);
    cdef int marge_rb(MODEL *model);
    cdef int translate(MODEL *model, short mode
            , vector[string] &b, vector[string] &be
            , vector[string] &s, vector[string] &se
            , vector[string] &d, vector[string] &de
            );
    cdef int sort_bone(MODEL *model
            , vector[string] &b, vector[string] &be
            , vector[string] &s, vector[string] &se
            , vector[string] &d, vector[string] &de
            );
    cdef int sort_skin(MODEL *model
            , vector[string] &b, vector[string] &be
            , vector[string] &s, vector[string] &se
            , vector[string] &d, vector[string] &de
            );
    cdef int sort_disp(MODEL *model
            , vector[string] &b, vector[string] &be
            , vector[string] &s, vector[string] &se
            , vector[string] &d, vector[string] &de
            );
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
cdef class Model:
    cdef MODEL *_thisptr;

    def __cinit__(self):
        self._thisptr=new MODEL()

    def __dealloc__(self):
        if self._thisptr != NULL:
            del self._thisptr

    def getInfo(self):
        return {
                "name": self._thisptr.header.name.c_str(),
                "name_eng": self._thisptr.header.name_eng.c_str(),
                "comment": self._thisptr.header.comment.c_str(),
                "comment_eng": self._thisptr.header.comment_eng.c_str(),
                "path": self._thisptr.header.path.c_str(),
                "vt_count": self._thisptr.vt.size(),
                "face_count": self._thisptr.vt_index.size()/3,
                "mat_count": self._thisptr.mat.size(),
                "bone_count": self._thisptr.bone.size(),
                "IK_count": self._thisptr.IK_list.size(),
                "skin_count": self._thisptr.skin.size(),
                "bone_group_count": self._thisptr.bone_group.size(),
                "bone_disp_count": self._thisptr.bone_disp.size(),

                "eng_support": self._thisptr.eng_support,
                "rb_count": self._thisptr.rbody.size(),
                "joint_count": self._thisptr.joint.size(),
                "skin_index": self._thisptr.skin_index,
        }

    def getVt(self, v_index):
        v=self._thisptr.vt[v_index]
        return {
                "loc": v.loc,
                "nor": v.nor,
                "uv": v.uv,
                "bone_num1": v.bone_num0,
                "bone_num2": v.bone_num1,
                "weight": v.bone_weight,
                "edge": v.edge_flag
        }

    def getFace(self, i_index):
        i=i_index*3
        return self._thisptr.vt_index[i], self._thisptr.vt_index[i+1], self._thisptr.vt_index[i+2]

    def getMat(self, m_index):
        m=self._thisptr.mat[m_index]
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

    def getBone(self, b_index):
        b=self._thisptr.bone[b_index]
        return {
                "name": b.name.c_str(),
                "name_eng": b.name_eng.c_str(),
                "parent": b.PBone_index,
                "tail": b.TBone_index,
                "type": b.type,
                "IK": b.IKBone_index,
                "loc": b.loc
        }

    def getIK(self, ik_index):
        ik=self._thisptr.IK_list[ik_index]
        return {
                "index": ik.IKBone_index,
                "tail": ik.IKTBone_index,
                "len": ik.IKCBone_index.size(),
                "ite": ik.iterations,
                "weight": ik.weight,
                "child": ik.IKCBone_index
        }

    def getSkin(self, s_index):
        s=self._thisptr.skin[s_index]
        return {
                "name": s.name.c_str(),
                "name_eng": s.name_eng.c_str(),
                "count": s.data.size(),
                "type": s.type
        }

    def getSkindata(self, s_index, offset_index):
        sd=self._thisptr.skin[s_index].data[offset_index]
        return {
                "index": sd.index,
                "loc": sd.loc,
        }

    def getBone_group(self, g_index):
        g=self._thisptr.bone_group[g_index]
        return {
                "name": g.name.c_str(),
                "name_eng": g.name_eng.c_str()
        }

    def getBone_disp(self, d_index):
        d=self._thisptr.bone_disp[d_index]
        return {
                "index": d.index,
                "bone_group": d.bone_group
        }

    def getToon(self):
        #return [x.c_str() for x in self._thisptr.toon]
        pass

    def getRb(self, rb_index):
        rb=self._thisptr.rbody[rb_index]
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

    def getJoint(self, j_index):
        j=self._thisptr.joint[j_index]
        return {
                "name": j.name.c_str(),
                "rbody": j.rbody,
                "loc": j.loc,
                "rot": j.rot,
                "limit": j.limit,
                "spring": j.spring,
                }

    def setMat(self, m_index, 
            diffuse, alpha, 
            specularity, specular,
            ambient, toon_index,
            edge_flag, vt_index_count,
            name, comment, name_english, comment_english
            ):
        cdef MATERIAL mat;
        mat.vt_index_count = vt_index_count*3;
        mat.diffuse=diffuse
        #mat.specular=specular
        #mat.ambient=ambient
        #strncpy(mat.tex, str[0], NAME_LEN);
        #strncpy(mat.sph, str[1], NAME_LEN);
        #strncpy(mat.tex_path, str[2], PATH_LEN);
        #strncpy(mat.sph_path, str[3], PATH_LEN);
        self._thisptr.mat[m_index] = mat;

    def setToon(self, toon):
        pass
        #for i, t in enumerate(toon):
        #    self._thisptr.toon[i]=t

    def Set_Name_Comment(self, name, comment, name_english, comment_english):
        #model.header.name= name
        #model.header.comment= comment
        #model.header.name_eng= name_english
        #model.header.comment_eng= comment_english
        pass

    def Load_PMD(self, path):
        return self._thisptr.load(path);

    def Write_PMD(self, path):
        return self._thisptr.save(path);

    def Add_PMD(self, Model src):
        add_PMD(self._thisptr, src._thisptr);

    def CopyTo(self, Model dst):
        dst._thisptr[0]=self._thisptr[0]

    def Marge_PMD(self):
        marge_bone(self._thisptr);
        marge_mat(self._thisptr);
        marge_IK(self._thisptr);
        marge_bone_disp(self._thisptr);
        marge_rb(self._thisptr);

    def Sort_PMD(self
            , bones, english_bones
            , skins, english_skins
            , disps, english_disps
            ):
        rename_tail(self._thisptr);
        marge_bone(self._thisptr);
        sort_bone(self._thisptr
                , bones, english_bones
                , skins, english_skins
                , disps, english_disps
                );
        sort_skin(self._thisptr
                , bones, english_bones
                , skins, english_skins
                , disps, english_disps
                );
        sort_disp(self._thisptr
                , bones, english_bones
                , skins, english_skins
                , disps, english_disps
                );
        if self._thisptr.bone[self._thisptr.bone.size()-1].name.c_str()==b"-0":
            self._thisptr.bone.resize(self._thisptr.bone.size()-1);
        translate(self._thisptr, 1
                , bones, english_bones
                , skins, english_skins
                , disps, english_disps
                );

    def Resize_Model(self, scale):
        return resize_model(self._thisptr, scale);

    def Move_Model(self, x, y, z):
        cdef array.array v=array.array('d', [x, y, z])
        return move_model(self._thisptr, v.data.as_doubles);

    def Resize_Bone(self, name, length, thickness):
        for i in range(self._thisptr.bone.size()):
            if self._thisptr.bone[i].name.c_str()==name:
                return scale_bone(self._thisptr, i, thickness, length, thickness);

    def Move_Bone(self, name, x, y, z):
        cdef array.array v=array.array('d', [x, y, z])
        for i in range(self._thisptr.bone.size()):
            if self._thisptr.bone[i].name.c_str()==name:
                return move_bone(self._thisptr, i, v.data.as_doubles);

    def Update_Skin(self):
        return update_skin(self._thisptr);

    def Adjust_Joints(self):
        return adjust_joint(self._thisptr);

    def getWHT(self):
        cdef array.array min=array.array('d', [0, 0, 0])
        cdef array.array max=array.array('d', [0, 0, 0])
        for i in range(self._thisptr.vt.size()):
            for j in range(3):
                value=self._thisptr.vt[i].loc[j]
                if value<min[j]: min[j]=value
                elif value>max[j]: max[j]=value

        return [max[0]-min[0], max[1]-min[1], max[2]-min[2]]

g_model=[Model() for x in range(16)]

