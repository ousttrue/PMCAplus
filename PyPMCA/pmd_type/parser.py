from typing import TypeVar, Type
import logging
import dataclasses
import struct
import ctypes

from .types import Vertex, Submesh, Bone, MoprhVertex, BoneDisplay, RigidBody, Joint
from .pmd import PMD, TOON
from .info import INFO
from .ik import IK_LIST
from .skin import SKIN
from .bone import BONE_DISP, BONE_GROUP


LOGGER = logging.getLogger(__name__)


T = TypeVar("T")


def decode_co032_bytes(src: bytes) -> str:
    i = 0
    for i, b in enumerate(src):
        if b == 0:
            break
    return src[: i + 1].decode("cp932", "replace")


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
        return decode_co032_bytes(span)

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


def parse(data: bytes) -> PMD | None:
    if not data:
        return PMD(
            INFO(),
            (Vertex * 0)(),
            (ctypes.c_uint16 * 0)(),
            (Submesh * 0)(),
            (Bone * 0)(),
            [],
            [],
            [],
            [],
            TOON(),
            (RigidBody * 0)(),
            (Joint * 0)(),
        )
    r = BinaryReader(data)

    # ehader
    assert r.read(3) == b"Pmd"
    assert r.f32() == 1.0
    name = r.string(20)
    comment = r.string(256)

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

    # ik
    ik_list: list[IK_LIST] = []
    ik_count = r.u16()
    for _ in range(ik_count):
        target_index = r.u16()
        effector_index = r.u16()
        chain_count = r.u8()
        iteration = r.u16()
        angle_limit = r.f32()
        chains = r.read_type(ctypes.c_uint16 * chain_count)
        ik_list.append(
            IK_LIST(
                target_index,
                effector_index,
                iteration,
                angle_limit,
                chains,
            )
        )

    # morph
    morphs: list[SKIN] = []
    morph_count = r.u16()
    for _ in range(morph_count):
        morph_name = r.string(20)
        morph_vertex_count = r.i32()
        morph_type = r.u8()
        morph_vertices = r.read_type(MoprhVertex * morph_vertex_count)
        morphs.append(
            SKIN(
                morph_name,
                "",
                morph_type,
                morph_vertices,
            )
        )

    # ui
    morph_disp_count = r.u8()
    morph_disp_list = r.read_type(ctypes.c_uint16 * morph_disp_count)

    bone_disp_name_count = r.u8()
    bone_disp_name_list = r.read_type((ctypes.c_char * 50) * bone_disp_name_count)
    bone_group: list[BONE_GROUP] = [
        BONE_GROUP(decode_co032_bytes(bytes(g)), "") for g in bone_disp_name_list
    ]

    bone_disp_count = r.i32()
    bone_disp_list = r.read_type(BoneDisplay * bone_disp_count)
    bone_dsp: list[BONE_DISP] = [
        BONE_DISP(
            d.bone_index,
            d.bone_disp_index,
        )
        for d in bone_disp_list
    ]

    # extension
    has_english = r.u8()
    english_name = ""
    english_comment = ""
    if has_english != 0:
        english_name = r.string(20)
        english_comment = r.string(256)
        english_bone_names = r.read_type((ctypes.c_char * 20) * bone_count)
        if morph_count > 1:
            english_morph_names = r.read_type((ctypes.c_char * 20) * (morph_count - 1))
        english_disp_names = r.read_type((ctypes.c_char * 50) * bone_disp_name_count)

    # toon
    toons = r.read_type((ctypes.c_char * 100) * 10)
    toon = TOON.from_bytes([bytes(t) for t in toons])

    # rigidbody
    rigidbody_count = r.i32()
    rigidbodies = r.read_type(RigidBody * rigidbody_count)
    assert len(rigidbodies) == rigidbody_count

    # joint
    joint_count = r.i32()
    joints = r.read_type(Joint * joint_count)
    assert len(joints) == joint_count

    assert r.is_end()

    info = INFO(
        name,
        english_name,
        comment,
        english_comment,
        has_english,
        skin_index=[int(x) for x in morph_disp_list],
    )
    return PMD(
        info,
        vertices,
        indices,
        submeshes,
        bones,
        ik_list,
        morphs,
        bone_group,
        bone_dsp,
        toon,
        rigidbodies,
        joints,
    )
