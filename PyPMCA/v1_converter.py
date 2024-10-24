#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List
import pathlib
import sys
import os
import subprocess
import logging


LOGGER = logging.getLogger(__name__)
sys.path.append(os.getcwd())


def main():
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得

    tmp = argvs[0].rsplit("/", 1)
    tmp = tmp.rsplit("/", 1)

    curd = tmp[0]

    path = "%s/PMCA_1.0-2.0converter" % (curd)

    v1_v2(path, argvs[1:])


def v1_v2(path: pathlib.Path, argvs: List[str]):
    for x in argvs:
        cmd = "%s %s" % (path, x)

        subprocess.call(cmd, shell=True)

        fp = open("%s" % (x), "r", encoding="cp932")
        lines = fp.read()
        fp.close()

        fp = open("%s" % (x), "w", encoding="utf-8")
        fp.write(lines)
        fp.close()
        LOGGER.info("文字コードをUTF8に変換しました: %s", path)


if __name__ == "__main__":
    main()
