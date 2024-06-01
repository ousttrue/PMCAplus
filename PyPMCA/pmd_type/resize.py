from .parser import parse
from .to_bytes import to_bytes
from .types import Float3


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

    for v in pmd.morphs[0].data:
        v.position = pmd.vertices[v.vertex_index].position

    return to_bytes(pmd)
