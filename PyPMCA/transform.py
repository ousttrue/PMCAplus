import dataclasses


@dataclasses.dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @staticmethod
    def from_str(x: str, y: str, z: str) -> "Vec3":
        return Vec3(float(x), float(y), float(z))

    def __mul__(self, rhs: float) -> "Vec3":
        return Vec3(self.x * rhs, self.y * rhs, self.z * rhs)

    def __iadd__(self, rhs: "Vec3") -> "Vec3":
        self.x += rhs.x
        self.y += rhs.y
        self.z += rhs.z
        return self


@dataclasses.dataclass
class BONE_TRANS_DATA:
    name: str = ""
    length: float = 0.0
    thick: float = 0.0
    pos: Vec3 = dataclasses.field(default_factory=Vec3)
    rot: Vec3 = dataclasses.field(default_factory=Vec3)
    props: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class MODEL_TRANS_DATA:
    name: str = ""
    scale: float = 1.0
    pos: Vec3 = dataclasses.field(default_factory=Vec3)
    rot: Vec3 = dataclasses.field(default_factory=Vec3)
    bones: list[BONE_TRANS_DATA] = dataclasses.field(default_factory=list)
    limit: tuple[float, float] = (0.0, 2.0)
    default: float = 1.0
    gamma: float = 1.0
    props: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def load(lines: list[str]) -> list["MODEL_TRANS_DATA"]:
        trans_list: list[MODEL_TRANS_DATA] = [MODEL_TRANS_DATA()]
        mode = 0
        for line in lines:
            line = line.rstrip("\n").replace("\t", " ").split(" ", 1)
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
        """
        mats_list.append(mats_list[-1])
        if mats_list[-1].entries[-1].__class__.__name__ == 'MATS_ENTRY':
            mats_list[-1].entries.append(mats_list[-1].entries[-1])
        """

        return trans_list

    def list_to_text(self):
        lines = []
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

    def text_to_list(self, lines):
        tmp = ["", "", None]
        i = 0
        try:
            while lines[i] != "TRANSFORM":
                i += 1
        except:
            return None

        i += 1
        print("体型調整読み込み")
        for j, x in enumerate(lines[i:]):
            x = x.split(" ")
            if x[0] == "[Name]":
                self.name = x[1]
            elif x[0] == "[Scale]":
                self.scale = float(x[1])
            elif x[0] == "[Pos]":
                self.pos = Vec3.from_str(*x[1:4])
            elif x[0] == "[Rot]":
                self.rot = Vec3.from_str(*x[1:4])
            elif x[0] == "BONES":
                break
        self.bones = []
        self.bones.append(BONE_TRANS_DATA())
        for x in lines[i + j :]:
            x = x.split(" ")
            print(x)
            if x[0] == "[Name]":
                self.bones[-1].name = x[1]
            elif x[0] == "[Length]":
                self.bones[-1].length = float(x[1])
            elif x[0] == "[Thick]":
                self.bones[-1].thick = float(x[1])
            elif x[0] == "[Pos]":
                self.bones[-1].pos = Vec3.from_str(*x[1:4])
            elif x[0] == "[Rot]":
                self.bones[-1].rot = Vec3.from_str(*x[1:4])
            elif x[0] == "NEXT":
                if self.bones[-1].name != "":
                    self.bones.append(BONE_TRANS_DATA())
