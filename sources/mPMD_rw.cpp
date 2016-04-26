#include "mPMD_rw.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <memory.h>
#include <string.h>
#include "mPMD.h"
#include "debug_io.h"


int load_PMD(MODEL *model, const char file_name[])
{
	int i, j, tmp;
	char *char_p, str[PATH_LEN];
	FILE *pmd;
	
	static MODEL cache_model[64];
	static unsigned char count[64];
	static unsigned char cur_count=255;
	
	//int *check;
	
	//check = MALLOC((size_t)1000*sizeof(int));
	
	//memset(check, 0, (size_t)1000*sizeof(int));
	
	//dbg_0check(check,1000);
	
	//�L���b�V���܂�菉����
	if(cur_count == 255){
		for(i=0; i<64; i++){
			count[i] = 255;
			cache_model[i] = MODEL();
		}
		cur_count = 0;
	}
	
	if(strcmp(file_name, "") == 0){
		printf("�t�@�C����������܂���\n");
		return 1;
	}
	
	if(cur_count > 64){
		cur_count=0;
	}else{
		cur_count++;
	}
	
	for(i=0; i<64; i++){
		if(count[i]!=255){
			//printf("%s, %s\n", cache_model[i].header.path, file_name);
			if(cache_model[i].header.path==file_name){
				*model=cache_model[i];
				count[i] = cur_count;
				break;
			}
		}
	}
	
	tmp = cur_count+1;
	if(tmp >= 64)tmp = 0;
	for(j=0; j<64; j++){
		if(count[i] == tmp){
			count[i] = 255;
			cache_model[i]=MODEL();
		}
	}
	if(i != 64){
		printf("Use Cache\n");
		return 0;
	}
	
	pmd = fopen(file_name,"rb");
	if(pmd == NULL  ){
		return 1;
	}
	
	model->header.path = file_name;
	
	char magic[4];
	FREAD(magic, 1, 3, pmd);
	float version;
	FREAD(&version, 4, 1, pmd);
	if(memcmp(magic, "Pmd", 3) != 0 || version != 1.0){
		printf("Format error\n");
		return -1;
	}
	
	model->header.name.fread<20>(pmd);
	model->header.comment.fread<256>(pmd);
	
	int vt_count;
	FREAD(&vt_count, 4,  1, pmd);
	model->vt.resize(vt_count);
	for(i=0; i<(model->vt.size()); i++){
		//fseek(pmd, 38, SEEK_CUR);
		FREAD(model->vt[i].loc, 4, 3, pmd);
		FREAD(model->vt[i].nor, 4, 3, pmd);
		FREAD(model->vt[i].uv, 4, 2, pmd);
		FREAD(&model->vt[i].bone_num0, 2, 1, pmd);
		FREAD(&model->vt[i].bone_num1, 2, 1, pmd);
		FREAD(&model->vt[i].bone_weight, 1, 1, pmd);
		FREAD(&model->vt[i].edge_flag, 1, 1, pmd);
	}
	
	int vt_index_count;
	FREAD(&vt_index_count, 4,  1, pmd);
	model->vt_index.resize(vt_index_count);
	for(i=0; i<model->vt_index.size(); i++){
		FREAD(&model->vt_index[i], 2, 1, pmd);
		if(model->vt_index[i] >= model->vt.size()){
			printf("���_�C���f�b�N�X���s���ł�\n");
			return 1;
		}
	}
	
	int mat_count;
	FREAD(&mat_count, 4,  1, pmd);
	model->mat.resize(mat_count);
	for(i=0; i<model->mat.size(); i++){
		FREAD(model->mat[i].diffuse, 4, 3, pmd);
		FREAD(&model->mat[i].alpha, 4, 1, pmd);
		FREAD(&model->mat[i].spec, 4, 1, pmd);
		FREAD(&model->mat[i].spec_col, 4, 3, pmd);
		FREAD(&model->mat[i].mirror_col, 4, 3, pmd);
		FREAD(&model->mat[i].toon_index, 1, 1, pmd);
		FREAD(&model->mat[i].edge_flag, 1, 1, pmd);
		FREAD(&model->mat[i].vt_index_count, 4, 1, pmd);
		model->mat[i].tex.fread<20>(pmd);
		
		strcpy(str, file_name);
		char_p = strrchr(str, '/');
		if(char_p!=NULL){
			char_p++;
			*char_p = '\0';
		}else{
			*str = '\0';
		}
		/*
		char_p = strchr(model->mat[i].tex, '*');
		if(char_p != NULL){
			*char_p='\0';
			++char_p;
			strcpy(model->mat[i].sph, char_p);
			sprintf(model->mat[i].sph_path,"%s%s\0", str, model->mat[i].sph);
		}
		else{
			*model->mat[i].sph='\0';
		}
		sprintf(model->mat[i].tex_path,"%s%s\0", str, model->mat[i].tex);
		*/
	}
	
	unsigned short bone_count;
	FREAD(&bone_count, 2,  1, pmd);
	model->bone.resize(bone_count);
	for(i=0; i<model->bone.size(); i++){
		model->bone[i].name.fread<20>(pmd);
		FREAD(&model->bone[i].PBone_index, 2, 1, pmd);
		FREAD(&model->bone[i].TBone_index, 2, 1, pmd);
		FREAD(&model->bone[i].type, 1, 1, pmd);
		FREAD(&model->bone[i].IKBone_index, 2, 1, pmd);
		FREAD(model->bone[i].loc, 4, 3, pmd);
	}
	
	unsigned short IK_count;
	FREAD(&IK_count, 2,  1, pmd);

	model->IK_list.resize(IK_count);
	for(i=0; i<model->IK_list.size(); i++){
		FREAD(&model->IK_list[i].IKBone_index, 2, 1, pmd);
		FREAD(&model->IK_list[i].IKTBone_index, 2, 1, pmd);
		unsigned char IK_chain_len;
		FREAD(&IK_chain_len, 1, 1, pmd);
		FREAD(&model->IK_list[i].iterations, 2, 1, pmd);
		FREAD(&model->IK_list[i].weight, 4, 1, pmd);
		model->IK_list[i].IKCBone_index.resize(IK_chain_len);
		if(IK_chain_len > 0){
			FREAD(&model->IK_list[i].IKCBone_index[0], 2, IK_chain_len, pmd);
		}
	}
	
	unsigned short skin_count;
	FREAD(&skin_count, 2,  1, pmd);
	model->skin.resize(skin_count);
	for(i=0; i<model->skin.size(); i++){
		model->skin[i].name.fread<20>(pmd);
		unsigned int skin_vt_count;
		FREAD(&skin_vt_count, 4, 1, pmd);
		FREAD(&model->skin[i].type, 1, 1, pmd);
		model->skin[i].data.resize(skin_vt_count);
		for(j=0; j<model->skin[i].data.size(); j++){
			FREAD(&model->skin[i].data[j].index, 4, 1, pmd);
			if(model->skin[i].data[j].index > model->vt.size()){
				exit(1);
			}
			FREAD(&model->skin[i].data[j].loc, 4, 3, pmd);
		}
	}
	
	unsigned char skin_disp_count;
	FREAD(&skin_disp_count, 1,  1, pmd);
	model->skin_index.resize(skin_disp_count);
	if (skin_disp_count) {
		FREAD(&model->skin_index[0], 2, model->skin_index.size(), pmd);
	}
	
	unsigned char bone_group_count;
	FREAD(&bone_group_count, 1,  1, pmd);
	model->bone_group.resize(bone_group_count);
	for(i=0; i<bone_group_count; i++){
		model->bone_group[i].name.fread<50>(pmd);
	}

	int bone_disp_count;
	FREAD(&bone_disp_count, 4,  1, pmd);
	model->bone_disp.resize(bone_disp_count);
	for(i=0; i<bone_disp_count; i++){
		FREAD(&model->bone_disp[i].index, 2,  1, pmd);
		FREAD(&model->bone_disp[i].bone_group, 1,  1, pmd);
	}
	
	FREAD(&model->eng_support, 1,  1, pmd);
	
	if(feof(pmd)!=0){
		model->eng_support = 0;
		for(i=0; i<10; i++){
			j=i+1;
			sprintf(model->toon[i].data(), "toon%02d.bmp\0", j);
		}
		model->rbody.clear();
		model->joint.clear();
		return 0;
	}
	
	#ifdef DEBUG
		printf("�p���Ή�:%d\n", model->eng_support);
	#endif
	
	if(model->eng_support == 1){
		model->header.name_eng.fread<20>(pmd);
		model->header.comment_eng.fread<256>(pmd);
		
		for(i=0; i<model->bone.size(); i++){
			model->bone[i].name_eng.fread<20>(pmd);
		}
		
		if(model->skin.size() > 0){
			model->skin[0].name_eng="base";
		}
		for(i=1; i<model->skin.size(); i++){
			model->skin[i].name_eng.fread<20>(pmd);
		}
		for(i=0; i<model->bone_group.size(); i++){
			model->bone_group[i].name_eng.fread<50>(pmd);
		}
	}
	
	for(i=0; i<10; i++){
		model->toon[i].fread<100>(pmd);
	}

	int rbody_count;
	FREAD(&rbody_count, 4,  1, pmd);
	model->rbody.resize(rbody_count);	
	for(i=0; i<model->rbody.size(); i++){
		model->rbody[i].name.fread<20>(pmd);
		FREAD(&model->rbody[i].bone, 2,  1, pmd);
		FREAD(&model->rbody[i].group, 1,  1, pmd);
		FREAD(&model->rbody[i].target, 2,  1, pmd);
		FREAD(&model->rbody[i].shape, 1,  1, pmd);
		FREAD(model->rbody[i].size, 4,  3, pmd);
		FREAD(model->rbody[i].loc, 4,  3, pmd);
		FREAD(model->rbody[i].rot, 4,  3, pmd);
		FREAD(model->rbody[i].property, 4,  5, pmd);
		FREAD(&model->rbody[i].type, 1,  1, pmd);
	}

	int joint_count;
	FREAD(&joint_count, 4,  1, pmd);
	model->joint.resize(joint_count);
	for(i=0; i<joint_count; i++){
		model->joint[i].name.fread<20>(pmd);
		FREAD(model->joint[i].rbody, 4,  2, pmd);
		FREAD(model->joint[i].loc, 4,  3, pmd);
		FREAD(model->joint[i].rot, 4,  3, pmd);
		FREAD(model->joint[i].limit, 4,  12, pmd);
		FREAD(model->joint[i].spring, 4,  6, pmd);
	}
	
	fclose(pmd);
	
	//���f�����L���b�V���ɕۑ�
	for(i=0; i<64; i++){
		if(count[i]==255){
			cache_model[i]=*model;
			count[i] = cur_count;
			break;
		}
	}
	
	return 0;
}


