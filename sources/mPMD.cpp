#include "mPmd.h"


bool MODEL::load(const std::string &path)
{
	if (path.empty()) {
		return false;
	}

	static MODEL cache_model[64];
	static unsigned char count[64];
	static unsigned char cur_count = 255;

	//キャッシュまわり初期化
	if (cur_count == 255) {
		for (int i = 0; i<64; i++) {
			count[i] = 255;
			cache_model[i] = MODEL();
		}
		cur_count = 0;
	}

	if (cur_count > 64) {
		cur_count = 0;
	}
	else {
		cur_count++;
	}

	int i = 0;
	for (; i<64; i++) {
		if (count[i] != 255) {
			//printf("%s, %s\n", cache_model[i].header.path, file_name);
			if (cache_model[i].header.path == path) {
				*this = cache_model[i];
				count[i] = cur_count;
				break;
			}
		}
	}

	auto tmp = cur_count + 1;
	if (tmp >= 64)tmp = 0;
	int j = 0;
	for (; j<64; j++) {
		if (count[i] == tmp) {
			count[i] = 255;
			cache_model[i] = MODEL();
		}
	}
	if (i != 64) {
		//printf("Use Cache\n");
		return true;
	}

	auto pmd = fopen(path.c_str(), "rb");
	if (!pmd) {
		return false;
	}

	header.path = path;

	char magic[4];
	fread(magic, 1, 3, pmd);
	float version;
	fread(&version, 4, 1, pmd);
	if (memcmp(magic, "Pmd", 3) != 0 || version != 1.0) {
		return false;
	}

	header.name.fread<20>(pmd);
	header.comment.fread<256>(pmd);

	int vt_count;
	fread(&vt_count, 4, 1, pmd);
	vt.resize(vt_count);
	for (i = 0; i<(vt.size()); i++) {
		//fseek(pmd, 38, SEEK_CUR);
		fread(vt[i].loc, 4, 3, pmd);
		fread(vt[i].nor, 4, 3, pmd);
		fread(vt[i].uv, 4, 2, pmd);
		fread(&vt[i].bone_num0, 2, 1, pmd);
		fread(&vt[i].bone_num1, 2, 1, pmd);
		fread(&vt[i].bone_weight, 1, 1, pmd);
		fread(&vt[i].edge_flag, 1, 1, pmd);
	}

	int vt_index_count;
	fread(&vt_index_count, 4, 1, pmd);
	vt_index.resize(vt_index_count);
	for (i = 0; i<vt_index.size(); i++) {
		fread(&vt_index[i], 2, 1, pmd);
		if (vt_index[i] >= vt.size()) {
			return false;
		}
	}

	int mat_count;
	fread(&mat_count, 4, 1, pmd);
	mat.resize(mat_count);
	for (i = 0; i<mat.size(); i++) {
		fread(mat[i].diffuse, 4, 3, pmd);
		fread(&mat[i].alpha, 4, 1, pmd);
		fread(&mat[i].spec, 4, 1, pmd);
		fread(&mat[i].spec_col, 4, 3, pmd);
		fread(&mat[i].mirror_col, 4, 3, pmd);
		fread(&mat[i].toon_index, 1, 1, pmd);
		fread(&mat[i].edge_flag, 1, 1, pmd);
		fread(&mat[i].vt_index_count, 4, 1, pmd);
		mat[i].tex.fread<20>(pmd);
	}

	unsigned short bone_count;
	fread(&bone_count, 2, 1, pmd);
	bone.resize(bone_count);
	for (i = 0; i<bone.size(); i++) {
		bone[i].name.fread<20>(pmd);
		fread(&bone[i].PBone_index, 2, 1, pmd);
		fread(&bone[i].TBone_index, 2, 1, pmd);
		fread(&bone[i].type, 1, 1, pmd);
		fread(&bone[i].IKBone_index, 2, 1, pmd);
		fread(bone[i].loc, 4, 3, pmd);
	}

	unsigned short IK_count;
	fread(&IK_count, 2, 1, pmd);

	IK_list.resize(IK_count);
	for (i = 0; i<IK_list.size(); i++) {
		fread(&IK_list[i].IKBone_index, 2, 1, pmd);
		fread(&IK_list[i].IKTBone_index, 2, 1, pmd);
		unsigned char IK_chain_len;
		fread(&IK_chain_len, 1, 1, pmd);
		fread(&IK_list[i].iterations, 2, 1, pmd);
		fread(&IK_list[i].weight, 4, 1, pmd);
		IK_list[i].IKCBone_index.resize(IK_chain_len);
		if (IK_chain_len > 0) {
			fread(&IK_list[i].IKCBone_index[0], 2, IK_chain_len, pmd);
		}
	}

	unsigned short skin_count;
	fread(&skin_count, 2, 1, pmd);
	skin.resize(skin_count);
	for (i = 0; i<skin.size(); i++) {
		skin[i].name.fread<20>(pmd);
		unsigned int skin_vt_count;
		fread(&skin_vt_count, 4, 1, pmd);
		fread(&skin[i].type, 1, 1, pmd);
		skin[i].data.resize(skin_vt_count);
		for (j = 0; j<skin[i].data.size(); j++) {
			fread(&skin[i].data[j].index, 4, 1, pmd);
			if (skin[i].data[j].index > vt.size()) {
				exit(1);
			}
			fread(&skin[i].data[j].loc, 4, 3, pmd);
		}
	}

	unsigned char skin_disp_count;
	fread(&skin_disp_count, 1, 1, pmd);
	skin_index.resize(skin_disp_count);
	if (skin_disp_count) {
		fread(&skin_index[0], 2, skin_index.size(), pmd);
	}

	unsigned char bone_group_count;
	fread(&bone_group_count, 1, 1, pmd);
	bone_group.resize(bone_group_count);
	for (i = 0; i<bone_group_count; i++) {
		bone_group[i].name.fread<50>(pmd);
	}

	int bone_disp_count;
	fread(&bone_disp_count, 4, 1, pmd);
	bone_disp.resize(bone_disp_count);
	for (i = 0; i<bone_disp_count; i++) {
		fread(&bone_disp[i].index, 2, 1, pmd);
		fread(&bone_disp[i].bone_group, 1, 1, pmd);
	}

	fread(&eng_support, 1, 1, pmd);

	if (feof(pmd) != 0) {
		eng_support = 0;
		for (i = 0; i<10; i++) {
			j = i + 1;
			sprintf(toon[i].data(), "toon%02d.bmp\0", j);
		}
		rbody.clear();
		joint.clear();
		return true;
	}

	if (eng_support == 1) {
		header.name_eng.fread<20>(pmd);
		header.comment_eng.fread<256>(pmd);

		for (i = 0; i<bone.size(); i++) {
			bone[i].name_eng.fread<20>(pmd);
		}

		if (skin.size() > 0) {
			skin[0].name_eng = "base";
		}
		for (i = 1; i<skin.size(); i++) {
			skin[i].name_eng.fread<20>(pmd);
		}
		for (i = 0; i<bone_group.size(); i++) {
			bone_group[i].name_eng.fread<50>(pmd);
		}
	}

	for (i = 0; i<10; i++) {
		toon[i].fread<100>(pmd);
	}

	int rbody_count;
	fread(&rbody_count, 4, 1, pmd);
	rbody.resize(rbody_count);
	for (i = 0; i<rbody.size(); i++) {
		rbody[i].name.fread<20>(pmd);
		fread(&rbody[i].bone, 2, 1, pmd);
		fread(&rbody[i].group, 1, 1, pmd);
		fread(&rbody[i].target, 2, 1, pmd);
		fread(&rbody[i].shape, 1, 1, pmd);
		fread(rbody[i].size, 4, 3, pmd);
		fread(rbody[i].loc, 4, 3, pmd);
		fread(rbody[i].rot, 4, 3, pmd);
		fread(rbody[i].property, 4, 5, pmd);
		fread(&rbody[i].type, 1, 1, pmd);
	}

	int joint_count;
	fread(&joint_count, 4, 1, pmd);
	joint.resize(joint_count);
	for (i = 0; i<joint_count; i++) {
		joint[i].name.fread<20>(pmd);
		fread(joint[i].rbody, 4, 2, pmd);
		fread(joint[i].loc, 4, 3, pmd);
		fread(joint[i].rot, 4, 3, pmd);
		fread(joint[i].limit, 4, 12, pmd);
		fread(joint[i].spring, 4, 6, pmd);
	}

	fclose(pmd);

	//モデルをキャッシュに保存
	for (i = 0; i<64; i++) {
		if (count[i] == 255) {
			cache_model[i] = *this;
			count[i] = cur_count;
			break;
		}
	}

	return true;
}

