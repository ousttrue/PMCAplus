#! /usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Callable
import sys, os.path
import os
import dataclasses
import PMCA
from .translation import TranslationList
from .parts import PARTS
from .material import MATS
from .transform import MODEL_TRANS_DATA, BONE_TRANS_DATA, Vec3
from .node import NODE
from . import types
from .pmca_data import PmcaData


__all__ = [
    "TranslationList",
    "PARTS",
    "MATS",
    "MODEL_TRANS_DATA",
    "BONE_TRANS_DATA",
    "Vec3",
    "NODE",
    "PmcaData",
]


@dataclasses.dataclass
class MODELINFO:
    name: str = "PMCAモデル"
    name_l: str = "PMCAモデル"
    comment: str = ""
    name_eng: str = "PMCA model"
    name_l_eng: str = "PMCA generated model"
    comment_eng: str = ""






def Set_Name_Comment(num=0, name="", comment="", name_eng="", comment_eng=""):
    PMCA.Set_Name_Comment(
        num,
        name.encode("cp932", "replace"),
        comment.encode("cp932", "replace"),
        name.encode("cp932", "replace"),
        comment.encode("cp932", "replace"),
    )
