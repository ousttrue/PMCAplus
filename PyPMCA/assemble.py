from typing import NamedTuple
import logging
from . import pmd_type


LOGGER = logging.getLogger(__name__)


class AssembleContext(NamedTuple):
    script_fin: list[str] = []
    authors: list[str] = []
    licenses: list[str] = []

    def pre_process(self, info: pmd_type.INFO, props: dict[str, str]):
        flag_author = False
        flag_license = False

        line = info.comment.split("\n")
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
                        for y in self.authors:
                            if x == y:
                                break
                        else:
                            self.authors.append(x)

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                if len(tmp) > 1:
                    flag_license = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        for y in self.licenses:
                            if x == y:
                                break
                        else:
                            self.licenses.append(x)

        if info.name != "":
            if flag_author == False:
                for x in self.authors:
                    if x == "Unknown":
                        break
                else:
                    self.authors.append("Unknown")
            if flag_license == False:
                for x in self.licenses:
                    if x == "Nonfree":
                        break
                else:
                    self.licenses.append("Nonfree")

        def run_script(x: str) -> None:
            LOGGER.debug(f"プレスクリプト実行: {x}")
            # argv = x.split()
            # fp = open(argv[0], "r", encoding="utf-8-sig")
            # script = fp.read()
            # exec(script)
            # fp.close

        match props.get("script_pre"):
            case str() as s:
                run_script(s)

            case list() as l:
                for x in l:
                    run_script(x)

            case None:
                pass

            case _:
                raise RuntimeError()

    def post_process(self, props: dict[str, str]):
        if "script_post" in props:
            for x in props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close
        if "script_fin" in props:
            self.script_fin.extend(props["script_fin"])

    def finalize(self):
        for x in self.script_fin:
            argv = x.split()
            with open(argv[0], "r", encoding="utf-8-sig") as fp:
                script = fp.read()
                exec(script)
