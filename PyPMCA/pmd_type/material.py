from typing import Sequence


class MATERIAL:
    def __init__(
        self,
        diff_col: tuple[float, float, float],
        alpha: float,
        spec: float,
        spec_col: tuple[float, float, float],
        mirr_col: tuple[float, float, float],
        toon: int,
        edge: float,
        face_count: int,
        tex: bytes,
        sph: bytes,
        tex_path: bytes,
        sph_path: bytes,
    ):
        self.diff_col = diff_col
        self.alpha = alpha
        self.spec = spec
        self.spec_col = spec_col
        self.mirr_col = mirr_col
        self.toon = toon
        self.edge = edge
        self.face_count = face_count
        self.tex = tex.decode("cp932", "replace")
        self.sph = sph.decode("cp932", "replace")
        self.tex_path = tex_path.decode("cp932", "replace")
        self.sph_path = sph_path.decode("cp932", "replace")


class TOON:
    def __init__(
        self,
        name: tuple[
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
        ] = (
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ),
        path: tuple[
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
            str,
        ] = (
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ),
    ):
        self.name = name
        self.path = path

    @staticmethod
    def from_bytes(name: Sequence[bytes], path: Sequence[bytes]) -> "TOON":
        return TOON(
            tuple(x.decode("cp932", "replace") for x in name),  # type: ignore
            tuple(x.decode("cp932", "replace") for x in path),  # type: ignore
        )
