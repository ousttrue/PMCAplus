from typing import TypeVar, Type
import ctypes
from .parser import parse
from .to_bytes import to_bytes
from .types import Float3, Vertex, Submesh, Bone, MoprhVertex, RigidBody, Joint


T = TypeVar("T")


def Resize_Model(data: bytes, scale: float) -> bytes:
    pmd = parse(data)
    assert pmd

    for bone in pmd.bones:
        bone.position.x *= scale
        bone.position.y *= scale
        bone.position.z *= scale

    for v in pmd.vertices:
        v.position.x *= scale
        v.position.y *= scale
        v.position.z *= scale

    for morph in pmd.morphs:
        for x in morph.data:
            x.position.x *= scale
            x.position.y *= scale
            x.position.z *= scale

    return to_bytes(pmd)


def Move_Model(data: bytes, x: float, y: float, z: float) -> bytes:
    pmd = parse(data)
    assert pmd

    for bone in pmd.bones:
        bone.position.x += x
        bone.position.y += y
        bone.position.z += z

    for v in pmd.vertices:
        v.position.x += x
        v.position.y += y
        v.position.z += z

    return to_bytes(pmd)


def Resize_Bone(data: bytes, name: str, length: float, thickness: float) -> bytes:
    pmd = parse(data)
    assert pmd

    for i, bone in enumerate(pmd.bones):
        if bone.str_name == name:
            tail = pmd.find_tail(i)
            if tail:
                rot = bone.rotation_to_tail(tail.position)
                pmd.scale_vertices(i, rot, Float3(thickness, length, thickness))
                pmd.scale_bones(i, rot, Float3(thickness, length, thickness))
            break

    return to_bytes(pmd)


def Move_Bone(data: bytes, name: str, diff: Float3) -> bytes:
    pmd = parse(data)
    assert pmd

    for i, bone in enumerate(pmd.bones):
        if bone.str_name == name:
            pmd.move_bone(i, diff)
            break

    return to_bytes(pmd)


def Adjust_Joints(data: bytes) -> bytes:
    """
    同じ名前のボーンにジョイントの位置を合わせる
    """
    pmd = parse(data)
    assert pmd

    for joint in pmd.joints:
        for bone in pmd.bones:
            if joint.str_name == bone.str_name:
                joint.position = bone.position
                break

    return to_bytes(pmd)


def Update_Skin(data: bytes) -> bytes:
    """
    表情baseの頂点位置を更新する
    """
    pmd = parse(data)
    assert pmd

    if len(pmd.morphs) > 0:
        for v in pmd.morphs[0].data:
            v.position = pmd.vertices[v.vertex_index].position

    return to_bytes(pmd)


def concat_array(t: Type[T], a: ctypes.Array[T], b: ctypes.Array[T]) -> ctypes.Array[T]:
    size = len(a) + len(b)
    return (t * size)(*a, *b)


def Add_PMD(data: bytes, b: bytes) -> bytes:
    """
    Add PMD from file"
    """
    pmd = parse(data)
    assert pmd
    add = parse(b)
    assert add

    pre_vt_size = len(pmd.vertices)
    pre_indices_size = len(pmd.indices)
    pre_bone_size = len(pmd.bones)
    pre_skin_disp_size = len(pmd.info.skin_index)
    pre_bone_group_size = len(pmd.bone_groups)
    pre_rbody_size = len(pmd.rigidbodies)
    pre_joint_isze = len(pmd.joints)

    # 頂点
    pmd.vertices = concat_array(Vertex, pmd.vertices, add.vertices)
    for i in range(pre_vt_size, len(pmd.vertices)):
        # fix bone index
        pmd.vertices[i].bone0 += pre_bone_size
        pmd.vertices[i].bone1 += pre_bone_size

    # 面頂点
    pmd.indices = concat_array(ctypes.c_uint16, pmd.indices, add.indices)
    for i in range(pre_indices_size, len(pmd.indices)):
        # fix index
        pmd.indices[i] += pre_vt_size

    # 材質
    pmd.submeshes = concat_array(Submesh, pmd.submeshes, add.submeshes)

    # ボーン
    pmd.bones = concat_array(Bone, pmd.bones, add.bones)
    for i in range(pre_bone_size, len(pmd.bones)):
        # fix bone index
        if pmd.bones[i].parent_index != 65535:
            pmd.bones[i].parent_index += pre_bone_size
        if pmd.bones[i].tail_index != 0:
            pmd.bones[i].tail_index += pre_bone_size
        if pmd.bones[i].ik_index != 0:
            pmd.bones[i].ik_index += pre_bone_size

    # IKリスト
    for ik in add.IK:
        pmd.IK.append(ik)
        pmd.IK[-1].bone_index += pre_bone_size
        pmd.IK[-1].target_bone_index += pre_bone_size
        for i, _ in enumerate(pmd.IK[-1].chain):
            pmd.IK[-1].chain[i] += pre_bone_size

    # 表情
    if len(add.morphs) == 0:
        # nothing
        pass
    elif len(pmd.morphs) == 0:
        # copy
        pmd.morphs = add.morphs.copy()
    elif len(pmd.morphs) != 0 and len(add.morphs) != 0:
        # 0番を合成
        pre_len = len(pmd.morphs[0].data)
        pmd.morphs[0].data = concat_array(
            MoprhVertex, pmd.morphs[0].data, add.morphs[0].data
        )
        for i in range(pre_len, len(pmd.morphs[0].data)):
            # index 補正
            pmd.morphs[0].data[i].vertex_index += pre_vt_size

        # 1以降追加
        for morph in add.morphs[1:]:
            pmd.morphs.append(morph)
            for v in pmd.morphs[-1].data:
                # index 補正
                v.vertex_index += pre_vt_size

    # 表情表示
    for sd in add.info.skin_index:
        pmd.info.skin_index.append(sd + pre_skin_disp_size)

    # ボーン表示
    for bg in add.bone_groups:
        pmd.bone_groups.append(bg)

    for bd in add.bone_displays:
        pmd.bone_displays.append(bd)
        pmd.bone_displays[-1].bone_group_index += pre_bone_group_size
        pmd.bone_displays[-1].bone_index += pre_bone_size

    # 英名
    # pmd.eng_support = add.eng_support

    # 剛体
    pmd.rigidbodies = concat_array(RigidBody, pmd.rigidbodies, add.rigidbodies)
    for i in range(pre_rbody_size, len(pmd.rigidbodies)):
        pmd.rigidbodies[i].rigidbody_rel_bone_index += pre_bone_group_size

    # ジョイント
    pmd.joints = concat_array(Joint, pmd.joints, add.joints)
    for i in range(pre_joint_isze, len(pmd.joints)):
        pmd.joints[i].joint_rigidbody_a += pre_rbody_size
        pmd.joints[i].joint_rigidbody_b += pre_rbody_size

    return to_bytes(pmd)


def Marge_PMD(data: bytes) -> bytes:
    """
    Marge PMD"
    """
    pmd = parse(data)
    assert pmd

    pmd.merge_bone()
    pmd.merge_mat()
    pmd.merge_IK()
    pmd.merge_bone_disp()
    pmd.merge_rb()

    return to_bytes(pmd)
