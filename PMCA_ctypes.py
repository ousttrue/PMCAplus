from typing import Any
import ctypes

PMCA = ctypes.CDLL("zig-out/bin/PMCA.pyd")

# static PyMethodDef PMCAMethods[] = {
_getInfo = PMCA.getInfo
_getInfo.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_int),  # vt
    ctypes.POINTER(ctypes.c_int),  # face
    ctypes.POINTER(ctypes.c_int),  # mat
    ctypes.POINTER(ctypes.c_int),  # bone
    ctypes.POINTER(ctypes.c_int),  # IK
    ctypes.POINTER(ctypes.c_int),  # skin
    ctypes.POINTER(ctypes.c_int),  # bone_grup
    ctypes.POINTER(ctypes.c_int),  # bone_disp
    ctypes.POINTER(ctypes.c_int),  # eng_support
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.POINTER(ctypes.c_ushort)),
]
_getInfo.restype = None


def getInfo(num: int) -> dict[str, Any]:
    name = (ctypes.c_char_p * 1)()
    name_eng = (ctypes.c_char_p * 1)()
    comment = (ctypes.c_char_p * 1)()
    comment_eng = (ctypes.c_char_p * 1)()
    vt_count = (ctypes.c_int * 1)()
    face_count = (ctypes.c_int * 1)()
    mat_count = (ctypes.c_int * 1)()
    bone_count = (ctypes.c_int * 1)()
    IK_count = (ctypes.c_int * 1)()
    skin_count = (ctypes.c_int * 1)()
    bone_group_count = (ctypes.c_int * 1)()
    bone_disp_count = (ctypes.c_int * 1)()
    eng_support = (ctypes.c_int * 1)()
    rb_count = (ctypes.c_int * 1)()
    joint_count = (ctypes.c_int * 1)()
    skin_index = (ctypes.POINTER(ctypes.c_ushort) * 1)()

    _getInfo(
        num,
        name,
        name_eng,
        comment,
        comment_eng,
        vt_count,
        face_count,
        mat_count,
        bone_count,
        IK_count,
        skin_count,
        bone_group_count,
        bone_disp_count,
        eng_support,
        rb_count,
        joint_count,
        skin_index,
    )

    return {
        "name": name[0],
        "name_eng": name_eng[0],
        "comment": comment[0],
        "comment_eng": comment_eng[0],
        "vt_count": vt_count[0],
        "face_count": face_count[0],
        "mat_count": mat_count[0],
        "bone_count": bone_count[0],
        "IK_count": IK_count[0],
        "skin_count": skin_count[0],
        "bone_group_count": bone_group_count[0],
        "bone_disp_count": bone_disp_count[0],
        "eng_support": eng_support[0],
        "rb_count": rb_count[0],
        "joint_count": joint_count[0],
        "skin_index": skin_index[0],
    }


# {"getVt", getVt, METH_VARARGS, "Get Vertex of PMD"},
# {"getFace", getFace, METH_VARARGS, "Get Face of PMD"},


class Float3(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z


_getMat = PMCA.getMat
_getMat.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(Float3),
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(Float3),
    ctypes.POINTER(Float3),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
]
_getMat.restype = None


def getMat(num: int, i: int) -> dict[str, Any]:
    diff_col = (Float3 * 1)()
    alpha = (ctypes.c_float * 1)()
    spec = (ctypes.c_float * 1)()
    spec_col = (Float3 * 1)()
    mirr_col = (Float3 * 1)()
    toon = (ctypes.c_int * 1)()
    edge = (ctypes.c_int * 1)()
    face_count = (ctypes.c_int * 1)()
    tex = (ctypes.c_char_p * 1)()
    sph = (ctypes.c_char_p * 1)()
    tex_path = (ctypes.c_char_p * 1)()
    sph_path = (ctypes.c_char_p * 1)()
    _getMat(
        num,
        i,
        diff_col,
        alpha,
        spec,
        spec_col,
        mirr_col,
        toon,
        edge,
        face_count,
        tex,
        sph,
        tex_path,
        sph_path,
    )
    return {
        "diff_col": diff_col[0],
        "alpha": alpha[0],
        "spec": spec[0],
        "spec_col": spec_col[0],
        "mirr_col": mirr_col[0],
        "toon": toon[0],
        "edge": edge[0],
        "face_count": face_count[0],
        "tex": tex[0],
        "sph": sph[0],
        "tex_path": tex_path[0],
        "sph_path": sph_path[0],
    }


_getBone = PMCA.getBone
_getBone.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_float),
]
_getBone.restype = None


def getBone(num: int, i: int) -> dict[str, Any]:
    name = (ctypes.c_char_p * 1)()
    name_eng = (ctypes.c_char_p * 1)()
    parent = (ctypes.c_int * 1)()
    tail = (ctypes.c_int * 1)()
    type = (ctypes.c_int * 1)()
    IK = (ctypes.c_int * 1)()
    loc = (ctypes.c_float * 3)()
    _getBone(num, i, name, name_eng, parent, tail, type, IK, loc)
    return {
        "name": name[0],
        "name_eng": name_eng[0],
        "parent": parent[0],
        "tail": tail[0],
        "type": type[0],
        "IK": IK[0],
        "loc": loc[0],
    }


# {"getIK", getIK, METH_VARARGS, "Get IK_List of PMD"},
# {"getSkin", getSkin, METH_VARARGS, "Get Skin of PMD"},
# {"getSkindata", getSkindata, METH_VARARGS, "Get Skin_data of PMD"},
# {"getBone_group", getBone_group, METH_VARARGS, "Get Bone_group of PMD"},
# {"getBone_disp", getBone_disp, METH_VARARGS, "Get Bone_disp of PMD"},

