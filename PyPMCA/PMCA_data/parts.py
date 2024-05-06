from typing import List


class PARTS:
    """
    パーツデータ
    """

    def __init__(
        self,
        name: str = "",
        comment: str = "",
        path: str = "",
        t: list[str] = [],
        joint=[],
        props={},
    ):
        self.name = name
        self.comment = comment
        self.path = path
        self.type = t
        self.joint = joint
        self.props = props

    @staticmethod
    def load_list(lines: List[str]) -> List["PARTS"]:
        """
        設定ファイル読み込み
        """
        parts_list: List[PARTS] = []
        directry = ""
        active = PARTS(props={})
        for l in lines:
            line = l.rstrip("\n").replace("\t", " ").split(" ", 1)
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
                active.type = active.type + line[1].split(",")
            elif line[0] == "[joint]":
                active.joint = active.joint + line[1].split(",")
            elif line[0][:1] == "[" and line[0][-1:] == "]":
                if line[0][1:-1] in active.props:
                    active.props[line[0][1:-1]].append(line[1])
                else:
                    active.props[line[0][1:-1]] = [line[1]]
        parts_list.append(active)
        return parts_list
