from typing import List, TypedDict

class InfoData(TypedDict):
    name: bytes
    name_eng: bytes
    comment: bytes
    comment_eng: bytes
    eng_support: int
    skin_index: list[int]
    vt_count: int
    face_count: int
    mat_count: int
    bone_count: int
    IK_count: int
    skin_count: int
    bone_group_count: int
    bone_disp_count: int
    rb_count: int
    joint_count: int

def getInfo(model: int) -> InfoData:
    """
    Get Info of PMD"
    """
    ...

class VtData(TypedDict):
    loc: tuple[float, float, float]

def getVt(model: int, index: int) -> VtData | None:
    """
    Get Vertex of PMD"
    """
    ...

def getFace(model: int, index: int) -> tuple[int, int, int] | None:
    """
    Get Face of PMD"
    """
    ...

class MaterialData(TypedDict):
    diff_col: tuple[float, float, float]
    alpha: float
    spec: float
    spec_col: tuple[float, float, float]
    mirr_col: tuple[float, float, float]
    toon: int
    edge: float
    face_count: int
    tex: bytes
    sph: bytes
    tex_path: bytes
    sph_path: bytes

def getMat(model: int, index: int) -> MaterialData | None:
    """
    Get Material of PMD"
    """
    ...

class BoneData(TypedDict):
    name: bytes
    name_eng: bytes
    parent: int
    tail: int
    type: int
    IK: int
    loc: tuple[float, float, float]

def getBone(model: int, index: int) -> BoneData | None:
    """
    Get Bone of PMD"
    """
    ...

class IkData(TypedDict):
    index: int
    tail: int
    len: int
    ite: int
    weight: float
    child: int

def getIK(model: int, index: int) -> IkData | None:
    """
    Get IK_List of PMD"
    """
    ...

class SkinData(TypedDict):
    name: bytes
    name_eng: bytes
    count: int
    type: int

def getSkin(model: int, index: int) -> SkinData | None:
    """
    Get Skin of PMD"
    """
    ...

class SkinDataData(TypedDict):
    index: int
    loc: tuple[float, float, float]

def getSkindata(model: int, index: int, j: int) -> SkinDataData | None:
    """
    Get Skin_data of PMD"
    """
    ...

class BoneGroupData(TypedDict):
    pass

def getBone_group(model: int, index: int) -> BoneGroupData | None:
    """
    Get Bone_group of PMD"
    """
    ...

class BoneDispData(TypedDict):
    index: int
    bone_group: int

def getBone_disp(model: int, index: int) -> BoneDispData | None:
    """
    Get Bone_disp of PMD"
    """
    ...

def getToon(
    model: int,
) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes] | None:
    """
    Get Toon textures of PMD"
    """
    ...

def getToonPath(
    model: int,
) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes] | None:
    """
    Get Toon textures path of PMD"
    """
    ...

class RbData(TypedDict):
    pass

def getRb(model: int, index: int) -> RbData | None:
    """
    Get Rigid bodies of PMD"
    """
    ...

class JointData(TypedDict):
    pass

def getJoint(model: int, index: int) -> JointData | None:
    """
    Get Joints of PMD"
    """
    ...

def Create_FromInfo(
    num: int,
    name: bytes,
    comment: bytes,
    name_eng: bytes,
    comment_eng: bytes,
    vt_count: int,
    face_count: int,
    mat_count: int,
    bone_count: int,
    ik_count: int,
    skin_count: int,
    bone_group_count: int,
    bone_dsp_count: int,
    eng_support: int,
    rb_count: int,
    joint_count: int,
    skin_index_count: int,
    skin_index: list[int],
) -> None:
    """
    Create PMD"
    """
    ...

def setVt():
    """
    Set Vertex of PMD"
    """
    ...

def setFace():
    """
    Set Face of PMD"
    """
    ...

def setMat():
    """
    Set Material of PMD"
    """
    ...

def setBone():
    """
    Set Bone of PMD"
    """
    ...

def setIK():
    """
    Set IK_List of PMD"
    """
    ...

def setSkin():
    """
    Set Skin of PMD"
    """
    ...

def setSkindata():
    """
    Set Skin_data of PMD"
    """
    ...

def setBone_group():
    """
    Set Bone_group of PMD"
    """
    ...

def setBone_disp():
    """
    Set Bone_disp of PMD"
    """
    ...

def setToon():
    """
    Set Toon textures of PMD"
    """
    ...

def setToonPath():
    """
    Set Toon textures path of PMD"
    """
    ...

def setRb():
    """
    Set Rigid bodies of PMD"
    """
    ...

def setJoint():
    """
    Set Joints of PMD"
    """
    ...

def Set_List(
    bn: int,
    b0: List[bytes],
    b1: List[bytes],
    sn: int,
    s0: List[bytes],
    s1: List[bytes],
    gn: int,
    g0: List[bytes],
    g1: List[bytes],
) -> None:
    """
    Set List of bone or things"
    """
    ...

def Set_Name_Comment(
    num: int,
    name: bytes,
    comment: bytes,
    name_eng: bytes,
    comment_eng: bytes,
) -> None:
    """
    Set Name and Comment
    """
    ...

def Init_PMD() -> None:
    """
    Initialize"
    """
    ...

def Load_PMD(num: int, path: bytes):
    """
    Load PMD from file"
    """
    ...

def Write_PMD():
    """
    Write PMD from file"
    """
    ...

def Add_PMD():
    """
    Add PMD from file"
    """
    ...

def Copy_PMD():
    """
    Copy PMD"
    """
    ...

def Create_PMD(num: int) -> None:
    """
    Create enpty PMD"
    """
    ...

def Marge_PMD():
    """
    Marge PMD"
    """
    ...

def Sort_PMD():
    """
    Sort PMD"
    """
    ...

def PMD_view_set():
    """
    Set selected PMD to dispray"
    """
    ...

def Resize_Model():
    """
    Resize_Model"
    """
    ...

def Move_Model():
    """
    Move_Model"
    """
    ...

def Resize_Bone():
    """
    Resize_Bone"
    """
    ...

def Move_Bone():
    """
    Move_Bone"
    """
    ...

def Update_Skin():
    """
    Update_Skin"
    """
    ...

def Adjust_Joints():
    """
    Adjust_Joints"
    """
    ...

def MODEL_LOCK(mode: int) -> None:
    """
    Lock/Unlock model"
    """
    ...

def getWHT():
    """
    get height, width, thickness from model"
    """
    ...

def CretateViewerThread() -> None:
    """
    CretateViewerThread
    """
    ...

def WaitViewerThread():
    """
    WaitViewerThread"
    """
    ...

def QuitViewerThread() -> None:
    """
    QuitViewerThread"
    """
    ...

def KillViewerThread():
    """
    KillViewerThread"
    """
    ...

def GetViewerThreadState():
    """
    GetViewerThreadState
    """
    ...

def show3Dview():
    """
    show3Dview"
    """
    ...