int write_PMD(MODEL *model, const char file_name[])
{
	int i, j, ret=0;
	char str[PATH_LEN];
	
	FILE *pmd;
	
	if(strcmp(file_name, "") == 0){
		printf("�t�@�C����������܂���\n");
		return 1;
	}
	
	pmd = fopen(file_name,"wb");
	if(pmd == NULL  ){
		printf("�t�@�C�� %s ���J���܂���\n", file_name);
		return 1;
	}
	
	/*�[������*/
	/*{
		int total_bytes;
		char b = '\0';
		total_bytes = 283+4+38*model->vt_count
						+4+2*model->vt_index_count
						+4*70*model->mat_count;
		for(i=0; i<total_bytes; i++){
			fwrite(&b,1,1,pmd);
		}
		fseek(pmd, 0, SEEK_SET);
	}*/
	
	//�w�b�_�[��������
	
	const char *magic = "Pmd";
	fwrite(magic, 3, 1,pmd);
	const float version = 1.0f;
	fwrite(&version, 4, 1, pmd);
	fwrite(model->header.name.c_str(), 20, 1, pmd);
	fwrite(model->header.comment.c_str(), 256, 1, pmd);
	
	int vt_count = model->vt.size();
	fwrite(&vt_count, 4,  1, pmd);	
	for(i=0; i<(model->vt.size()); i++){
		//fseek(pmd, 38, SEEK_CUR);
		fwrite(model->vt[i].loc, 4, 3, pmd);
		fwrite(model->vt[i].nor, 4, 3, pmd);
		fwrite(model->vt[i].uv, 4, 2, pmd);
		fwrite(&model->vt[i].bone_num0, 2, 1, pmd);
		fwrite(&model->vt[i].bone_num1, 2, 1, pmd);
		fwrite(&model->vt[i].bone_weight, 1, 1, pmd);
		fwrite(&model->vt[i].edge_flag, 1, 1, pmd);
	}
		
	int vt_index_count = model->vt_index.size();
	fwrite(&vt_index_count, 4,  1, pmd);
	for(i=0; i<model->vt_index.size(); i++){
		if(model->vt_index[i] >= model->vt.size()){
			printf("���_�C���f�b�N�X���s���ł� :%d\n", model->vt_index[i]);
			return 1;
		}
		fwrite(&model->vt_index[i], 2, 1, pmd);
	}
	
	int mat_count = model->mat.size();
	fwrite(&mat_count, 4,  1, pmd);	
	for(i=0; i<model->mat.size(); i++){
		//70bytes
		fwrite(model->mat[i].diffuse, 4, 3, pmd);
		fwrite(&model->mat[i].alpha, 4, 1, pmd);
		fwrite(&model->mat[i].spec, 4, 1, pmd);
		fwrite(model->mat[i].spec_col, 4, 3, pmd);
		fwrite(model->mat[i].mirror_col, 4, 3, pmd);
		fwrite(&model->mat[i].toon_index, 1, 1, pmd);
		fwrite(&model->mat[i].edge_flag, 1, 1, pmd);
		fwrite(&model->mat[i].vt_index_count, 4, 1, pmd);
		/*
		if(*model->mat[i].sph != '\0'){
			sprintf(str, "%s*%s\0", model->mat[i].tex, model->mat[i].sph);
			if(strlen(str) > 20){
				ret = 2;
			}
			fwrite(str, 1, 20, pmd);
		}
		else*/
		{
			fwrite(model->mat[i].tex.c_str(), 1, 20, pmd);
		}
	}
	
	unsigned short bone_count = model->bone.size();
	fwrite(&bone_count, 2,  1, pmd);
	for(i=0; i<model->bone.size(); i++){
		fwrite(model->bone[i].name.c_str(), 1, 20, pmd);
		fwrite(&model->bone[i].PBone_index, 2, 1, pmd);
		fwrite(&model->bone[i].TBone_index, 2, 1, pmd);
		fwrite(&model->bone[i].type, 1, 1, pmd);
		fwrite(&model->bone[i].IKBone_index, 2, 1, pmd);
		fwrite(model->bone[i].loc, 4, 3, pmd);
	}
	
	unsigned short IK_count = model->IK_list.size();
	fwrite(&IK_count, 2,  1, pmd);
	for(i=0; i<model->IK_list.size(); i++){
		fwrite(&model->IK_list[i].IKBone_index, 2, 1, pmd);
		fwrite(&model->IK_list[i].IKTBone_index, 2, 1, pmd);
		unsigned char IK_chain_len = model->IK_list[i].IKCBone_index.size();
		fwrite(&IK_chain_len, 1, 1, pmd);
		fwrite(&model->IK_list[i].iterations, 2, 1, pmd);
		fwrite(&model->IK_list[i].weight, 4, 1, pmd);
		fwrite(&model->IK_list[i].IKCBone_index[0], 2, model->IK_list[i].IKCBone_index.size(), pmd);
	}
	
	unsigned short skin_count = model->skin.size();
	fwrite(&skin_count, 2,  1, pmd);	
	for(i=0; i<model->skin.size(); i++){
		fwrite(model->skin[i].name.c_str(), 1, 20, pmd);
		unsigned int skin_vt_count=model->skin[i].data.size();
		fwrite(&skin_vt_count, 4, 1, pmd);
		fwrite(&model->skin[i].type, 1, 1, pmd);
		for(j=0; j<model->skin[i].data.size(); j++){
			fwrite(&model->skin[i].data[j].index, 4, 1, pmd);
			fwrite(model->skin[i].data[j].loc, 4, 3, pmd);
		}
	}
	
	unsigned char skin_disp_count = model->skin_index.size();
	fwrite(&skin_disp_count, 1,  1, pmd);
	fwrite(&model->skin_index[0], 2, model->skin_index.size(), pmd);
	
	unsigned char bone_group_count = model->bone_group.size();
	fwrite(&bone_group_count, 1,  1, pmd);
	for(i=0; i<bone_group_count; i++){
		fwrite(model->bone_group[i].name.c_str(), 1, 50, pmd);
	}
	
	int bone_disp_count = model->bone_disp.size();
	fwrite(&bone_disp_count, 4,  1, pmd);
	for(i=0; i<model->bone_disp.size(); i++){
		fwrite(&model->bone_disp[i].index, 2,  1, pmd);
		fwrite(&model->bone_disp[i].bone_group, 1,  1, pmd);
	}
	
	//extension
	fwrite(&model->eng_support, 1,  1, pmd);
	
	if(model->eng_support==1){
		fwrite(model->header.name_eng.c_str(), 1,  20, pmd);
		fwrite(model->header.comment_eng.c_str(), 1,  256, pmd);
		for(i=0; i<model->bone.size(); i++){
			fwrite(model->bone[i].name_eng.c_str(), 1,  20, pmd);
		}
		for(i=1; i<model->skin.size(); i++){
			fwrite(model->skin[i].name_eng.c_str(), 1,  20, pmd);
		}
		for(i=0; i<model->bone_group.size(); i++){
			fwrite(model->bone_group[i].name_eng.c_str(), 1,  50, pmd);
		}
	}
	#ifdef DEBUG
		printf("�p��\n");
	#endif
	
	for(i=0; i<10; i++){
		fwrite(model->toon[i].c_str(), 1, 100, pmd);
	}
	
	int rbody_count = model->rbody.size();
	fwrite(&rbody_count, 4,  1, pmd);
	for(i=0; i<model->rbody.size(); i++){
		fwrite(model->rbody[i].name.c_str(), 1,  20, pmd);
		fwrite(&model->rbody[i].bone, 2,  1, pmd);
		fwrite(&model->rbody[i].group, 1,  1, pmd);
		fwrite(&model->rbody[i].target, 2,  1, pmd);
		fwrite(&model->rbody[i].shape, 1,  1, pmd);
		fwrite(model->rbody[i].size, 4,  3, pmd);
		fwrite(model->rbody[i].loc, 4,  3, pmd);
		fwrite(model->rbody[i].rot, 4,  3, pmd);
		fwrite(model->rbody[i].property, 4,  5, pmd);
		fwrite(&model->rbody[i].type, 1,  1, pmd);
	}
	
	int joint_count = model->joint.size();
	fwrite(&joint_count, 4,  1, pmd);	
	for(i=0; i<model->joint.size(); i++){
		fwrite(model->joint[i].name.c_str(), 1,  20, pmd);
		fwrite(model->joint[i].rbody, 4,  2, pmd);
		fwrite(model->joint[i].loc, 4,  3, pmd);
		fwrite(model->joint[i].rot, 4,  3, pmd);
		fwrite(model->joint[i].limit, 4,  12, pmd);
		fwrite(model->joint[i].spring, 4,  6, pmd);
	}
	
	fclose(pmd);
	printf("%s�֏o�͂��܂����B\n",file_name);
	
	return ret;
}

