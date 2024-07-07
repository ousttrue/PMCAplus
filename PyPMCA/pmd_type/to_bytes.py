import io
import ctypes
import struct
from .pmd import PMD


class BinWriter:
    def __init__(self):
        self.w = io.BytesIO()

    def getvalue(self) -> bytes:
        return self.w.getvalue()

    def write(self, b: bytes) -> None:
        self.w.write(b)

    def sjis(self, v: str, size: int) -> None:
        buffer = (ctypes.c_uint8 * size)()
        data = v.encode("cp932")
        for i in range(min(len(data), size)):
            buffer[i] = data[i]
        self.write(bytes(buffer))

    def u8(self, v: int) -> None:
        self.write(struct.pack("b", v))

    def u16(self, v: int) -> None:
        self.write(struct.pack("H", v))

    # def i16(self, v: int) -> None:
    #     self.write(struct.pack("h", v))

    def i32(self, v: int) -> None:
        self.write(struct.pack("i", v))

    def f32(self, v: float) -> None:
        self.write(struct.pack("f", v))


def to_bytes(model: PMD) -> bytes:
    w = BinWriter()
    w.write(b"Pmd")
    w.f32(1.0)
    w.sjis(model.info.name, 20)
    w.sjis(model.info.comment, 256)

    w.i32(len(model.vertices))
    w.write(bytes(model.vertices))

    w.i32(len(model.indices))
    w.write(bytes(model.indices))

    w.i32(len(model.submeshes))
    w.write(bytes(model.submeshes))

    w.u16(len(model.bones))
    w.write(bytes(model.bones))

    w.u16(len(model.IK))
    for ik in model.IK:
        w.u16(ik.bone_index)
        w.u16(ik.target_bone_index)
        w.u8(len(ik.chain))
        w.u16(ik.iterations)
        w.f32(ik.weight)
        w.write(bytes(ik.chain))

    w.u16(len(model.morphs))
    for morph in model.morphs:
        w.sjis(morph.name, 20)
        w.i32(len(morph.data))
        w.u8(morph.type)
        w.write(bytes(morph.data))

    w.u8(len(model.info.skin_index))
    w.write(
        bytes((ctypes.c_uint16 * len(model.info.skin_index))(*model.info.skin_index))
    )

    w.u8(len(model.bone_groups))
    for bone_group in model.bone_groups:
        w.sjis(bone_group.name, 50)

    w.i32(len(model.bone_displays))
    for dsp in model.bone_displays:
        w.u16(dsp.bone_index)
        w.u8(dsp.bone_group_index)

    w.u8(0)
    # w.sjis(model.info.name_eng, 20)
    # w.sjis(model.info.comment_eng, 256)
    # for i in range(len(model.bones)):
    #     w.sjis(model.info.)
    # for i in range(len(model.morphs-1)):
    #     pass
    # for i in range(len(model.bone_groups)):
    #     pass

    for i in range(10):
        w.sjis(model.toon.name[i], 100)

    w.i32(len(model.rigidbodies))
    w.write(bytes(model.rigidbodies))

    w.i32(len(model.joints))
    w.write(bytes(model.joints))

    return w.getvalue()
