import logging
from ..PMCA_data.parts import PARTS
import PMCA  # type: ignore
import sys
from ..pmd_type import pmd


LOGGER = logging.getLogger(__name__)


class TREE_LIST:
    def __init__(
        self,
        node: "NODE | None" = None,
        depth: int = 0,
        text: str = "",
        c_num: int = -1,
    ):
        self.node = node
        self.depth = depth
        self.text = text
        self.c_num = c_num


class NODE:  # モデルのパーツツリー
    def __init__(
        self,
        parts: PARTS,
        depth: int = 0,
        children: list["NODE|None"] = [],
        list_num: int = -1,
    ):
        self.parts = parts
        self.depth = depth
        self.children = children
        self.list_num = list_num

    def assemble(self, num: int, app):
        app.script_fin = []
        PMCA.Create_PMD(num)
        PMCA.Load_PMD(num, self.parts.path.encode(sys.getdefaultencoding(), "replace"))
        info_data = PMCA.getInfo(0)
        info = pmd.INFO(info_data)
        line = info.comment.split("\n")

        app.authors = []
        app.licenses = []
        if info.name != "":
            app.authors = ["Unknown"]
            app.licenses = ["Nonfree"]

        app.functions = PMCA
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
            app.script_fin.extend(self.parts.props["script_fin"])

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
        LOGGER.debug("パーツのパス:%s" % (self.parts.path))
        for x in self.children:
            if x != None:
                x.assemble_child(num, app)

        PMCA.Sort_PMD(num)

        for x in app.script_fin:
            argv = x.split()
            fp = open(argv[0], "r", encoding="utf-8-sig")
            script = fp.read()
            exec(script)
            fp.close

    def assemble_child(self, num, app):
        pmpy = app
        LOGGER.info("パーツのパス:%s" % (self.parts.path))

        PMCA.Create_PMD(4)
        PMCA.Load_PMD(4, self.parts.path.encode(sys.getdefaultencoding(), "replace"))

        info_data = PMCA.getInfo(4)
        info = pmd.INFO(info_data)
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
                        for y in app.authors:
                            if x == y:
                                break
                        else:
                            app.authors.append(x)

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                if len(tmp) > 1:
                    flag_license = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        for y in app.licenses:
                            if x == y:
                                break
                        else:
                            app.licenses.append(x)
        if info.name != "":
            if flag_author == False:
                for x in app.authors:
                    if x == "Unknown":
                        break
                else:
                    app.authors.append("Unknown")
            if flag_license == False:
                for x in app.licenses:
                    if x == "Nonfree":
                        break
                else:
                    app.licenses.append("Nonfree")

        if "script_pre" in self.parts.props:
            for x in self.parts.props["script_pre"]:
                LOGGER.debug("プレスクリプト実行")
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
            app.script_fin.extend(self.parts.props["script_fin"])

        for x in self.children:
            if x != None:
                x.assemble_child(num, app)

    def create_list(self) -> list["TREE_LIST"]:
        l: list[TREE_LIST] = [
            TREE_LIST(
                node=self, depth=self.depth, text="  " * self.depth + self.parts.name
            )
        ]
        for i, x in enumerate(self.children):
            if x != None:
                l.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=("  " * (self.depth + 1)) + self.children[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(l)
            elif self.parts.joint[i] != "":
                l.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )
        return l

    def list_add(self, list):
        for i, x in enumerate(self.children):
            if x != None:
                list.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + self.children[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(list)
            elif self.parts.joint[i] != "":
                list.append(
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
        for x in self.children:
            if x != None:
                x.recalc_depth(depth)

    def node_to_text(self):
        lines = []
        lines.append("[Name] %s" % (self.parts.name))
        lines.append("[Path] %s" % (self.parts.path))
        lines.append("[Child]")
        for x in self.children:
            if x != None:
                lines.extend(x.node_to_text())
            else:
                lines.append("None")
        lines.append("[Parent]")
        return lines

    def text_to_node(self, parts_list: list[PARTS], lines: list[str]) -> None:
        LOGGER.info("parse nodes")
        tmp = [None, None]
        curnode = self
        parents = [self]
        child_nums = [0]
        count = 0

        while count < len(lines):
            line = lines[count].split(" ")
            if len(parents) == 0:
                break
            if line[0] == "None":
                tmp = [None, None]
                child_nums[-1] += 1

            elif line[0] == "[Name]":
                tmp[0] = line[1]

            elif line[0] == "[Path]":
                if len(line) == 1:
                    tmp[1] = ""
                else:
                    tmp[1] = line[1]

            elif line[0] == "[Child]":

                tp = None
                if tmp[0] != None:
                    for y in parts_list:
                        if y.name == tmp[0]:
                            tp = y
                            break
                    else:
                        for y in parts_list:
                            if y.path == tmp[1]:
                                tp = y
                                break

                if tp != None:
                    curnode.children[child_nums[-1]] = NODE(
                        parts=y, depth=curnode.depth + 1, children=[]
                    )
                    parents.append(curnode)
                    curnode = curnode.children[child_nums[-1]]
                    child_nums.append(0)
                    for x in curnode.parts.joint:
                        curnode.children.append(None)

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

            elif line[0] == "[Parent]":
                curnode = parents.pop()
                child_nums.pop()
                if len(child_nums) > 0:
                    child_nums[-1] += 1
            elif line[0] == "MATERIAL":
                break
            count += 1

        self.recalc_depth
