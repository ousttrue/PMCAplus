import converter
import pathlib
import logging

from . import parts
from . import material
from . import transform


LOGGER = logging.getLogger(__name__)


class PmcaAssets:
    def __init__(self) -> None:
        self.parts_list: list[parts.PARTS] = []
        self.mats_list: list[material.MATS] = []
        self.transform_list: list[transform.MODEL_TRANS_DATA] = []

    def load(self, dir: pathlib.Path):
        for x in dir.iterdir():
            if not x.is_file():
                continue
            if x.stem.startswith("."):
                continue

            converter.convert_oldversion(x)

            try:
                lines = x.read_text(encoding="utf-8-sig").splitlines()
                match lines[0]:
                    case "PMCA Parts list v2.0":
                        LOGGER.info(f"{x} => {lines[0]}")
                        self.parts_list += parts.PARTS.load(lines[1:])
                    case "PMCA Materials list v2.0":
                        LOGGER.info(f"{x} => {lines[0]}")
                        self.mats_list += material.MATS.load(lines)
                    case "PMCA Transform list v2.0":
                        LOGGER.info(f"{x} => {lines[0]}")
                        self.transform_list += transform.MODEL_TRANS_DATA.load(lines)
                    case _:
                        pass
            except Exception as ex:
                # LOGGER.exception(ex)
                raise ex