getToon = PMCA.getToon
getToon.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
getToon.restype = None

getToonPath = PMCA.getToonPath
getToonPath.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
getToonPath.restype = None

# {"getRb", getRb, METH_VARARGS, "Get Rigid bodies of PMD"},
# {"getJoint", getJoint, METH_VARARGS, "Get Joints of PMD"},
# /******************************************************************/
# {"Create_FromInfo", Create_FromInfo, METH_VARARGS, "Create PMD"},
# {"setVt", setVt, METH_VARARGS, "Set Vertex of PMD"},
# {"setFace", setFace, METH_VARARGS, "Set Face of PMD"},

_setMat = PMCA.setMat
_setMat.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_float,
    ctypes.c_float,
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_char_p,
]
_setMat.restype = None


def setMat(
    num: int,
    i: int,
    diff_col: Float3,
    alpha: float,
    spec: float,
    spec_col: Float3,
    mirr_col: Float3,
    toon: int,
    edge: int,
    face_count: int,
    tex: str,
    sph: str,
    tex_path: str,
    sph_path: str,
):
    _setMat(
        num,
        i,
        (ctypes.c_float * 3)(*diff_col),
        alpha,
        spec,
        (ctypes.c_float * 3)(*spec_col),
        (ctypes.c_float * 3)(*mirr_col),
        toon,
        edge,
        face_count,
        tex.encode("cp932", "replace"),
        sph.encode("cp932", "replace"),
        tex_path.encode("cp932", "replace"),
        sph_path.encode("cp932", "replace"),
    )


# {"setBone", setBone, METH_VARARGS, "Set Bone of PMD"},
# {"setIK", setIK, METH_VARARGS, "Set IK_List of PMD"},
# {"setSkin", setSkin, METH_VARARGS, "Set Skin of PMD"},
# {"setSkindata", setSkindata, METH_VARARGS, "Set Skin_data of PMD"},
# {"setBone_group", setBone_group, METH_VARARGS, "Set Bone_group of PMD"},
# {"setBone_disp", setBone_disp, METH_VARARGS, "Set Bone_disp of PMD"},

setToon = PMCA.setToon
setToon.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
setToon.restype = None

setToonPath = PMCA.setToonPath
setToonPath.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
setToonPath.restype = None

# {"setRb", setRb, METH_VARARGS, "Set Rigid bodies of PMD"},
# {"setJoint", setJoint, METH_VARARGS, "Set Joints of PMD"},
# /***********************************************************************/

Set_List = PMCA.Set_List
Set_List.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_char_p),
    ctypes.POINTER(ctypes.c_char_p),
]
Set_List.restype = None

# /***********************************************************************/
# {"Set_Name_Comment", Set_Name_Comment, METH_VARARGS,
#  "Set Name and Comment"},
# /***********************************************************************/
# {"Init_PMD", Init_PMD, METH_VARARGS, "Initialize"},

Init_PMD = PMCA.Init_PMD
Init_PMD.argtypes = []
Init_PMD.restype = None

Load_PMD = PMCA.Load_PMD
Load_PMD.argtypes = [ctypes.c_int, ctypes.c_char_p]
Load_PMD.restype = None

# {"Write_PMD", Write_PMD, METH_VARARGS, "Write PMD from file"},

Add_PMD = PMCA.Add_PMD
Add_PMD.argtypes = [ctypes.c_int, ctypes.c_int]
Add_PMD.restype = None

Copy_PMD = PMCA.Copy_PMD
Copy_PMD.argtypes = [ctypes.c_int, ctypes.c_int]
Copy_PMD.restype = ctypes.c_int

Create_PMD = PMCA.Create_PMD
Create_PMD.argtypes = [ctypes.c_int]
Create_PMD.restype = None

Marge_PMD = PMCA.Marge_PMD
Marge_PMD.argtypes = [ctypes.c_int]
Marge_PMD.restype = ctypes.c_int

Sort_PMD = PMCA.Sort_PMD
Sort_PMD.argtypes = [ctypes.c_int]
Sort_PMD.restype = ctypes.c_int

# {"PMD_view_set", PMD_view_set, METH_VARARGS, "Set selected PMD to dispray"},
# /***********************************************************************/
# {"Resize_Model", Resize_Model, METH_VARARGS, "Resize_Model"},
# {"Move_Model", Move_Model, METH_VARARGS, "Move_Model"},
# {"Resize_Bone", Resize_Bone, METH_VARARGS, "Resize_Bone"},
# {"Move_Bone", Move_Bone, METH_VARARGS, "Move_Bone"},
# {"Update_Skin", Update_Skin, METH_VARARGS, "Update_Skin"},
# {"Adjust_Joints", Adjust_Joints, METH_VARARGS, "Adjust_Joints"},
#
# /***********************************************************************/

MODEL_LOCK = PMCA.MODEL_LOCK
MODEL_LOCK.argtypes = [ctypes.c_int]
MODEL_LOCK.restype = None

# {"getWHT", getWHT, METH_VARARGS, "get height, width, thickness from model"},
# /***********************************************************************/

CreateViewerThread = PMCA.CreateViewerThread
CreateViewerThread.argtypes = []
CreateViewerThread.restype = None

#  "CretateViewerThread"},
# {"WaitViewerThread", WaitViewerThread, METH_VARARGS, "WaitViewerThread"},
# {"QuitViewerThread", QuitViewerThread, METH_VARARGS, "QuitViewerThread"},
# {"KillViewerThread", KillViewerThread, METH_VARARGS, "KillViewerThread"},
# {"GetViewerThreadState", GetViewerThreadState, METH_VARARGS,
#  "GetViewerThreadState"},
# {"show3Dview", show3Dview, METH_VARARGS, "show3Dview"},
# {NULL, NULL, 0, NULL}};
