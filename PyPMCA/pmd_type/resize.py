from .parser import parse
from .to_bytes import to_bytes


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
