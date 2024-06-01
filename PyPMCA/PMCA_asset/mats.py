from typing import List
import dataclasses
import logging


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class MATS_ENTRY:
    name: str
    tex: str | None = None
    tex_path: str | None = None
    sph: str | None = None
    sph_path: str | None = None
    toon: tuple[int, str] | None = None
    diff_rgb: tuple[float, float, float] | None = None
    alpha: float | None = None
    spec_rgb: tuple[float, float, float] | None = None
    mirr_rgb: tuple[float, float, float] | None = None
    author: str | None = None
    license: str | None = None


@dataclasses.dataclass
class MATS:
    """
    材質データ
    PMCA Materials list v2.0

    SETDIR ./parts/

    [name] mt_hair
    [comment] 髪の色

    [ENTRY] 青色01
    [tex]	mt_hair_bl01.png
    [toon] 6 toon_mt_hair_bl01.bmp
    [diff_rgb] 0.80 0.80 0.80
    [spec_rgb] 0.08 0.22 0.37
    [mirr_rgb] 0.37 0.65 0.63
    [author] mato

    """

    name: str
    comment: str = ""
    entries: list[MATS_ENTRY] = dataclasses.field(default_factory=list)
    props: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def load_list(lines: List[str]) -> List["MATS"]:
        lines.pop(0)
        mats_list: List[MATS] = []

        directry = ""
        active: MATS | None = None
        for l in lines:
            l = l.replace("\t", " ").strip()
            if l == "":
                continue
            if l.startswith("#"):
                continue
            if l.startswith("SETDIR "):
                directry = l[7:].strip()
                continue
            if l == "NEXT":
                active = None
                continue

            k, v = [x.strip() for x in l.split(maxsplit=1)]
            match k:
                case "[name]":
                    active = None
                    for x in mats_list:
                        if x.name == v:
                            active = x
                            break
                    if not active:
                        active = MATS(v)
                        mats_list.append(active)
                case "[comment]":
                    assert active
                    active.comment = v
                case "[ENTRY]":
                    assert active
                    active.entries.append(MATS_ENTRY(name=v))

                case "[author]":
                    assert active
                    active.entries[-1].author = v
                case "[license]":
                    assert active
                    active.entries[-1].license = v
                case "[tex]":
                    assert active
                    active.entries[-1].tex = v
                    active.entries[-1].tex_path = directry + v
                case "[sph]":
                    assert active
                    active.entries[-1].sph = v
                    active.entries[-1].sph_path = directry + v
                case "[toon]":
                    assert active
                    index, toon = [x.strip() for x in v.split(maxsplit=1)]
                    active.entries[-1].toon = (int(index), toon)
                case "[diff_rgb]":
                    assert active
                    r, g, b = [x.strip() for x in v.split()]
                    active.entries[-1].diff_rgb = (float(r), float(g), float(b))
                case "[spec_rgb]":
                    assert active
                    r, g, b = [x.strip() for x in v.split()]
                    active.entries[-1].spec_rgb = (float(r), float(g), float(b))
                case "[mirr_rgb]":
                    assert active
                    r, g, b = [x.strip() for x in v.split()]
                    active.entries[-1].mirr_rgb = (float(r), float(g), float(b))
                case "alpha":
                    assert active
                    active.entries[-1].alpha = float(v)
                case _:
                    raise RuntimeError()

        return list(filter(lambda m: len(m.entries) > 0, mats_list))
