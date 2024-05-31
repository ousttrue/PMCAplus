from typing import Iterator
import pathlib
import logging
import re
import dataclasses


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PARTS:
    """
    パーツデータ

    PMCA Parts list v2.0

    SETDIR ./parts/

    [name] マフラー1
    [comment] 防寒具
    [type] body_acce
    [path] bdac_mt_muffler1.pmd
    [joint] body_acce
    [pic] bdac_mt_muffler1.png

    NEXT
    """

    name: str
    joint: list[str]
    path: pathlib.Path | None = None
    comment: str = ""
    type: list[str] = dataclasses.field(default_factory=list)
    props: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def from_lines(directory: pathlib.Path | None, lines: list[str]) -> "PARTS":
        name = ""
        path: pathlib.Path | None = None
        comment = ""
        head_types: list[str] = []
        joint: list[str] = []
        props: dict[str, str] = {}

        for l in lines:
            l = l.strip()
            if l == "":
                continue
            if l.startswith("#"):
                continue

            m = re.match(r"\[([^]]+)\]\s*(.*)", l)
            if m:
                match m.group(1):
                    case "name":
                        name = m.group(2)
                    case "path":
                        assert directory
                        path = directory / m.group(2)
                    case "comment":
                        comment = m.group(2)
                    case "type":
                        for x in m.group(2).split(","):
                            x = x.strip()
                            if x:
                                head_types.append(x)
                    case "joint":
                        for x in m.group(2).split(","):
                            x = x.strip()
                            if x:
                                joint.append(x)
                    case _:
                        props[m.group(1)] = m.group(2)
            else:
                LOGGER.debug(l)

        assert name
        p = PARTS(name, joint, path, comment, head_types, props)
        # LOGGER.debug(p)
        return p

    @staticmethod
    def parse(lines: list[str]) -> Iterator["PARTS"]:
        """
        設定ファイル読み込み
        """
        if lines[0].strip() == "PMCA Parts list v2.0":
            lines.pop(0)

        directory: pathlib.Path | None = None
        start = 0
        for i, l in enumerate(lines):
            l = l.strip()
            if l.startswith("SETDIR"):
                directory = pathlib.Path(l[6:].strip())
                start = i + 1
            elif l == "NEXT":
                yield PARTS.from_lines(directory, lines[start:i])
                start = i + 1

        yield PARTS.from_lines(directory, lines[start:])
