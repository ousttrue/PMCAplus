import dataclasses


@dataclasses.dataclass
class PARTS:
    """
    読み込みパーツデータ
    """

    name: str = ""
    comment: str = ""
    path: str = ""
    joint_type: list[str] = dataclasses.field(default_factory=list)
    child_joints: list[str] = dataclasses.field(default_factory=list)
    props: dict[str, list[str]] = dataclasses.field(default_factory=dict)

    @staticmethod
    def load(lines: list[str]) -> list["PARTS"]:
        directry = ""
        active = PARTS()
        parts_list: list[PARTS] = []
        for line in lines:
            line = line.rstrip("\n").replace("\t", " ").split(" ", 1)
            if line[0] == "":
                pass
            if line[0][:1] == "#":
                pass
            elif line[0] == "SETDIR":
                directry = line[1]

            elif line[0] == "NEXT":
                parts_list.append(active)
                active = PARTS(props={})

            elif len(line) < 2:
                pass
            elif line[0] == "[name]":
                active.name = line[1]
            elif line[0] == "[path]":
                active.path = directry + line[1]
            elif line[0] == "[comment]":
                active.comment = line[1]
            elif line[0] == "[type]":
                active.joint_type = active.joint_type + line[1].split(",")
            elif line[0] == "[joint]":
                active.child_joints = active.child_joints + line[1].split(",")
            elif line[0][:1] == "[" and line[0][-1:] == "]":
                if line[0][1:-1] in active.props:
                    active.props[line[0][1:-1]].append(line[1])
                else:
                    active.props[line[0][1:-1]] = [line[1]]
        parts_list.append(active)
        return parts_list