bool MODEL::save(const std::string &path)const
{
	if (path.empty()) {
		return false;
	}

	auto pmd = fopen(path.c_str(), "wb");
	if (!pmd) {
		return false;
	}

	const char *magic = "Pmd";
	fwrite(magic, 3, 1, pmd);
	const float version = 1.0f;
	fwrite(&version, 4, 1, pmd);
	fwrite(header.name.c_str(), 20, 1, pmd);
	fwrite(header.comment.c_str(), 256, 1, pmd);

	int vt_count = vt.size();
	fwrite(&vt_count, 4, 1, pmd);
	for (size_t i = 0; i<(vt.size()); i++) {
		fwrite(vt[i].loc, 4, 3, pmd);
		fwrite(vt[i].nor, 4, 3, pmd);
		fwrite(vt[i].uv, 4, 2, pmd);
		fwrite(&vt[i].bone_num0, 2, 1, pmd);
		fwrite(&vt[i].bone_num1, 2, 1, pmd);
		fwrite(&vt[i].bone_weight, 1, 1, pmd);
		fwrite(&vt[i].edge_flag, 1, 1, pmd);
	}

	int vt_index_count = vt_index.size();
	fwrite(&vt_index_count, 4, 1, pmd);
	for (size_t i = 0; i<vt_index.size(); i++) {
		if (vt_index[i] >= vt.size()) {
			return false;
		}
		fwrite(&vt_index[i], 2, 1, pmd);
	}

	int mat_count = mat.size();
	fwrite(&mat_count, 4, 1, pmd);
	for (size_t i = 0; i<mat.size(); i++) {
		fwrite(mat[i].diffuse, 4, 3, pmd);
		fwrite(&mat[i].alpha, 4, 1, pmd);
		fwrite(&mat[i].spec, 4, 1, pmd);
		fwrite(mat[i].spec_col, 4, 3, pmd);
		fwrite(mat[i].mirror_col, 4, 3, pmd);
		fwrite(&mat[i].toon_index, 1, 1, pmd);
		fwrite(&mat[i].edge_flag, 1, 1, pmd);
		fwrite(&mat[i].vt_index_count, 4, 1, pmd);
		fwrite(mat[i].tex.c_str(), 1, 20, pmd);
	}

	unsigned short bone_count = bone.size();
	fwrite(&bone_count, 2, 1, pmd);
	for (size_t i = 0; i<bone.size(); i++) {
		fwrite(bone[i].name.c_str(), 1, 20, pmd);
		fwrite(&bone[i].PBone_index, 2, 1, pmd);
		fwrite(&bone[i].TBone_index, 2, 1, pmd);
		fwrite(&bone[i].type, 1, 1, pmd);
		fwrite(&bone[i].IKBone_index, 2, 1, pmd);
		fwrite(bone[i].loc, 4, 3, pmd);
	}

	unsigned short IK_count = IK_list.size();
	fwrite(&IK_count, 2, 1, pmd);
	for (size_t i = 0; i<IK_list.size(); i++) {
		fwrite(&IK_list[i].IKBone_index, 2, 1, pmd);
		fwrite(&IK_list[i].IKTBone_index, 2, 1, pmd);
		unsigned char IK_chain_len = IK_list[i].IKCBone_index.size();
		fwrite(&IK_chain_len, 1, 1, pmd);
		fwrite(&IK_list[i].iterations, 2, 1, pmd);
		fwrite(&IK_list[i].weight, 4, 1, pmd);
		fwrite(&IK_list[i].IKCBone_index[0], 2, IK_list[i].IKCBone_index.size(), pmd);
	}

	unsigned short skin_count = skin.size();
	fwrite(&skin_count, 2, 1, pmd);
	for (size_t i = 0; i<skin.size(); i++) {
		fwrite(skin[i].name.c_str(), 1, 20, pmd);
		unsigned int skin_vt_count = skin[i].data.size();
		fwrite(&skin_vt_count, 4, 1, pmd);
		fwrite(&skin[i].type, 1, 1, pmd);
		for (size_t j = 0; j<skin[i].data.size(); j++) {
			fwrite(&skin[i].data[j].index, 4, 1, pmd);
			fwrite(skin[i].data[j].loc, 4, 3, pmd);
		}
	}

	unsigned char skin_disp_count = skin_index.size();
	fwrite(&skin_disp_count, 1, 1, pmd);
	fwrite(&skin_index[0], 2, skin_index.size(), pmd);

	unsigned char bone_group_count = bone_group.size();
	fwrite(&bone_group_count, 1, 1, pmd);
	for (size_t i = 0; i<bone_group_count; i++) {
		fwrite(bone_group[i].name.c_str(), 1, 50, pmd);
	}

	int bone_disp_count = bone_disp.size();
	fwrite(&bone_disp_count, 4, 1, pmd);
	for (size_t i = 0; i<bone_disp.size(); i++) {
		fwrite(&bone_disp[i].index, 2, 1, pmd);
		fwrite(&bone_disp[i].bone_group, 1, 1, pmd);
	}

	//extension
	fwrite(&eng_support, 1, 1, pmd);

	if (eng_support == 1) {
		fwrite(header.name_eng.c_str(), 1, 20, pmd);
		fwrite(header.comment_eng.c_str(), 1, 256, pmd);
		for (size_t i = 0; i<bone.size(); i++) {
			fwrite(bone[i].name_eng.c_str(), 1, 20, pmd);
		}
		for (size_t i = 1; i<skin.size(); i++) {
			fwrite(skin[i].name_eng.c_str(), 1, 20, pmd);
		}
		for (size_t i = 0; i<bone_group.size(); i++) {
			fwrite(bone_group[i].name_eng.c_str(), 1, 50, pmd);
		}
	}

	for (size_t i = 0; i<10; i++) {
		fwrite(toon[i].c_str(), 1, 100, pmd);
	}

	int rbody_count = rbody.size();
	fwrite(&rbody_count, 4, 1, pmd);
	for (size_t i = 0; i<rbody.size(); i++) {
		fwrite(rbody[i].name.c_str(), 1, 20, pmd);
		fwrite(&rbody[i].bone, 2, 1, pmd);
		fwrite(&rbody[i].group, 1, 1, pmd);
		fwrite(&rbody[i].target, 2, 1, pmd);
		fwrite(&rbody[i].shape, 1, 1, pmd);
		fwrite(rbody[i].size, 4, 3, pmd);
		fwrite(rbody[i].loc, 4, 3, pmd);
		fwrite(rbody[i].rot, 4, 3, pmd);
		fwrite(rbody[i].property, 4, 5, pmd);
		fwrite(&rbody[i].type, 1, 1, pmd);
	}

	int joint_count = joint.size();
	fwrite(&joint_count, 4, 1, pmd);
	for (size_t i = 0; i<joint.size(); i++) {
		fwrite(joint[i].name.c_str(), 1, 20, pmd);
		fwrite(joint[i].rbody, 4, 2, pmd);
		fwrite(joint[i].loc, 4, 3, pmd);
		fwrite(joint[i].rot, 4, 3, pmd);
		fwrite(joint[i].limit, 4, 12, pmd);
		fwrite(joint[i].spring, 4, 6, pmd);
	}

	fclose(pmd);

	return true;
}
