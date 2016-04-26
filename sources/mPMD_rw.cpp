#include "mPMD_rw.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <memory.h>
#include <string.h>
#include "mPMD.h"
#include "debug_io.h"





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
