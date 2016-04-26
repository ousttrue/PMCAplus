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
	//頂点
	std::vector<VERTEX> vt(model->vt.size() + add->vt.size());
	for(size_t i=0; i<model->vt.size(); i++){
		vt[i] = model->vt[i];
	}
	size_t j = 0;
	auto bone_offset = (unsigned short)model->bone.size();
	for(size_t i=model->vt.size(); i<vt.size(); i++){
		vt[i] = add->vt[j];
		vt[i].bone_num0 += bone_offset;
		vt[i].bone_num1 += bone_offset;
		j++;
	}
		
	//面頂点
	std::vector<unsigned short> vt_index(model->vt_index.size() + add->vt_index.size());
	for(size_t i=0; i<model->vt_index.size(); i++){
		vt_index[i] = model->vt_index[i];
	}
	j = 0;
	auto vertex_offset = (unsigned short)model->vt.size();
	for(size_t i=model->vt_index.size(); i<vt_index.size(); i++){
		vt_index[i] = add->vt_index[j] + vertex_offset;
		j++;
	}
		
	//材質
	std::vector<MATERIAL> mat(model->mat.size() + add->mat.size());
	for(size_t i=0; i<model->mat.size(); i++){
		mat[i] = model->mat[i];
	}
	j = 0;	
	for(size_t i=model->mat.size(); i<mat.size(); i++){
		mat[i] = add->mat[j];
		j++;
	}
		
	//ボーン
	std::vector<BONE> bone(model->bone.size() + add->bone.size());
	for(size_t i=0; i<model->bone.size(); i++){
		bone[i] = model->bone[i];
	}
	j=0;
	for(size_t i=model->bone.size(); i<bone.size(); i++){
		bone[i] = add->bone[j];
		if(bone[i].PBone_index != USHORT_MAX)
		bone[i].PBone_index = bone[i].PBone_index + bone_offset;
		if(bone[i].TBone_index != 0)
		bone[i].TBone_index = bone[i].TBone_index + bone_offset;
		if(bone[i].IKBone_index != 0)
		bone[i].IKBone_index = bone[i].IKBone_index + bone_offset;
		j++;
	}

	//IKリスト
	std::vector<IK_LIST> IK_list(model->IK_list.size() + add->IK_list.size());
	for(size_t i=0; i<model->IK_list.size(); i++){
		IK_list[i] = model->IK_list[i];
	}
	j = 0;
	for(size_t i=model->IK_list.size(); i<IK_list.size(); i++){
		IK_list[i] = add->IK_list[j];
		IK_list[i].IKBone_index = IK_list[i].IKBone_index + bone_offset;
		IK_list[i].IKTBone_index = IK_list[i].IKTBone_index + bone_offset;
		for(size_t k=0; k<IK_list[i].IKCBone_index.size(); k++){
			IK_list[i].IKCBone_index[k] = IK_list[i].IKCBone_index[k] + bone_offset;
		}
		j++;
	}
	
	//表情
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
		//baseの合成
		
		for(size_t i=0; i < model->skin[0].data.size(); i++){
			skin[0].data[i].index = model->skin[0].data[i].index;
		}
		//printf("%d %d %d\n", skin[0].skin_vt_count, model->skin[0].skin_vt_count, add->skin[0].skin_vt_count);
		j = 0;
		for(size_t i = model->skin[0].data.size(); i < skin[0].data.size(); i++){
			//printf("%d \n", i);
			skin[0].data[i].index = add->skin[0].data[j].index + vertex_offset;
			j++;
		}
		//表情追加
		for(size_t i=1; i<model->skin.size(); i++){
			skin[i] = model->skin[i];
		}
		j = 1;
		for(size_t i=model->skin.size(); i<skin.size(); i++){
			//printf("%d\n", j);
			skin[i] = add->skin[j];
			for(size_t k=0; k < skin[i].data.size(); k++){
				skin[i].data[k].index = skin[i].data[k].index + (unsigned int)model->skin[0].data.size();
			}
			j++;
		}
	}
	
	//表情表示
	std::vector<unsigned short> skin_index(model->skin_index.size() + add->skin_index.size());
	if (!skin_index.empty() && !model->skin_index.empty()) {
		memcpy(&skin_index[0], &model->skin_index[0], model->skin_index.size() * sizeof(unsigned short));
	}
	j = 0;
	for(size_t i=model->skin_index.size(); i<skin_index.size(); i++){
		skin_index[i] = add->skin_index[j] + (unsigned short)model->skin_index.size();
		j++;
	}
	
	//ボーン表示
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
		bone_disp[i].index = add->bone_disp[j].index + bone_offset;
		bone_disp[i].bone_group = add->bone_disp[j].bone_group + (unsigned char)model->bone_group.size();
		j++;
		//printf("%d %d %d %d\n", add->bone_disp[j].index, add->bone_disp[j].bone_group, bone_disp[i].index, bone_disp[i].bone_group);
	}
		
	//英名
	model->eng_support = add->eng_support;
		
	//剛体
	std::vector<RIGID_BODY> rbody(model->rbody.size() + add->rbody.size());
	for(size_t i=0; i<model->rbody.size(); i++){
		rbody[i] = model->rbody[i];
	}
	j=0;
	for(size_t i=model->rbody.size(); i<rbody.size(); i++){
		rbody[i] = add->rbody[j];
		rbody[i].bone = rbody[i].bone + bone_offset;
		j++;
	}

	//ジョイント
	std::vector<JOINT> joint(model->joint.size() + add->joint.size());
	for(size_t i=0; i<model->joint.size(); i++){
		joint[i] = model->joint[i];
	}
	j=0;
	for(size_t i=model->joint.size(); i<joint.size(); i++){
		joint[i] = add->joint[j];
		for(size_t k=0; k<2; k++){
			joint[i].rbody[k] = joint[i].rbody[k] + (int)model->rbody.size();
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

int get_file_name(char file_name[])
{
	int i;
	char input[256];
	printf("ファイル名:");
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
