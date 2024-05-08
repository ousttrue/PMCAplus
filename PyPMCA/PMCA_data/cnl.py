from typing import NamedTuple


class CnlInfo(NamedTuple):
    name: str
    name_l: str
    comment: list[str]


def read_info(lines: list[str]) -> tuple[list[str], CnlInfo]:
    name = lines.pop(0)
    name_l = lines.pop(0)
    comment: list[str] = []
    while len(lines) > 0:
        line = lines.pop(0)
        if line == "PARTS":
            return lines, CnlInfo(name, name_l, comment)
        elif line == "":
            pass
        else:
            comment.append(line)

    raise RuntimeError()
