import sys
from typing import Optional, Iterator, NamedTuple
import dataclasses
import PMCA_ctypes as PMCA
from .author_license import AuthorLicense
from . import types


@dataclasses.dataclass
class Joint:
    joint_type: str
    parts: Optional["PARTS"] = None

    def connect(self, child_parts: Optional["PARTS"]):
        if child_parts and self.parts:
            # copy child
            # TODO: recursive ?
            for dst in child_parts.child_joints:
                src_parts: PARTS | None = None
                for src in self.parts.child_joints:
                    if src.joint_type == dst.joint_type:
                        src_parts = src.parts
                        break
                if src_parts:
                    # print(f"{child_parts.name}.{dst} => {src_parts.name}")
                    dst.parts = src_parts
                else:
                    # print(f"{child_parts.name}.{dst} not found")
                    pass

        self.parts = child_parts


class TreeNode(NamedTuple):
    depth: int
    joint: Joint

    def make_entry(self) -> str:
        return f"{'  ' * self.depth}{self.joint.joint_type} => {self.joint.parts.name if self.joint.parts else '#None'}"


@dataclasses.dataclass
class PARTS:
    """
    読み込みパーツデータ
    """

    name: str = ""
    comment: str = ""
    path: str = ""
    joint_type: list[str] = dataclasses.field(default_factory=list)
    # note: 同じパーツが複数回使われるとうまくいかない
    # 体内に同じ joint が複数回あらわれうるのか
    child_joints: list[Joint] = dataclasses.field(default_factory=list)
    props: dict[str, list[str]] = dataclasses.field(default_factory=dict)

    @staticmethod
    def load(lines: list[str]) -> list["PARTS"]:
        """
        [name] セーラー服上半身01(スカート,長袖)
        [comment] 普通の長袖セーラー服、縦リボン
        [type] root
        [path] ub_mt_slr001_l_sk.pmd
        [joint] head,hand,lb_sk,body_acce
        [pic] ub_mt_slr001_l_sk.png

        NEXT
        """
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
                joints = [Joint(x) for x in line[1].split(",") if x]
                active.child_joints += joints
            elif line[0][:1] == "[" and line[0][-1:] == "]":
                if line[0][1:-1] in active.props:
                    active.props[line[0][1:-1]].append(line[1])
                else:
                    active.props[line[0][1:-1]] = [line[1]]
        parts_list.append(active)
        return parts_list

    def load_cnl(self, lines: list[str], parts_list: list["PARTS"]) -> None:
        curnode: PARTS = self
        parents: list[PARTS] = [self]
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
                    y: PARTS | None = None
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
                    assert y

                    if tp != None:
                        curnode.child_joints[child_nums[-1]].parts = y
                        parents.append(curnode)
                        curnode = y
                        child_nums.append(0)
                        for x in curnode.child_joints:
                            x.parts = None

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

    def traverse(self, level: int = 0) -> Iterator[TreeNode]:
        for joint in self.child_joints:
            yield TreeNode(level, joint)
            if joint.parts:
                for node in joint.parts.traverse(level + 1):
                    yield node

    def assemble(self, num: int) -> AuthorLicense:
        PMCA.Create_PMD(num)
        sysenc = sys.getfilesystemencoding()
        PMCA.Load_PMD(num, self.path.encode(sysenc, "replace"))
        info_data = PMCA.getInfo(0)
        info = types.INFO.create(info_data)
        line = info.comment.split("\n")
        author_license = AuthorLicense.create(info.name)

        if "script_pre" in self.props:
            for x in self.props["script_pre"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        if "script_post" in self.props:
            for x in self.props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        if "script_fin" in self.props:
            author_license.script_fin.extend(self.props["script_fin"])

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
        for x in self.child_joints:
            if x.parts != None:
                x.parts.assemble_child(num, author_license)

        PMCA.Sort_PMD(num)

        author_license.execute_scripts()

        return author_license

    def assemble_child(self, num: int, author_license: AuthorLicense) -> None:
        sysenc = sys.getfilesystemencoding()

        PMCA.Create_PMD(4)
        PMCA.Load_PMD(4, self.path.encode(sysenc, "replace"))

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

        if "script_pre" in self.props:
            for x in self.props["script_pre"]:
                print("プレスクリプト実行")
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        PMCA.Add_PMD(num, 4)
        PMCA.Marge_PMD(num)

        if "script_post" in self.props:
            for x in self.props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close
        if "script_fin" in self.props:
            author_license.script_fin.extend(self.props["script_fin"])

        for x in self.child_joints:
            if x.parts != None:
                x.parts.assemble_child(num, author_license)

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
