from typing import Callable
import logging
import pathlib
import PMCA
from . import pmd_type
from . import PMCA_asset
from . import PMCA_cnl
from . import native

LOGGER = logging.getLogger(__name__)


class App:
    """
    UI 操作 => パーツ組み換え => 描画更新
    """

    def __init__(self, asset_dir: pathlib.Path):
        # data
        self.data = PMCA_asset.PMCAData()
        list_txt = self.data.load_asset(asset_dir)
        if list_txt:
            native.set_list(*list_txt)

        self.cnl = PMCA_cnl.CnlInfo()
        self.cnl_file = pathlib.Path()
        self.on_assemble: list[Callable[[], None]] = []

    def load(self, cnl_file: pathlib.Path | None = None):
        if cnl_file:
            self.cnl_file = cnl_file
        else:
            cnl_file = self.cnl_file
        self.cnl.load_CNL_File(cnl_file, self.data)
        self.assemble()

    def assemble(self):
        """
        cnl の変更を MODEL=0 に反映して描画を更新する
        """
        LOGGER.info("モデル組立て")
        context = native.assemble(self.cnl.tree, 0)

        # PMCA.Copy_PMD(0, 1)

        LOGGER.info("材質置換")
        materials = native.get_material()
        self.cnl.update_mat_rep(self.data, materials)
        native.set_material(context, self.cnl.mat_rep)

        # PMCA.Copy_PMD(0, 2)

        LOGGER.info("体型調整")
        info_data = PMCA.getInfo(0)
        tmpbone = native.get_bones(info_data)

        refbone = None
        refbone_index = None
        for i, transform_bone in enumerate(tmpbone):
            if transform_bone.name == "右足首":
                refbone = transform_bone
                refbone_index = i
                break

        for transform_data in self.cnl.transform_data_list:
            PMCA.Resize_Model(0, transform_data.scale)
            for transform_bone in transform_data.bones:
                PMCA.Resize_Bone(
                    0,
                    transform_bone.name.encode("cp932", "replace"),
                    transform_bone.length,
                    transform_bone.thick,
                )
                PMCA.Move_Bone(
                    0,
                    transform_bone.name.encode("cp932", "replace"),
                    transform_bone.pos[0],
                    transform_bone.pos[1],
                    transform_bone.pos[2],
                )

        if refbone:
            assert refbone_index
            newbone = None
            tmp = PMCA.getBone(0, refbone_index)
            assert tmp
            newbone = pmd_type.BONE(
                tmp["name"],
                tmp["name_eng"],
                tmp["parent"],
                tmp["tail"],
                tmp["type"],
                tmp["IK"],
                tmp["loc"],
            )

            # 体型調整による足首の移動量で設置を調整
            dy = refbone.loc[1] - newbone.loc[1]
            for transform_bone in tmpbone:
                i = transform_bone.parent
                count = 0
                while i < info_data["bone_count"] and count < info_data["bone_count"]:
                    if tmpbone[i].name == "センター":
                        PMCA.Move_Bone(
                            0, transform_bone.name.encode("cp932", "replace"), 0, dy, 0
                        )
                        break
                    i = tmpbone[i].parent
                    count += 1

            PMCA.Move_Bone(0, "センター".encode("cp932", "replace"), 0, dy, 0)
            PMCA.Move_Bone(0, "+センター".encode("cp932", "replace"), 0, -dy, 0)

        for transform_data in self.cnl.transform_data_list:
            PMCA.Move_Model(
                0, transform_data.pos[0], transform_data.pos[1], transform_data.pos[2]
            )

        PMCA.Update_Skin(0)
        PMCA.Adjust_Joints(0)

        # w, h, t = PMCA.getWHT(0)
        # self.cnl.on_refresh()
        for callback in self.on_assemble:
            callback()
