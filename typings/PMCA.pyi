from typing import List, TypedDict
from PyPMCA import pmd_type

def getInfo(model: int) -> pmd_type.InfoData:
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

def setVt(
    num: int,
    i: int,
    loc: tuple[float, float, float],
    normal: tuple[float, float, float],
    uv: tuple[float, float],
    bone0: int,
    bone1: int,
    weight: int,
    edge: int,
) -> None:
    """
    Set Vertex of PMD"
    """
    ...

def setFace(num: int, i: int, face: tuple[int, int, int]) -> None:
    """
    Set Face of PMD"
    """
    ...

def setMat(
    num: int,
    i: int,
    diffuse: tuple[float, float, float],
    alpha: float,
    specular: float,
    specular_color: tuple[float, float, float],
    mirror_color: tuple[float, float, float],
    toon: int,
    edge: int,
    vertex_count: int,
    tex: bytes,
    sph: bytes,
    tex_path: bytes,
    sph_path: bytes,
) -> None:
    """
    Set Material of PMD"
    """
    ...

def setBone(
    num: int,
    i: int,
    name: bytes,
    name_en: bytes,
    parent: int,
    tail: int,
    type: int,
    IK: int,
    loc: tuple[float, float, float],
) -> None:
    """
    Set Bone of PMD"
    """
    ...

def setIK(
    num: int,
    i: int,
    bone: int,
    target: int,
    chain_len: int,
    iteration: int,
    weight: float,
    chain: list[int],
) -> None:
    """
    Set IK_List of PMD"
    """
    ...

def setSkin(
    num: int, i: int, name: bytes, name_eng: bytes, length: int, skin_type: int
) -> None:
    """
    Set Skin of PMD"
    """
    ...

def setSkindata(
    num: int, i: int, j: int, index: int, vec3: tuple[float, float, float]
) -> None:
    """
    Set Skin_data of PMD"
    """
    ...

def setBone_group(num: int, i: int, name: bytes, name_eng: bytes) -> None:
    """
    Set Bone_group of PMD"
    """
    ...

def setBone_disp(num: int, i: int, x: int, y: int) -> None:
    """
    Set Bone_disp of PMD"
    """
    ...

def setToon(
    num: int,
    toon_list: tuple[
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
    ],
) -> None:
    """
    Set Toon textures of PMD"
    """
    ...

def setToonPath(
    num: int,
    toon_path_list: tuple[
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
        bytes,
    ],
) -> None:
    """
    Set Toon textures path of PMD"
    """
    ...

def setRb(
    num: int,
    i: int,
    name: bytes,
    bone: int,
    group: int,
    target: int,
    shape: int,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    rot: tuple[float, float, float],
    mass: float,
    damp: float,
    rdamp: float,
    res: float,
    fric: float,
    type: int,
) -> None:
    """
    Set Rigid bodies of PMD"
    """
    ...

def setJoint(
    num: int,
    i: int,
    name: bytes,
    rb: tuple[int, int],
    loc: tuple[float, float, float],
    rot: tuple[float, float, float],
    limit: tuple[
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
        float,
    ],
    spring: tuple[
        float,
        float,
        float,
        float,
        float,
        float,
    ],
) -> None:
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

def Load_PMD(num: int, path: bytes) -> None:
    """
    Load PMD from file"
    """
    ...

def Write_PMD():
    """
    Write PMD from file"
    """
    ...

def Add_PMD(num: int, i: int) -> None:
    """
    Add PMD from file"
    """
    ...

def Copy_PMD(src: int, dst: int) -> None:
    """
    Copy PMD"
    """
    ...

def Marge_PMD(num: int) -> bool:
    """
    Marge PMD"
    """
    ...

def Sort_PMD(num: int) -> None:
    """
    Sort PMD"
    """
    ...

def PMD_view_set(num: int, mode: str) -> None:
    """
    Set selected PMD to dispray"
    """
    ...

def Get_PMD(num: int) -> tuple[bytes, bytes, list[tuple[int, str]]] | None:
    """
    Get vertices, indices and vertex_count list
    """
    ...

def Resize_Model(num: int, scale: float) -> None:
    """
    Resize_Model"
    """
    ...

def Move_Model(num: int, x: float, y: float, z: float) -> None:
    """
    Move_Model"
    """
    ...

def Resize_Bone(num: int, name: bytes, length: float, thickness: float) -> None:
    """
    Resize_Bone"
    """
    ...

def Move_Bone(num: int, name: bytes, x: float, y: float, z: float) -> None:
    """
    Move_Bone"
    """
    ...

def Update_Skin(num: int) -> None:
    """
    Update_Skin"
    """
    ...

def Adjust_Joints(num: int) -> None:
    """
    Adjust_Joints"
    """
    ...

def getWHT(num: int) -> tuple[float, float, float]:
    """
    get height, width, thickness from model"
    """
    ...
