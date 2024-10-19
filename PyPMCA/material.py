import dataclasses


@dataclasses.dataclass
class MATS_ENTRY:
    name: str
    props: dict[str, str]


@dataclasses.dataclass
class MATS:
    """
    読み込み材質データ
    """

    name: str = ""
    comment: str = ""
    entries: list[MATS_ENTRY] = dataclasses.field(default_factory=list)
    props: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def load(lines: list[str]) -> list["MATS"]:
        directry = ""
        mats_list: list[MATS] = [MATS()]
        mode = 0
        active = mats_list[-1]
        for line in lines:
            line = line.rstrip("\n").replace("\t", " ").split(" ", 1)
            if line[0] == "":
                pass
            if line[0][:1] == "#":
                pass
            elif line[0] == "SETDIR":
                directry = line[1]

            elif line[0] == "NEXT":
                if len(active.entries) == 0:
                    mats_list.pop()
                mats_list.append(MATS(entries=[], props={}))
                active = mats_list[-1]
                mode = 0

            elif len(line) < 2:
                pass

            elif line[0] == "[ENTRY]":
                active.entries.append(MATS_ENTRY(name=line[1], props={}))
                mode = 1
            elif line[0] == "[name]":
                if mode == 0:
                    for x in mats_list:
                        if x.name == line[1]:
                            active = x
                            mats_list.pop()
                            break
                    else:
                        active.name = line[1]
            elif line[0] == "[comment]":
                if mode == 0:
                    active.comment = line[1]
            elif line[0] == "[tex]":
                active.entries[-1].props["tex"] = line[1]
                active.entries[-1].props["tex_path"] = directry + line[1]
            elif line[0] == "[sph]":
                active.entries[-1].props["sph"] = line[1]
                active.entries[-1].props["sph_path"] = directry + line[1]
            elif line[0][:1] == "[" and line[0][-5:] == "_rgb]":
                active.entries[-1].props[line[0][1:-1]] = line[1].split()
            elif line[0][:1] == "[" and line[0][-1:] == "]":
                if line[0][1:-1] in active.entries[-1].props:
                    active.entries[-1].props[line[0][1:-1]].append(line[1])
                else:
                    active.entries[-1].props[line[0][1:-1]] = [line[1]]
        return mats_list