int create_PMD(MODEL *model)
{
	model->header.name.clear();
	model->header.comment.clear();
	
	model->vt.clear();	
	model->vt_index.clear();	
	model->mat.clear();
	model->bone.clear();
	model->IK_list.clear();
	model->skin.clear();
	model->skin_index.clear();
	model->bone_group.clear();
	model->bone_disp.clear();
	
	model->eng_support = 0;
	
	for(int i=0; i<10; i++){
		sprintf(model->toon[i].data(), "toon%02d.bmp\0", i+1);
	}
	
	model->rbody.clear();
	model->joint.clear();
	
	return 0;
}

int delete_PMD(MODEL *model)
{
	model->header.name.clear();
	model->header.comment.clear();
	
	model->vt.clear();	
	model->vt_index.clear();	
	model->mat.clear();
	model->bone.clear();	
	model->IK_list.clear();
	model->skin.clear();
	model->skin_index.clear();
	model->bone_group.clear();
	model->bone_disp.clear();
	
	model->eng_support = 0;
	
	for(int i=0; i<10; i++){
		sprintf(model->toon[i].data(), "toon%02d.bmp\0", i+1);
	}
	
	model->rbody.clear();
	model->joint.clear();
	
	return 0;
}

int copy_PMD(MODEL *out, MODEL *model)
{
	out->header =model->header;
	out->vt = model->vt;
	out->vt_index = model->vt_index;
	out->mat = model->mat;
	out->bone = model->bone;
	out->IK_list = model->IK_list;
	out->skin = model->skin;
	out->skin_index = model->skin_index;
	out->bone_group = model->bone_group;
	out->bone_disp = model->bone_disp;
	out->toon=model->toon;	
	out->eng_support = model->eng_support;	
	out->rbody = model->rbody;
	out->joint = model->joint;
	
	return 0;
}

