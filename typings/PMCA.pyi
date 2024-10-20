# {"getInfo", getInfo, METH_VARARGS, "Get Info of PMD"},
# {"getVt", getVt, METH_VARARGS, "Get Vertex of PMD"},
# {"getFace", getFace, METH_VARARGS, "Get Face of PMD"},
# {"getMat", getMat, METH_VARARGS, "Get Material of PMD"},
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
    pass

# /***********************************************************************/
# {"Set_Name_Comment", Set_Name_Comment, METH_VARARGS,
#  "Set Name and Comment"},
# /***********************************************************************/

def Init_PMD() -> None:
    """
    Initialize
    """
    pass

# {"Load_PMD", Load_PMD, METH_VARARGS, "Load PMD from file"},
# {"Write_PMD", Write_PMD, METH_VARARGS, "Write PMD from file"},
# {"Add_PMD", Add_PMD, METH_VARARGS, "Add PMD from file"},
# {"Copy_PMD", Copy_PMD, METH_VARARGS, "Copy PMD"},
# {"Create_PMD", Create_PMD, METH_VARARGS, "Create enpty PMD"},
# {"Marge_PMD", Marge_PMD, METH_VARARGS, "Marge PMD"},
# {"Sort_PMD", Sort_PMD, METH_VARARGS, "Sort PMD"},
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
# {"MODEL_LOCK", MODEL_LOCK, METH_VARARGS, "Lock/Unlock model"},
# {"getWHT", getWHT, METH_VARARGS, "get height, width, thickness from model"},
# /***********************************************************************/

def CretateViewerThread() -> None:
    pass

# {"WaitViewerThread", WaitViewerThread, METH_VARARGS, "WaitViewerThread"},
# {"QuitViewerThread", QuitViewerThread, METH_VARARGS, "QuitViewerThread"},
# {"KillViewerThread", KillViewerThread, METH_VARARGS, "KillViewerThread"},
# {"GetViewerThreadState", GetViewerThreadState, METH_VARARGS,
#  "GetViewerThreadState"},
# {"show3Dview", show3Dview, METH_VARARGS, "show3Dview"},
#
