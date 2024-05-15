from typing import TypeVar, Type
import logging
import dataclasses
import struct
import ctypes
from .pmd import PMD


LOGGER = logging.getLogger(__name__)


T = TypeVar("T")


@dataclasses.dataclass
class BinaryReader:
    data: bytes
    pos: int = 0

    def is_end(self) -> bool:
        return self.pos >= len(self.data)

    def read(self, size: int) -> bytes:
        span = self.data[self.pos : self.pos + size]
        self.pos += size
        return span

    def string(self, byte_len: int, encoding: str = "cp932") -> str:
        span = self.read(byte_len)
        i = 0
        for i, b in enumerate(span):
            if b == 0:
                break
        return span[0:i].decode(encoding)

    def i32(self) -> int:
        span = self.read(4)
        return struct.unpack("i", span)[0]

    def u8(self) -> int:
        return self.read(1)[0]

    def u16(self) -> int:
        span = self.read(2)
        return struct.unpack("h", span)[0]

    def f32(self) -> float:
        span = self.read(4)
        return struct.unpack("f", span)[0]

    def read_type(self, t: Type[T]) -> T:
        size = ctypes.sizeof(t)  # type:ignore
        span = self.read(size)
        return t.from_buffer_copy(span)  # type:ignore


class Float2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]


class Float3(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]


class Float4(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]


class Vertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("position", Float3),
        ("normal", Float3),
        ("uv", Float2),
        ("bone0", ctypes.c_uint16),
        ("bone1", ctypes.c_uint16),
        ("weight", ctypes.c_ubyte),  # 0 to 100
        ("flag", ctypes.c_ubyte),
    ]


assert ctypes.sizeof(Vertex) == 38


class Submesh(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("diffuse_rgba", Float4),
        ("specularity", ctypes.c_float),
        ("specular_rgb", Float3),
        ("ambient_rgb", Float3),
        ("toon_index", ctypes.c_ubyte),
        ("flag", ctypes.c_ubyte),
        ("index_count", ctypes.c_uint),
        ("texture_file", (ctypes.c_char * 20)),
    ]


assert ctypes.sizeof(Submesh) == 70


class Bone(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("name", ctypes.c_char * 20),
        ("parent_index", ctypes.c_uint16),
        ("tail_index", ctypes.c_uint16),
        ("type", ctypes.c_ubyte),
        ("ik_index", ctypes.c_uint16),
        ("position", Float3),
    ]


assert ctypes.sizeof(Bone) == 39


class MoprhVertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("vertex_index", ctypes.c_int32),
        ("position", Float3),
    ]


assert ctypes.sizeof(MoprhVertex) == 16


class BoneDisplay(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bone_index", ctypes.c_int16),
        ("bone_disp_index", ctypes.c_uint8),
    ]


assert ctypes.sizeof(BoneDisplay) == 3


class RigidBody(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("rigidbody_name", ctypes.c_char * 20),
        ("rigidbody_rel_bone_index", ctypes.c_uint16),
        ("rigidbody_group_index", ctypes.c_uint8),
        ("rigidbody_group_target", ctypes.c_uint16),
        ("shape_type", ctypes.c_uint8),
        ("shape_xuz", Float3),
        ("pos_pos", Float3),
        ("pos_rot", Float3),
        ("rigidbody_weight", ctypes.c_float),
        ("rigidbody_pos_dim", ctypes.c_float),
        ("rigidbody_rot_dim", ctypes.c_float),
        ("rigidbody_recoil", ctypes.c_float),
        ("rigidbody_friction", ctypes.c_float),
        ("rigidbody_type", ctypes.c_uint8),
    ]


assert ctypes.sizeof(RigidBody) == 83


class Joint(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("joint_name", ctypes.c_char * 20),
        ("joint_rigidbody_a", ctypes.c_int),
        ("joint_rigidbody_b", ctypes.c_int),
        ("joint_pos", Float3),
        ("joint_rot", Float3),
        ("constrain_pos_1", Float3),
        ("constrain_pos_2", Float3),
        ("constrain_rot_1", Float3),
        ("constrain_rot_2", Float3),
        ("spring_pos", Float3),
        ("spring_rot", Float3),
    ]


assert ctypes.sizeof(Joint) == 124


def parse(data: bytes) -> PMD | None:
    r = BinaryReader(data)

    # ehader
    assert r.read(3) == b"Pmd"
    assert r.f32() == 1.0
    name = r.string(20)
    LOGGER.debug(name)
    comment = r.string(256)
    LOGGER.debug(comment)

    # vertex
    vertex_count = r.i32()
    vertices = r.read_type(Vertex * vertex_count)
    assert len(vertices) == vertex_count

    # index
    index_count = r.i32()
    indices = r.read_type(ctypes.c_uint16 * index_count)
    assert len(indices) == index_count

    # submesh
    submesh_count = r.i32()
    submeshes = r.read_type(Submesh * submesh_count)
    assert len(submeshes) == submesh_count

    # bone
    bone_count = r.u16()
    bones = r.read_type(Bone * bone_count)
    assert len(bones) == bone_count

    # ik
    ik_count = r.u16()
    for i in range(ik_count):
        target_index = r.u16()
        effector_index = r.u16()
        chain_count = r.u8()
        iteration = r.u16()
        angle_limit = r.f32()
        chains = r.read_type(ctypes.c_uint16 * chain_count)

    # morph
    morph_count = r.u16()
    for i in range(morph_count):
        name = r.string(20)
        morph_vertex_count = r.i32()
        morph_type = r.u8()
        morph_vertices = r.read_type(MoprhVertex * morph_vertex_count)

    # ui
    morph_disp_count = r.u8()
    morph_disp_list = r.read_type(ctypes.c_uint16 * morph_disp_count)
    bone_disp_name_count = r.u8()
    bone_disp_name_list = r.read_type((ctypes.c_char * 50) * bone_disp_name_count)
    bone_disp_count = r.i32()
    bone_disp_list = r.read_type(BoneDisplay * bone_disp_count)

    # extension
    has_english = r.u8()
    if has_english != 0:
        english_name = r.string(20)
        LOGGER.info(english_name)
        english_comment = r.string(256)
        LOGGER.info(english_comment)
        english_bone_names = r.read_type((ctypes.c_char * 20) * bone_count)
        if morph_count > 1:
            english_morph_names = r.read_type((ctypes.c_char * 20) * (morph_count - 1))
        english_disp_names = r.read_type((ctypes.c_char * 50) * bone_disp_name_count)

    # toon
    r.read_type((ctypes.c_char * 100) * 10)

    # rigidbody
    rigidbody_count = r.i32()
    rigidbodies = r.read_type(RigidBody * rigidbody_count)
    assert len(rigidbodies) == rigidbody_count

    # joint
    joint_count = r.i32()
    joints = r.read_type(Joint * joint_count)
    assert len(joints) == joint_count

    assert r.is_end()

    assert False
