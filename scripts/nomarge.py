# -*- coding: utf-8 -*-

"""
for PMCAv0.0.6 beta2
重複するボーン名を変更して同名のボーンがあってもマージされないようにします
引数：なし

"""

import re
import logging

LOGGER = logging.getLogger(__name__)

LOGGER.info("プレスクリプト")
LOGGER.debug("ボーンマージ無効")
model = Get_PMD(0)
model2 = Get_PMD(4)
maxnum = -1
for y in model.bone:
    y.tmpname = None
    y.tmpnum = -1

for x in model2.bone:
    name = x.name.replace("+", "\+")
    name = name.replace("*", "\*")
    name = name.replace(".", "\.")
    name = name.replace("(", "\(")
    name = name.replace(")", "\)")
    name = name.replace("]", "\]")
    name = name.replace("[", "\[")
    p = re.compile("%s-?\d*\Z" % (name))
    for y in model.bone:
        m = p.match(y.name)
        if m != None:
            y.tmpname = x.name
            p2 = re.compile("-\d+\Z")
            m2 = p2.search(m.group())
            if m2 != None:
                # 番号付き一致
                y.tmpnum = int(m2.group()[1:])
                if maxnum < y.tmpnum:
                    maxnum = y.tmpnum
            else:
                # 番号なし一致
                y.tmpnum = 0
                if maxnum < 0:
                    maxnum = 0

maxnum += 1

if maxnum > 0:
    for x in model2.bone:
        x.name = "%s-%d" % (x.name, maxnum)

    for x in model.bone:
        if x.tmpnum == 0:
            x.name = "%s-%d" % (x.tmpname, x.tmpnum)

    Set_PMD(0, model)
    Set_PMD(4, model2)
