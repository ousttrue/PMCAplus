from typing import Literal
import dataclasses
import logging

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class BONE_TRANS_DATA:
    name: str
    length: float = 1.0
    thick: float = 1.0
    pos: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rot: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclasses.dataclass
class MODEL_TRANS_DATA:
    name: str
    scale_min: float = 0.0
    scale_max: float = 2.0
    scale_default: float = 1.0
    props: dict[str, str] = dataclasses.field(default_factory=dict)

    scale: float = 1.0
    pos: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rot: tuple[float, float, float] = (0.0, 0.0, 0.0)
    bones: list[BONE_TRANS_DATA] = dataclasses.field(default_factory=list)

    def list_to_text(self) -> list[str]:
        lines: list[str] = []
        lines.append("[Scale] %f" % (self.scale))
        lines.append("[Pos] %f %f %f" % (self.pos[0], self.pos[1], self.pos[2]))
        lines.append("[Rot] %f %f %f" % (self.rot[0], self.rot[1], self.rot[2]))
        lines.append("BONES")
        for x in self.bones:
            lines.append("[Name] %s" % (x.name))
            lines.append("[Length] %f" % (x.length))
            lines.append("[Thick] %f" % (x.thick))
            lines.append("[Pos] %f %f %f" % (x.pos[0], x.pos[1], x.pos[2]))
            lines.append("[Rot] %f %f %f" % (x.rot[0], x.rot[1], x.rot[2]))
            lines.append("NEXT")
        lines.pop()

        return lines

    @staticmethod
    def load_list(lines: list[str]) -> list["MODEL_TRANS_DATA"]:
        """
        PMCA Transform list v2.0

        [name] 全身スケール
        [range] 0.8 1.2
        [scale] 1.0

        NEXT

        [name] 胴体
        [range] 0.5 1.5
        [ENTRY] 上半身
        [length] 1.0
        [ENTRY] 下半身
        [length] 0.5

        NEXT
        """
        assert lines[0] == "PMCA Transform list v2.0"

        trans_list: list[MODEL_TRANS_DATA] = []

        mode: Literal["MODEL"] | Literal["BONE"] = "MODEL"
        for line in lines[1:]:
            line = line.replace("\t", " ").strip("")  # .split(" ", 1)
            if line == "":
                continue
            if line.startswith("#"):
                continue
            if line == "NEXT":
                mode = "MODEL"
                continue

            k, v = [x.strip() for x in line.split(maxsplit=1)]
            if k == "[ENTRY]":
                trans_list[-1].bones.append(BONE_TRANS_DATA(v))
                mode = "BONE"
                continue

            match mode:
                case "MODEL":
                    match k:
                        case "[name]":
                            trans_list.append(MODEL_TRANS_DATA(v))
                        case "[scale]":
                            trans_list[-1].scale = float(v)
                        case "[pos]":
                            x, y, z = v.split()
                            trans_list[-1].pos = (
                                float(x),
                                float(y),
                                float(z),
                            )
                        case "[range]":
                            scale_min, scale_max = v.split(maxsplit=1)
                            trans_list[-1].scale_min = float(scale_min)
                            trans_list[-1].scale_max = float(scale_max)
                        case "[default]":
                            trans_list[-1].scale_default = float(v)
                        case _:
                            raise RuntimeError()

                case "BONE":
                    match k:
                        case "[scale]":
                            trans_list[-1].bones[-1].length = float(v)
                            trans_list[-1].bones[-1].thick = float(v)
                        case "[length]":
                            trans_list[-1].bones[-1].length = float(v)
                        case "[thick]":
                            trans_list[-1].bones[-1].thick = float(v)
                        case "[pos]":
                            x, y, z = v.split()
                            trans_list[-1].bones[-1].pos = (
                                float(x),
                                float(y),
                                float(z),
                            )
                        case _:
                            raise RuntimeError()

        return trans_list

    def make_scaled(
        self,
        var: float,
    ) -> "MODEL_TRANS_DATA":
        new_scale = self.scale * var + 1 - self.scale

        new_pos = (
            self.pos[0] * var,
            self.pos[1] * var,
            self.pos[2] * var,
        )

        new_rot = (
            self.rot[0] * var,
            self.rot[1] * var,
            self.rot[2] * var,
        )

        def scale(
            v: tuple[float, float, float], var: float
        ) -> tuple[float, float, float]:
            x, y, z = v
            return (x * var, y * var, z * var)

        new_bones = [
            BONE_TRANS_DATA(
                bone.name,
                bone.length * var + 1 - bone.length,
                bone.thick * var + 1 - bone.thick,
                scale(bone.pos, var),
                scale(bone.rot, var),
            )
            for bone in self.bones
        ]

        return MODEL_TRANS_DATA(
            self.name,
            scale=new_scale,
            pos=new_pos,
            rot=new_rot,
            bones=new_bones,
        )
