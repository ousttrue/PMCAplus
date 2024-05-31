import ctypes


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
        ("diffuse_rgb", Float3),
        ("alpha", ctypes.c_float),
        ("specularity", ctypes.c_float),
        ("specular_rgb", Float3),
        ("ambient_rgb", Float3),
        ("toon_index", ctypes.c_ubyte),
        ("flag", ctypes.c_ubyte),
        ("index_count", ctypes.c_uint),
        ("texture_file", (ctypes.c_uint8 * 20)),
    ]

    @property
    def tex(self) -> str:
        for i, c in enumerate(self.texture_file):
            if c == 0 or c == ord("*"):
                return bytes(self.texture_file)[0:i].decode("cp932")
        return bytes(self.texture_file).decode("cp932")

    @tex.setter
    def tex(self, value: str) -> None:
        data = value.encode("cp932")
        assert len(data) < 20
        for i, c in enumerate(data):
            self.texture_file[i] = c
        for i in range(len(data), 20):
            self.texture_file[i] = 0


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
