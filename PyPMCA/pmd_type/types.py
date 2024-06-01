import ctypes
import math


def angle_from_vec(u: float, v: float) -> float:
    """
    ベクトルがv軸方向を向く回転を求める
    """
    angle = math.asin(u / math.sqrt(u * u + v * v))
    # printf("angle %f\n", angle);
    if v < 0:
        angle = math.pi - angle
    return angle


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

    def __add__(self, rhs: "Float3") -> "Float3":
        return Float3(
            self.x + rhs.x,
            self.y + rhs.y,
            self.z + rhs.z,
        )

    def __sub__(self, rhs: "Float3") -> "Float3":
        return Float3(
            self.x - rhs.x,
            self.y - rhs.y,
            self.z - rhs.z,
        )

    def __mul__(self, f: float) -> "Float3":
        return Float3(
            self.x * f,
            self.y * f,
            self.z * f,
        )

    def scale(self, rhs: "Float3") -> "Float3":
        return Float3(
            self.x * rhs.x,
            self.y * rhs.y,
            self.z * rhs.z,
        )

    @staticmethod
    def dot(l: "Float3", r: "Float3") -> float:
        return l.x * r.x + l.y * r.y + l.z * r.z

    def length(self) -> float:
        return math.sqrt(Float3.dot(self, self))

    def normalized(self) -> "Float3":
        return self * (1 / self.length())


class Float4(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]


class Mat3(ctypes.Structure):
    _fields_ = [
        ("row0", Float3),
        ("row1", Float3),
        ("row2", Float3),
    ]

    @property
    def col0(self) -> Float3:
        return Float3(self.row0.x, self.row1.x, self.row2.x)

    @property
    def col1(self) -> Float3:
        return Float3(self.row0.y, self.row1.y, self.row2.y)

    @property
    def col2(self) -> Float3:
        return Float3(self.row0.z, self.row1.z, self.row2.z)

    def transposed(self) -> "Mat3":
        return Mat3(
            self.col0,
            self.col1,
            self.col2,
        )

    def __mul__(self, rhs: "Mat3") -> "Mat3":
        return Mat3(
            Float3(
                Float3.dot(self.row0, rhs.col0),
                Float3.dot(self.row0, rhs.col1),
                Float3.dot(self.row0, rhs.col2),
            ),
            Float3(
                Float3.dot(self.row1, rhs.col0),
                Float3.dot(self.row1, rhs.col1),
                Float3.dot(self.row1, rhs.col2),
            ),
            Float3(
                Float3.dot(self.row2, rhs.col0),
                Float3.dot(self.row2, rhs.col1),
                Float3.dot(self.row2, rhs.col2),
            ),
        )

    def rotate(self, rhs: Float3) -> Float3:
        return Float3(
            Float3.dot(self.row0, rhs),
            Float3.dot(self.row1, rhs),
            Float3.dot(self.row2, rhs),
        )

    @staticmethod
    def rotation_z(theta: float) -> "Mat3":
        c = math.cos(theta)
        s = math.sin(theta)
        return Mat3(
            Float3(c, -s, 0),
            Float3(s, c, 0),
            Float3(0, 0, 1),
        )

    @staticmethod
    def rotation_x(theta: float) -> "Mat3":
        c = math.cos(theta)
        s = math.sin(theta)
        return Mat3(
            Float3(1, 0, 0),
            Float3(0, c, s),
            Float3(0, -s, c),
        )


assert ctypes.sizeof(Mat3) == 36


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
        ("name", ctypes.c_uint8 * 20),
        ("parent_index", ctypes.c_uint16),
        ("tail_index", ctypes.c_uint16),
        ("type", ctypes.c_ubyte),
        ("ik_index", ctypes.c_uint16),
        ("position", Float3),
    ]

    @property
    def str_name(self) -> str:
        for i, c in enumerate(self.name):
            if c == 0:
                return bytes(self.name)[0:i].decode("cp932")
        return bytes(self.name).decode("cp932")

    def rotation_to_tail(self, tail: Float3) -> Mat3:
        """
        head => tail ベクトル
        """
        vec = (tail - self.position).normalized()

        # ベクトルのZXY角を求める
        rot_z = angle_from_vec(vec.x, vec.y)
        rot_x = angle_from_vec(vec.z, math.sqrt(vec.x * vec.x + vec.y * vec.y))
        # 回転行列を求める
        return Mat3.rotation_x(rot_x) * Mat3.rotation_z(rot_z)


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
