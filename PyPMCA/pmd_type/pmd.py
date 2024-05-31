from typing import Sequence
import dataclasses
import ctypes
from .types import Vertex, Submesh, Bone, RigidBody, Joint
from .info import INFO
from .bone import BONE_DISP, BONE_GROUP
from .ik import IK_LIST
from .skin import SKIN


@dataclasses.dataclass
class TOON:
    name: tuple[
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
    ] = (
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )
    path: tuple[
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
    ] = (
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    )

    def name_cp932(
        self,
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
        return (
            self.name[0].encode("cp932", "replace"),
            self.name[1].encode("cp932", "replace"),
            self.name[2].encode("cp932", "replace"),
            self.name[3].encode("cp932", "replace"),
            self.name[4].encode("cp932", "replace"),
            self.name[5].encode("cp932", "replace"),
            self.name[6].encode("cp932", "replace"),
            self.name[7].encode("cp932", "replace"),
            self.name[8].encode("cp932", "replace"),
            self.name[9].encode("cp932", "replace"),
        )

    def path_cp932(
        self,
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
        return (
            self.path[0].encode("cp932", "replace"),
            self.path[1].encode("cp932", "replace"),
            self.path[2].encode("cp932", "replace"),
            self.path[3].encode("cp932", "replace"),
            self.path[4].encode("cp932", "replace"),
            self.path[5].encode("cp932", "replace"),
            self.path[6].encode("cp932", "replace"),
            self.path[7].encode("cp932", "replace"),
            self.path[8].encode("cp932", "replace"),
            self.path[9].encode("cp932", "replace"),
        )

    @staticmethod
    def from_bytes(
        name: Sequence[bytes], path: Sequence[bytes] | None = None
    ) -> "TOON":
        return TOON(
            tuple(x.decode("cp932", "replace") for x in name),  # type: ignore
            tuple(x.decode("cp932", "replace") for x in path) if path else tuple([""] * 10),  # type: ignore
        )


@dataclasses.dataclass
class PMD:
    info: INFO
    vertices: ctypes.Array[Vertex]
    indices: ctypes.Array[ctypes.c_uint16]
    submeshes: ctypes.Array[Submesh]
    bones: ctypes.Array[Bone]
    IK: list[IK_LIST]
    morphs: list[SKIN]
    bone_groups: list[BONE_GROUP]
    bone_displays: list[BONE_DISP]
    toon: TOON
    rigidbodies: ctypes.Array[RigidBody]
    joints: ctypes.Array[Joint]

    @staticmethod
    def create() -> "PMD":
        return PMD(
            info=INFO(),
            vertices=None,
            indices=None,
            submeshes=None,
            bones=None,
            IK=[],
            morphs=[],
            bone_groups=[],
            bone_displays=[],
            toon=TOON(),
            rigidbodies=None,
            joints=None,
        )

    def add(self, parts: "PMD") -> None:
        """
        port from c++

        bool MODEL::add_PMD(const std::shared_ptr<MODEL> &add)
        """
        pre_vt_size = len(self.vertices) if self.vertices else 0
        pre_face_size = len(self.indices) if self.indices else 0
        pre_mat_size = len(self.submeshes) if self.submeshes else 0
        pre_bone_size = len(self.bones) if self.bones else 0
        # pre_skin_disp_size = len(self.skin_disp) if self.info.skin_index
        pre_bone_group_size = len(self.bone_groups)
        pre_rbody_size = len(self.rigidbodies) if self.rigidbodies else 0

        # 頂点
        assert parts.vertices
        vt = (Vertex * (pre_vt_size + len(parts.vertices)))()
        if self.vertices:
            for i, v in enumerate(self.vertices):
                vt[i] = v
        index = pre_vt_size
        for v in parts.vertices:
            vt[index] = v
            # fix bone index
            vt[index].bone0 += pre_bone_size
            vt[index].bone1 += pre_bone_size
            index += 1
        self.vertices = vt

        # 面頂点
        assert parts.indices
        faces = (ctypes.c_uint16 * (pre_face_size + len(parts.indices)))()
        if self.indices:
            for i, f in enumerate(self.indices):
                faces[i] = f
        index = pre_face_size
        for f in parts.indices:
            # fix index
            faces[index] = f + pre_face_size
            index += 1
        parts.indices = faces

        # 材質
        assert parts.submeshes
        mat = (Submesh * (pre_mat_size + len(parts.submeshes)))()
        if self.submeshes:
            for i, m in enumerate(self.submeshes):
                mat[i] = m
        index = pre_mat_size
        for m in parts.submeshes:
            mat[index] = m
            index += 1
        parts.submeshes = mat

        # ボーン
        for b in parts.bones:
            self.bones.append(BONE(**dataclasses.asdict(b)))
            # fix bone index
            if self.bones[-1].parent_index != 65535:
                self.bones[-1].parent_index += pre_bone_size
            if self.bones[-1].tail_index != 0:
                self.bones[-1].tail_index += pre_bone_size
            if self.bones[-1].ik != 0:
                self.bones[-1].ik += pre_bone_size

        # IKリスト
        for ik in parts.IK:
            self.IK.append(ik)
            self.IK[-1].bone_index += pre_bone_size
            self.IK[-1].target_boneindex += pre_bone_size
            for k in range(len(self.IK[-1].chain)):
                self.IK[-1].chain[k] += pre_bone_size

        # 表情
        if len(parts.morphs) == 0:
            pass
        elif len(self.morphs) == 0:
            # copy
            for skin in parts.morphs:
                self.morphs.append(skin)
        else:
            # 0番を合成
            pass
        #     skin[0].skin_vt.reserve(this->skin[0].skin_vt.size() +
        #                             parts.skin[0].skin_vt.size());
        #     for (auto &skin_vt : parts.skin[0].skin_vt) {
        #     this->skin[0].skin_vt.push_back(skin_vt);
        #     // index 補正
        #     this->skin[0].skin_vt.back().index += pre_vt_size;
        #     }

        #     // 1以降追加
        #     this->skin.reserve(this->skin.size() + parts.skin.size() - 1);
        #     for (size_t i = 1; i < parts.skin.size(); i++) {
        #     skin.push_back(parts.skin[i]);
        #     for (size_t k = 0; k < skin.back().skin_vt.size(); k++) {
        #         // index 補正
        #         skin.back().skin_vt[k].index += pre_vt_size;
        #     }
        #     }
        # }

        # // 表情表示
        # skin_disp.reserve(this->skin_disp.size() + parts.skin_disp.size());
        # for (auto &sd : parts.skin_disp) {
        #     skin_disp.push_back(sd + pre_skin_disp_size);
        # }

        # // ボーン表示
        # bone_group.reserve(this->bone_group.size() + parts.bone_group.size());
        # for (auto &bg : parts.bone_group) {
        #     bone_group.push_back(bg);
        # }
        # bone_disp.reserve(this->bone_disp.size() + parts.bone_disp.size());
        # for (auto &bd : parts.bone_disp) {
        #     bone_disp.push_back(bd);
        #     bone_disp.back().index += pre_bone_size;
        #     bone_disp.back().bone_group += pre_bone_group_size;
        # }

        # // 英名
        # this->eng_support = parts.eng_support;

        # // 剛体
        # rbody.reserve(this->rbody.size() + parts.rbody.size());
        # for (auto &rb : parts.rbody) {
        #     rbody.push_back(rb);
        #     rbody.back().bone += pre_bone_group_size;
        # }

        # // ジョイント
        # joint.reserve(this->joint.size() + parts.joint.size());
        # for (auto &j : parts.joint) {
        #     joint.push_back(j);
        #     joint.back().rbody[0] += pre_rbody_size;
        #     joint.back().rbody[1] += pre_rbody_size;
        # }
