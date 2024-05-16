from typing import Sequence
import dataclasses


class MATERIAL:
    def __init__(
        self,
        diff_col: tuple[float, float, float],
        alpha: float,
        spec: float,
        spec_col: tuple[float, float, float],
        mirr_col: tuple[float, float, float],
        toon: int,
        edge: int,
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


@dataclasses.dataclass
class TOON:
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
    )
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
    )

    def name_cp932(
        self,
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
        return (
            self.name[0].encode("cp932", "replace"),
            self.name[1].encode("cp932", "replace"),
            self.name[2].encode("cp932", "replace"),
            self.name[3].encode("cp932", "replace"),
            self.name[4].encode("cp932", "replace"),
            self.name[5].encode("cp932", "replace"),
            self.name[6].encode("cp932", "replace"),
            self.name[7].encode("cp932", "replace"),
            self.name[8].encode("cp932", "replace"),
            self.name[9].encode("cp932", "replace"),
        )

    def path_cp932(
        self,
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes, bytes]:
        return (
            self.path[0].encode("cp932", "replace"),
            self.path[1].encode("cp932", "replace"),
            self.path[2].encode("cp932", "replace"),
            self.path[3].encode("cp932", "replace"),
            self.path[4].encode("cp932", "replace"),
            self.path[5].encode("cp932", "replace"),
            self.path[6].encode("cp932", "replace"),
            self.path[7].encode("cp932", "replace"),
            self.path[8].encode("cp932", "replace"),
            self.path[9].encode("cp932", "replace"),
        )

    @staticmethod
    def from_bytes(
        name: Sequence[bytes], path: Sequence[bytes] | None = None
    ) -> "TOON":
        return TOON(
            tuple(x.decode("cp932", "replace") for x in name),  # type: ignore
            tuple(x.decode("cp932", "replace") for x in path) if path else tuple([""] * 10),  # type: ignore
        )
