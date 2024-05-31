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


def Resize_Bone(data: bytes, name: bytes, length: float, thickness: float) -> bytes:
    pmd = parse(data)
    assert pmd
    return to_bytes(pmd)


#   const uint8_t *pa;
#   size_t sa;
#   const char *str;
#   double len, thi;
#   if (!PyArg_ParseTuple(args, "y#ydd", &pa, &sa, &str, &len, &thi)) {
#     Py_RETURN_NONE;
#   }

#   auto model = MODEL::from_bytes({pa, sa});
#   int index = 0;
#   for (; index < model->bone.size(); index++) {
#     if (strcmp(model->bone[index].name, str) == 0) {
#       break;
#     }
#   }
#   if (index == model->bone.size()) {
#     Py_RETURN_NONE;
#   }

#   if (!model->scale_bone(index, thi, len, thi)) {
#     // Py_RETURN_NONE;
#   }

#   auto bytes = model->to_bytes();
#   return Py_BuildValue("y#", bytes.data(), bytes.size());
# }
