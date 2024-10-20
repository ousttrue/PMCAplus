from typing import TypedDict, Any

class InfoDict(TypedDict):
    name: bytes
    name_eng: bytes
    comment: bytes
    comment_eng: bytes
    eng_support: int
    skin_index: int
    mat_count: int

def getInfo(slot: int) -> dict[str, Any]:
    """
    Get Info of PMD
    """
    ...

# {"getVt", getVt, METH_VARARGS, "Get Vertex of PMD"},
# {"getFace", getFace, METH_VARARGS, "Get Face of PMD"},
def getMat(slot: int, material: int) -> dict[str, Any]:
    """
    Get Material of PMD
    """
    ...

# {"getBone", getBone, METH_VARARGS, "Get Bone of PMD"},
# {"getIK", getIK, METH_VARARGS, "Get IK_List of PMD"},
# {"getSkin", getSkin, METH_VARARGS, "Get Skin of PMD"},
# {"getSkindata", getSkindata, METH_VARARGS, "Get Skin_data of PMD"},
# {"getBone_group", getBone_group, METH_VARARGS, "Get Bone_group of PMD"},
# {"getBone_disp", getBone_disp, METH_VARARGS, "Get Bone_disp of PMD"},
# {"getToon", getToon, METH_VARARGS, "Get Toon textures of PMD"},
# {"getToonPath", getToonPath, METH_VARARGS, "Get Toon textures path of PMD"},
# {"getRb", getRb, METH_VARARGS, "Get Rigid bodies of PMD"},
# {"getJoint", getJoint, METH_VARARGS, "Get Joints of PMD"},
# /******************************************************************/
# {"Create_FromInfo", Create_FromInfo, METH_VARARGS, "Create PMD"},
# {"setVt", setVt, METH_VARARGS, "Set Vertex of PMD"},
# {"setFace", setFace, METH_VARARGS, "Set Face of PMD"},
# {"setMat", setMat, METH_VARARGS, "Set Material of PMD"},
# {"setBone", setBone, METH_VARARGS, "Set Bone of PMD"},
# {"setIK", setIK, METH_VARARGS, "Set IK_List of PMD"},
# {"setSkin", setSkin, METH_VARARGS, "Set Skin of PMD"},
# {"setSkindata", setSkindata, METH_VARARGS, "Set Skin_data of PMD"},
# {"setBone_group", setBone_group, METH_VARARGS, "Set Bone_group of PMD"},
# {"setBone_disp", setBone_disp, METH_VARARGS, "Set Bone_disp of PMD"},
# {"setToon", setToon, METH_VARARGS, "Set Toon textures of PMD"},
# {"setToonPath", setToonPath, METH_VARARGS, "Set Toon textures path of PMD"},
# {"setRb", setRb, METH_VARARGS, "Set Rigid bodies of PMD"},
# {"setJoint", setJoint, METH_VARARGS, "Set Joints of PMD"},
# /***********************************************************************/

def Set_List(
    bone_count: int,
    bone_name_list: list[bytes],
    bone_name_eng_list: list[bytes],
    skin_count: int,
    skin_name_list: list[bytes],
    skin_name_eng_list: list[bytes],
    bone_group_count: int,
    bone_group_name_list: list[bytes],
    bone_group_name_eng_list: list[bytes],
) -> None:
    """
    Set List of bone or things
    """
    ...

# /***********************************************************************/
# {"Set_Name_Comment", Set_Name_Comment, METH_VARARGS,
#  "Set Name and Comment"},
# /***********************************************************************/

def Init_PMD() -> None:
    """
    Initialize
    """
    ...

def Load_PMD(slot: int, path: bytes) -> None:
    """
    Load PMD from file
    """
    ...

# {"Write_PMD", Write_PMD, METH_VARARGS, "Write PMD from file"},

def Add_PMD(src: int, dst: int) -> None: ...
def Copy_PMD(src: int, dst: int) -> None: ...
def Create_PMD(slot: int) -> None:
    """
    Create empty PMD
    """
    ...

def Marge_PMD(slot: int) -> None: ...

# {"Sort_PMD", Sort_PMD, METH_VARARGS, "Sort PMD"},

def PMD_view_set(slot: int, mode: str) -> None:
    """
    Set selected PMD to dispray
    """
    ...

# {"Resize_Model", Resize_Model, METH_VARARGS, "Resize_Model"},
def Move_Model(slot: int, x: float, y: float, z: float) -> None: ...

# {"Resize_Bone", Resize_Bone, METH_VARARGS, "Resize_Bone"},
def Move_Bone(slot: int, bone: bytes, x: float, y: float, z: float) -> None: ...
def Update_Skin(slot: int) -> None: ...
def Adjust_Joints(slot: int) -> None: ...
def MODEL_LOCK(lock: int) -> None:
    """
    Lock/Unlock model
    """
    ...

def getWHT(slot: int) -> tuple[float, float, float]:
    """
    get height, width, thickness from model
    """
    ...

def CretateViewerThread() -> None: ...

# {"WaitViewerThread", WaitViewerThread, METH_VARARGS, "WaitViewerThread"},
def QuitViewerThread() -> None: ...

# {"KillViewerThread", KillViewerThread, METH_VARARGS, "KillViewerThread"},
# {"GetViewerThreadState", GetViewerThreadState, METH_VARARGS,
#  "GetViewerThreadState"},
# {"show3Dview", show3Dview, METH_VARARGS, "show3Dview"},
