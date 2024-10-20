from typing import Any
import sys
import dataclasses
import PMCA
from . import types
from .parts import PARTS
from .author_license import AuthorLicense


@dataclasses.dataclass
class NODE:
    """
    モデルのパーツツリー
    """

    # def __init__(self, parts="", depth=0, child=[], list_num=-1):
    parts: PARTS
    depth: int = 0
    child: list[Any] = dataclasses.field(default_factory=list)
    list_num: int = -1

    @staticmethod
    def make_root() -> "NODE":
        return NODE(
            parts=PARTS(name="ROOT", joint=["root"]),
            depth=-1,
            child=[None],
        )

    @staticmethod
    def load(lines: list[str], parts_list: list[PARTS]) -> "NODE":
        root = NODE.make_root()
        curnode = root
        parents: list[NODE] = [root]
        child_nums = [0]
        count = 0
        while lines[count] != "PARTS":
            count += 1
        count += 1

        name = ""
        path = ""
        while count < len(lines):
            line = lines[count].split(" ")
            if len(parents) == 0:
                # empty statck
                break

            match line[0]:
                case "None":
                    name = ""
                    path = ""
                    child_nums[-1] += 1

                case "[Name]":
                    name = line[1]

                case "[Path]":
                    if len(line) == 1:
                        path = ""
                    else:
                        path = line[1]

                case "[Child]":

                    tp: PARTS | None = None
                    if name:
                        for y in parts_list:
                            if y.name == name:
                                tp = y
                                break
                    if not tp and path:
                        for y in parts_list:
                            if y.path == path:
                                tp = y
                                break

                    if tp != None:
                        curnode.child[child_nums[-1]] = NODE(
                            parts=y, depth=curnode.depth + 1, child=[]
                        )
                        parents.append(curnode)
                        curnode = curnode.child[child_nums[-1]]
                        child_nums.append(0)
                        for x in curnode.parts.joint:
                            curnode.child.append(None)

                    else:
                        depc = 1
                        while depc == 0:
                            count += 1
                            if lines[count] == "[Child]":
                                depc += 1
                            if lines[count] == "[Parent]":
                                depc -= 1
                        parents.pop()
                        child_nums.pop()
                        child_nums[-1] += 1

                case "[Parent]":
                    curnode = parents.pop()
                    child_nums.pop()
                    if len(child_nums) > 0:
                        child_nums[-1] += 1

                case "MATERIAL":
                    break

                case _:
                    pass

            count += 1

        # root.recalc_depth()

        return root

    def assemble(self, num: int) -> AuthorLicense:
        PMCA.Create_PMD(num)
        sysenc = sys.getfilesystemencoding()
        PMCA.Load_PMD(num, self.parts.path.encode(sysenc, "replace"))
        info_data = PMCA.getInfo(0)
        info = types.INFO.create(info_data)
        line = info.comment.split("\n")
        author_license = AuthorLicense.create(info.name)

        if "script_pre" in self.parts.props:
            for x in self.parts.props["script_pre"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        if "script_post" in self.parts.props:
            for x in self.parts.props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        if "script_fin" in self.parts.props:
            author_license.script_fin.extend(self.parts.props["script_fin"])

        for x in line:
            tmp = x.split(":", 1)
            if len(tmp) == 1:
                tmp = x.split("：", 1)
            if (
                tmp[0] == "Author"
                or tmp[0] == "author"
                or tmp[0] == "Creator"
                or tmp[0] == "creator"
                or tmp[0] == "モデル制作"
            ):
                tmp[1] = tmp[1].replace("　", " ")
                app.authors = tmp[1].split(" ")

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                tmp[1] = tmp[1].replace("　", " ")
                app.licenses = tmp[1].split(" ")
        for x in self.child:
            if x != None:
                x.assemble_child(num, author_license)

        PMCA.Sort_PMD(num)

        author_license.execute_scripts()

        return author_license

    def assemble_child(self, num: int, author_license: AuthorLicense) -> None:
        sysenc = sys.getfilesystemencoding()

        PMCA.Create_PMD(4)
        PMCA.Load_PMD(4, self.parts.path.encode(sysenc, "replace"))

        info_data = PMCA.getInfo(4)
        info = types.INFO.create(info_data)
        line = info.comment.split("\n")
        flag_author = False
        flag_license = False
        for x in line:
            tmp = x.split(":", 1)
            if len(tmp) == 1:
                tmp = x.split("：", 1)
            if (
                tmp[0] == "Author"
                or tmp[0] == "author"
                or tmp[0] == "Creator"
                or tmp[0] == "creator"
                or tmp[0] == "モデル制作"
            ):
                if len(tmp) > 1:
                    flag_author = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        author_license.append_author(x)

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                if len(tmp) > 1:
                    flag_license = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        author_license.append_license(x)

        if info.name != "":
            if flag_author == False:
                author_license.append_author("Unknown")
            if flag_license == False:
                author_license.append_license("Nonfree")

        if "script_pre" in self.parts.props:
            for x in self.parts.props["script_pre"]:
                print("プレスクリプト実行")
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        PMCA.Add_PMD(num, 4)
        PMCA.Marge_PMD(num)

        if "script_post" in self.parts.props:
            for x in self.parts.props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close
        if "script_fin" in self.parts.props:
            author_license.script_fin.extend(self.parts.props["script_fin"])

        for x in self.child:
            if x != None:
                x.assemble_child(num, author_license)

    def create_list(self) -> list["TREE_LIST"]:
        List: list[TREE_LIST] = [
            # TREE_LIST(
            #     node=self, depth=self.depth, text="  " * self.depth + self.parts.name
            # )
        ]
        for i, x in enumerate(self.child):
            if x != None:
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + self.child[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(List)
            elif self.parts.joint[i] != "":
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )
        return List

    def list_add(self, List):
        for i, x in enumerate(self.child):
            if x != None:
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + self.child[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(List)
            elif self.parts.joint[i] != "":
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )

    def recalc_depth(self, depth):
        self.depth = depth
        depth = depth + 1
        for x in self.child:
            if x != None:
                x.recalc_depth(depth)

    def node_to_text(self):
        lines = []
        lines.append("[Name] %s" % (self.parts.name))
        lines.append("[Path] %s" % (self.parts.path))
        lines.append("[Child]")
        print(self.parts.path)
        for x in self.child:
            if x != None:
                lines.extend(x.node_to_text())
            else:
                lines.append("None")
        lines.append("[Parent]")
        return lines


@dataclasses.dataclass
class TREE_LIST:
    # def __init__(self, node=None, depth=0, text="", c_num=-1, list_num=0):
    node: NODE
    depth: int = 0
    text: str = ""
    c_num: int = -1
