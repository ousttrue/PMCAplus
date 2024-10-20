#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import pathlib


def v1_v2(path, argvs):
    # print(argvs)

    for x in argvs:
        cmd = "%s %s" % (path, x)
        # print(cmd)

        retcode = subprocess.call(cmd, shell=True)

        fp = open("%s" % (x), "r", encoding="cp932")
        lines = fp.read()
        fp.close()

        fp = open("%s" % (x), "w", encoding="utf-8")
        fp.write(lines)
        fp.close()
        # print("文字コードをUTF8に変換しました")


def convert_oldversion(x: pathlib.Path):
    fp = open(x, "r", encoding="cp932")
    try:
        lines = fp.read()
        line = lines.split("\n")
        line = line[0].replace("\n", "")
        if (
            line == "PMCA Parts list v1.0"
            or line == "PMCA Materials list v1.1"
            or line == "PMCA Materials list v1.0"
            or line == "PMCA Textures list v1.0"
            or line == "PMCA Bone_Group list v1.0"
        ):
            fp.close()

            logging.info(f"convert old version: {x}")
            if os.name == "posix":
                fp = open(x, "w", encoding="cp932")
                fp.write(lines)
                fp.close()
                converter.v1_v2("./converter/PMCA_1.0-2.0converter", [x])
            elif os.name == "nt":
                converter.v1_v2(".\\converter\\PMCA_1.0-2.0converter.exe", [x])
        if line == "bone":
            logging.info(f"convert old version: {x}")
            fp = open(x, "r", encoding="cp932")
            lines = fp.read()
            fp.close()

            fp = open(x, "w", encoding="utf-8")
            fp.write("PMCA list data v2.0\n")
            fp.write(lines)
            fp.close()

    except UnicodeDecodeError:
        fp.close()


def main():
    argvs = sys.argv  # コマンドライン引数を格納したリストの取得

    tmp = argvs[0].rsplit("/", 1)
    tmp = tmp.rsplit("/", 1)
    # print(tmp)

    curd = tmp[0]

    path = "%s/PMCA_1.0-2.0converter" % (curd)

    v1_v2(path, argvs[1:])


if __name__ == "__main__":
    main()
