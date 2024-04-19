from typing import List

def getInfo(num: int):
    """
    Get Info of PMD"
    """
    ...

def getVt():
    """
    Get Vertex of PMD"
    """
    ...

def getFace():
    """
    Get Face of PMD"
    """
    ...

def getMat():
    """
    Get Material of PMD"
    """
    ...

def getBone():
    """
    Get Bone of PMD"
    """
    ...

def getIK():
    """
    Get IK_List of PMD"
    """
    ...

def getSkin():
    """
    Get Skin of PMD"
    """
    ...

def getSkindata():
    """
    Get Skin_data of PMD"
    """
    ...

def getBone_group():
    """
    Get Bone_group of PMD"
    """
    ...

def getBone_disp():
    """
    Get Bone_disp of PMD"
    """
    ...

def getToon():
    """
    Get Toon textures of PMD"
    """
    ...

def getToonPath():
    """
    Get Toon textures path of PMD"
    """
    ...

def getRb():
    """
    Get Rigid bodies of PMD"
    """
    ...

def getJoint():
    """
    Get Joints of PMD"
    """
    ...

def Create_FromInfo():
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
):
    """
    Set Name and Comment
    """
    ...

def Init_PMD():
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

def Create_PMD(num: int):
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

def MODEL_LOCK():
    """
    Lock/Unlock model"
    """
    ...

def getWHT():
    """
    get height, width, thickness from model"
    """
    ...

def CretateViewerThread():
    """
    CretateViewerThread
    """
    ...

def WaitViewerThread():
    """
    WaitViewerThread"
    """
    ...

def QuitViewerThread():
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