int add_PMD(MODEL *model, MODEL *add)
{
	//���_
	std::vector<VERTEX> vt(model->vt.size() + add->vt.size());
	for(size_t i=0; i<model->vt.size(); i++){
		vt[i] = model->vt[i];
	}
	size_t j = 0;	
	for(size_t i=model->vt.size(); i<vt.size(); i++){
		vt[i] = add->vt[j];
		vt[i].bone_num0 += model->bone.size();
		vt[i].bone_num1 += model->bone.size();
		j++;
	}
		
	//�ʒ��_
	std::vector<unsigned short> vt_index(model->vt_index.size() + add->vt_index.size());
	for(size_t i=0; i<model->vt_index.size(); i++){
		vt_index[i] = model->vt_index[i];
	}
	j = 0;
	for(size_t i=model->vt_index.size(); i<vt_index.size(); i++){
		vt_index[i] = add->vt_index[j] + model->vt.size();
		j++;
	}
		
	//�ގ�
	std::vector<MATERIAL> mat(model->mat.size() + add->mat.size());
	for(size_t i=0; i<model->mat.size(); i++){
		mat[i] = model->mat[i];
	}
	j = 0;	
	for(size_t i=model->mat.size(); i<mat.size(); i++){
		mat[i] = add->mat[j];
		j++;
	}
		
	//�{�[��
	std::vector<BONE> bone(model->bone.size() + add->bone.size());
	for(size_t i=0; i<model->bone.size(); i++){
		bone[i] = model->bone[i];
	}
	j=0;
	for(size_t i=model->bone.size(); i<bone.size(); i++){
		bone[i] = add->bone[j];
		if(bone[i].PBone_index != USHORT_MAX)
		bone[i].PBone_index = bone[i].PBone_index + model->bone.size();
		if(bone[i].TBone_index != 0)
		bone[i].TBone_index = bone[i].TBone_index + model->bone.size();
		if(bone[i].IKBone_index != 0)
		bone[i].IKBone_index = bone[i].IKBone_index + model->bone.size();
		j++;
	}

	//IK���X�g
	std::vector<IK_LIST> IK_list(model->IK_list.size() + add->IK_list.size());
	for(size_t i=0; i<model->IK_list.size(); i++){
		IK_list[i] = model->IK_list[i];
	}
	j = 0;
	for(size_t i=model->IK_list.size(); i<IK_list.size(); i++){
		IK_list[i] = add->IK_list[j];
		IK_list[i].IKBone_index = IK_list[i].IKBone_index + model->bone.size();
		IK_list[i].IKTBone_index = IK_list[i].IKTBone_index + model->bone.size();
		for(size_t k=0; k<IK_list[i].IKCBone_index.size(); k++){
			IK_list[i].IKCBone_index[k] = IK_list[i].IKCBone_index[k] + model->bone.size();
		}
		j++;
	}
	
	//�\��
	std::vector<SKIN> skin(model->skin.size() + add->skin.size());	
	if(add->skin.size() == 0){
		skin = model->skin;
	}
	else if(model->skin.size() == 0){
		skin = add->skin;
	}
	else if(model->skin.size() != 0 && add->skin.size() != 0){
		skin.resize(skin.size()-1);
		skin[0] = model->skin[0];
		skin[0].data.resize(model->skin[0].data.size() + add->skin[0].data.size());
		auto x = model->skin[0].data.size();
		memcpy(&skin[0].data[0], &model->skin[0].data[0], x * sizeof(SKIN_DATA));
		memcpy(&skin[0].data[x], &add->skin[0].data[0], add->skin[0].data.size() * sizeof(SKIN_DATA));
		//base�̍���
		
		for(size_t i=0; i < model->skin[0].data.size(); i++){
			skin[0].data[i].index = model->skin[0].data[i].index;
		}
		//printf("%d %d %d\n", skin[0].skin_vt_count, model->skin[0].skin_vt_count, add->skin[0].skin_vt_count);
		j = 0;
		for(size_t i = model->skin[0].data.size(); i < skin[0].data.size(); i++){
			//printf("%d \n", i);
			skin[0].data[i].index = add->skin[0].data[j].index + model->vt.size();
			j++;
		}
		//�\��ǉ�
		for(size_t i=1; i<model->skin.size(); i++){
			skin[i] = model->skin[i];
		}
		j = 1;
		for(size_t i=model->skin.size(); i<skin.size(); i++){
			//printf("%d\n", j);
			skin[i] = add->skin[j];
			for(size_t k=0; k < skin[i].data.size(); k++){
				skin[i].data[k].index = skin[i].data[k].index + model->skin[0].data.size();
			}
			j++;
		}
	}
	
	//�\��\��
	std::vector<unsigned short> skin_index(model->skin_index.size() + add->skin_index.size());
	if (!skin_index.empty() && !model->skin_index.empty()) {
		memcpy(&skin_index[0], &model->skin_index[0], model->skin_index.size() * sizeof(unsigned short));
	}
	j = 0;
	for(size_t i=model->skin_index.size(); i<skin_index.size(); i++){
		skin_index[i] = add->skin_index[j] + model->skin_index.size();
		j++;
	}
	
	//�{�[���\��
	std::vector<BONE_GROUP> bone_group(model->bone_group.size() + add->bone_group.size());
	for(size_t i=0; i<model->bone_group.size(); i++){
		bone_group[i] = model->bone_group[i];
	}
	j = 0;
	for(size_t i=model->bone_group.size(); i<bone_group.size(); i++){
		bone_group[i] = add->bone_group[j];
		j++;
	}
	
	std::vector<BONE_DISP> bone_disp(model->bone_disp.size() + add->bone_disp.size());
	for(size_t i=0; i<model->bone_disp.size(); i++){
		bone_disp[i] = model->bone_disp[i];
	}
	j = 0;
	for(size_t i=model->bone_disp.size(); i<bone_disp.size(); i++){
		bone_disp[i].index = add->bone_disp[j].index + model->bone.size();
		bone_disp[i].bone_group = add->bone_disp[j].bone_group + model->bone_group.size();
		j++;
		//printf("%d %d %d %d\n", add->bone_disp[j].index, add->bone_disp[j].bone_group, bone_disp[i].index, bone_disp[i].bone_group);
	}
		
	//�p��
	model->eng_support = add->eng_support;
		
	//����
	std::vector<RIGID_BODY> rbody(model->rbody.size() + add->rbody.size());
	for(size_t i=0; i<model->rbody.size(); i++){
		rbody[i] = model->rbody[i];
	}
	j=0;
	for(size_t i=model->rbody.size(); i<rbody.size(); i++){
		rbody[i] = add->rbody[j];
		rbody[i].bone = rbody[i].bone + model->bone.size();
		j++;
	}

	//�W���C���g
	std::vector<JOINT> joint(model->joint.size() + add->joint.size());
	for(size_t i=0; i<model->joint.size(); i++){
		joint[i] = model->joint[i];
	}
	j=0;
	for(size_t i=model->joint.size(); i<joint.size(); i++){
		joint[i] = add->joint[j];
		for(size_t k=0; k<2; k++){
			joint[i].rbody[k] = joint[i].rbody[k] + model->rbody.size();
		}
		j++;
	}
		
	model->header = add->header;
	model->vt = vt;	
	model->vt_index = vt_index;	
	model->mat = mat;
	model->bone = bone;
	model->IK_list = IK_list;
	model->skin = skin;
	model->skin_index = skin_index;
	model->bone_group = bone_group;
	model->bone_disp = bone_disp;
	model->rbody = rbody;
	model->joint = joint;
	
	return 0;
}

