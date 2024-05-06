import logging

LOGGER = logging.getLogger(__name__)


class BONE_TRANS_DATA:
    def __init__(
        self,
        name: str = "",
        length: float = 1.0,
        thick: float = 1.0,
        pos: list[float] = [0.0, 0.0, 0.0],
        rot: list[float] = [0.0, 0.0, 0.0],
        props: dict[str, str] = {},
    ):
        self.name = name
        self.length = length
        self.thick = thick
        self.pos = pos
        self.rot = rot
        self.props = props


class MODEL_TRANS_DATA:
    def __init__(
        self,
        name: str = "",
        scale: float = 1.0,
        pos=[0.0, 0.0, 0.0],
        rot=[0.0, 0.0, 0.0],
        bones=[],
        limit=[0.0, 2.0],
        default=1.0,
        gamma=1.0,
        props={},
    ):
        self.name = name
        self.scale = scale
        self.pos = pos
        self.rot = rot
        self.bones = bones
        self.limit = limit
        self.default = default
        self.gamma = gamma
        self.props = props

    def list_to_text(self) -> list[str]:
        lines: list[str] = []
        # lines.append('[Name] %s'%(self.name))
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

    def text_to_list(self, lines: list[str]):
        tmp = ["", "", None]
        i = 0
        try:
            while lines[i] != "TRANSFORM":
                i += 1
        except:
            return None

        i += 1
        LOGGER.info("体型調整読み込み")
        for j, x in enumerate(lines[i:]):
            x = x.split(" ")
            if x[0] == "[Name]":
                self.name = x[1]
            elif x[0] == "[Scale]":
                self.scale = float(x[1])
            elif x[0] == "[Pos]":
                self.pos[0] = float(x[1])
                self.pos[1] = float(x[2])
                self.pos[2] = float(x[3])
            elif x[0] == "[Rot]":
                self.rot[0] = float(x[1])
                self.rot[1] = float(x[2])
                self.rot[2] = float(x[3])
            elif x[0] == "BONES":
                break
        self.bones = []
        self.bones.append(BONE_TRANS_DATA())
        for x in lines[i + j :]:
            x = x.split(" ")
            if x[0] == "[Name]":
                self.bones[-1].name = x[1]
            elif x[0] == "[Length]":
                self.bones[-1].length = float(x[1])
            elif x[0] == "[Thick]":
                self.bones[-1].thick = float(x[1])
            elif x[0] == "[Pos]":
                self.bones[-1].pos[0] = float(x[1])
                self.bones[-1].pos[1] = float(x[2])
                self.bones[-1].pos[2] = float(x[3])
            elif x[0] == "[Rot]":
                self.bones[-1].rot[0] = float(x[1])
                self.bones[-1].rot[1] = float(x[2])
                self.bones[-1].rot[2] = float(x[3])
            elif x[0] == "NEXT":
                if self.bones[-1].name != "":
                    self.bones.append(BONE_TRANS_DATA())

    @staticmethod
    def load_list(lines: list[str]) -> list["MODEL_TRANS_DATA"]:
        trans_list: list[MODEL_TRANS_DATA] = []
        trans_list.append(MODEL_TRANS_DATA(bones=[]))

        mode = 0
        for l in lines:
            line = l.rstrip("\n").replace("\t", " ").split(" ", 1)
            if line[0] == "":
                pass
            if line[0][:1] == "#":
                pass
            elif line[0] == "NEXT":
                trans_list.append(MODEL_TRANS_DATA(scale=0.0, bones=[]))
                mode = 0

            elif len(line) < 2:
                pass

            elif line[0] == "[ENTRY]":
                trans_list[-1].bones.append(
                    BONE_TRANS_DATA(name=line[1], length=0.0, thick=0.0, props={})
                )
                mode = 1
            elif line[0] == "[name]":
                if mode == 0:
                    trans_list[-1].name = line[1]
            elif line[0] == "[scale]":
                if mode == 0:
                    trans_list[-1].scale = float(line[1])
                elif mode == 1:
                    trans_list[-1].bones[-1].length = float(line[1])
                    trans_list[-1].bones[-1].thick = float(line[1])
            elif line[0] == "[length]":
                if mode == 1:
                    trans_list[-1].bones[-1].length = float(line[1])
            elif line[0] == "[thick]":
                if mode == 1:
                    trans_list[-1].bones[-1].thick = float(line[1])
            elif line[0] == "[pos]":
                tmp = line[1].split(" ")
                if mode == 0:
                    trans_list[-1].pos = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
                elif mode == 1:
                    trans_list[-1].bones[-1].pos = [
                        float(tmp[0]),
                        float(tmp[1]),
                        float(tmp[2]),
                    ]
            elif line[0] == "[range]":
                tmp = line[1].split(" ")
                trans_list[-1].limit = [float(tmp[0]), float(tmp[1])]
            elif line[0] == "[default]":
                trans_list[-1].default = float(line[1])
            elif line[0][:1] == "[" and line[0][-1:] == "]":
                if line[0][1:-1] in trans_list[-1].props:
                    trans_list[-1].props[line[0][1:-1]].append(line[1])
                else:
                    trans_list[-1].props[line[0][1:-1]] = [line[1]]

        return trans_list
