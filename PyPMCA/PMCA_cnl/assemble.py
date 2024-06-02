import logging
from .. import pmd_type
from ..pmd_type import resize
from .. import PMCA_cnl
from .. import PMCA_asset


LOGGER = logging.getLogger(__name__)


class AssembleContext:

    def __init__(self):
        self.script_fin: list[str] = []
        self.authors: list[str] = []
        self.licenses: list[str] = []
        # 空モデル
        self.data0 = b""

    def process(self, tree: PMCA_cnl.NODE) -> bytes:
        if tree.parts:
            pmd0 = pmd_type.parse(self.data0)
            assert pmd0
            self.pre_process(pmd0.info, tree.parts.props)
            self.post_process(tree.parts.props)

        # Parts を合体
        for child in tree.children:
            if child.parts:
                self._assemble_child(child)

        # PMCA.Set_PMD(0, self.data0)
        # PMCA.Sort_PMD(0)
        self.finalize()
        return self.data0

    # static PyObject *Sort_PMD(PyObject *self, PyObject *args) {
    #   int num;
    #   if (!PyArg_ParseTuple(args, "i", &num))
    #     Py_RETURN_FALSE;
    #
    #   auto model = g_model[num];
    #   LOGD << "ボーンマージ";
    #   if (!model->marge_bone()) {
    #     Py_RETURN_FALSE;
    #   }
    #
    #   LOGD << "ボーンソート";
    #   model->sort_bone(&list);
    #
    #   LOGD << "表情ソート";
    #   model->sort_skin(&list);
    #
    #   LOGD << "ボーングループソート";
    #   model->sort_disp(&list);
    #
    #   //-0ボーン削除
    #   if (strcmp(model->bone[model->bone.size() - 1].name, "-0") == 0) {
    #     model->bone.pop_back();
    #   }
    #
    #   LOGD << "英語対応化";
    #   model->translate(&list, 1);
    #
    #   Py_RETURN_TRUE;
    # }
    def _assemble_child(self, current: PMCA_cnl.NODE) -> None:
        # 4 にロード
        assert current.parts and current.parts.path
        data4 = current.parts.path.read_bytes()

        # pmd_parts = pmd_type.parse(pathlib.Path(current.parts.path).read_bytes())
        # if pmd_parts:
        #     root.add(pmd_parts)

        pmd4 = pmd_type.parse(data4)
        assert pmd4
        self.pre_process(pmd4.info, current.parts.props)

        # 0 に 4 を合成
        self.data0 = resize.Add_PMD(self.data0, data4)
        self.data0 = resize.Marge_PMD(self.data0)

        self.post_process(current.parts.props)

        # 再帰
        for child in current.children:
            if child.parts:
                self._assemble_child(child)

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

    def apply(self, x: pmd_type.Submesh, mat: PMCA_asset.MATS_ENTRY) -> None:
        if mat.author != None:
            for y in mat.author.split(" "):
                if y not in self.authors:
                    self.authors.append(y)
        if mat.license != None:
            for y in mat.license.split(" "):
                if y not in self.licenses:
                    self.licenses.append(y)

        if mat.tex != None:
            x.tex = mat.tex
        if mat.tex_path != None:
            x.tex_path = mat.tex_path
        if mat.sph != None:
            x.sph = mat.sph
        if mat.sph_path != None:
            x.sph_path = mat.sph_path
        if mat.diff_rgb != None:
            x.diff_col = list(mat.diff_rgb)
        if mat.alpha != None:
            x.alpha = mat.alpha
        if mat.spec_rgb != None:
            x.spec_col = list(mat.spec_rgb)
        if mat.mirr_rgb != None:
            x.mirr_col = list(mat.mirr_rgb)
        if mat.toon != None:
            # update toon list
            pass
            # name = list(PMCA.getToon(0))
            # name[mat.toon[0]] = mat.toon[1].encode("cp932", "replace")
            # PMCA.setToon(0, name)

            # path = list(PMCA.getToonPath(0))
            # path[mat.toon[0]] = ("toon/" + mat.toon[1]).encode("cp932", "replace")
            # PMCA.setToonPath(0, path)

            # x.toon = mat.toon[0]