int listup_bone(MODEL *model, const char file_name[]){
	int i;
	char str[64], *p;
	
	FILE *txt;
	
	if(strcmp(file_name, "") == 0){
		printf("�t�@�C����������܂���\n");
		return 1;
	}
	txt = fopen(file_name,"w");
	if(txt == NULL  ){
		fprintf(txt, "�o�̓e�L�X�g�t�@�C�����J���܂���\n");
		return 1;
	}
	
	if(model->eng_support == 0){
		printf("���X�g�o�͂��ł���͉̂p���Ή����f���݂̂ł�\n");
		return 1;
	}
	
	fprintf(txt, "%s \n %s \n",
		model->header.name,
		model->header.comment);
	
	fprintf(txt, "�{�[����:%d\n", model->bone.size());
	
	for(i=0; i<model->bone.size(); i++){
		fprintf(txt, "%s %s\n", model->bone[i].name, model->bone[i].name_eng);
	}
	
	fprintf(txt, "�\�:%d\n", model->skin.size());
	for(i=0; i<model->skin.size(); i++){
		fprintf(txt, "%s %s\n", model->skin[i].name, model->skin[i].name_eng);
	}
	fprintf(txt, "�{�[���g��:%d\n", model->bone_group.size());
	for(i=0; i<model->bone_group.size(); i++){
		fprintf(txt, "%s %s\n", model->bone_group[i].name.c_str(), model->bone_group[i].name_eng);
	}
	
	fclose(txt);
	
	return 0;
}


int get_file_name(char file_name[])
{
	int i;
	char input[256];
	printf("�t�@�C����:");
	fgets(input, 256, stdin);
	if(input[0] == '\"'){
		for(i=1; i<256; i++){
			file_name[i-1] = input[i];
			if(input[i] == '\"'){
				file_name[i-1] = '\0';
				input[i] = '\0';
				break;
			}else if(input[i] == '\0'){
				break;
			}
		}
	}else{
		strcpy(file_name, input);
	}
	
	return 0;
}
