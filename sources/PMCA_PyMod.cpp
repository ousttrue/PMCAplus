#include "PMCA_PyMod.h"
#include "mPMD_rw.h"
#include "mPMD_edit.h"
#include "debug_io.h"


#define PMCA_MODULE
#define MODEL_COUNT 16
MODEL g_model[MODEL_COUNT];
LIST list;
static PyObject *PMCAError;

//int* zero;

#ifdef __cplusplus
extern "C" {
#endif

/*データ変換Utils*/
PyObject* Array_to_PyList_UShort(const unsigned short* input, int count)
{
	int i;
	PyObject *l, *x;
	l = PyList_New(0);
	for(i=0; i<count; i++){
		x = PyLong_FromLong((int)input[i]);
		if(x == NULL)break;
		PyList_Append(l, x);
		Py_DECREF(x);
	}
	//Py_INCREF(l);
	return l;
}

PyObject* Array_to_PyList_Float(const float* input, int count)
{
	int i;
	PyObject *l, *x;
	l = PyList_New(0);
	for(i=0; i<count; i++){
		x = PyFloat_FromDouble(input[i]);
		if(x == NULL)break;
		PyList_Append(l, x);
		Py_DECREF(x);
	}
	//Py_INCREF(l);
	return l;
}

int PyList_to_Array_Float(float* output, PyObject* List, int size)
{
	int i;
	PyObject* tmp;
	
	
	for(i=0; i<size; i++){
		tmp = PyList_GetItem(List, i);
		output[i] = PyFloat_AsDouble(tmp);
	}
	return 0;
}

int PyList_to_Array_UShort(unsigned short* output, PyObject* List, int size)
{
	int i;
	PyObject* tmp;
	if(size > PyList_Size(List))return -1;
	for(i=0; i<size; i++){
		tmp = PyList_GetItem(List, i);
		if(tmp==NULL)return -1;
		output[i] = (unsigned short)PyLong_AsLong(tmp);
		//printf("%d, ", (int)output[i]);
	}
	//printf("\n");
	return 0;
}

int PyList_to_Array_Str(char** output, PyObject* List, int size, int val)
{
	int i;
	Py_ssize_t maxlen;
	char *p;
	
	maxlen = (Py_ssize_t)val - 1;
	PyObject* tmp;
	for(i=0; i<size; i++){
		tmp = PyList_GetItem(List, i);
		//op = output + val*i;
		//p = PyBytes_AsString(tmp);
		//printf("b %p\n", &output[i]);
		//strncpy(output[i], PyBytes_AsString(tmp), maxlen);
		PyBytes_AsStringAndSize(tmp, &p, &maxlen);
		strncpy(output[i], p, maxlen);
		//printf("a %p %s\n", output[i], output[i]);
		
	}
	return 0;
}

/************************************************************/
/*C-Pythonデータ変換関連*/
static PyObject* getInfo(PyObject *self, PyObject *args)
{
	int num;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	model = &g_model[num];
	return Py_BuildValue("{s:y,s:y,s:y,s:y,"
							"s:i,s:i,s:i,s:i,"
							"s:i,s:i,s:i,s:i,"
							"s:i,s:i,s:i,s:O}",
							"name", model->header.name.c_str(),
							"name_eng", model->header.name_eng.c_str(),
							"comment", model->header.comment.c_str(),
							"comment_eng", model->header.comment_eng.c_str(),
							
							"vt_count", model->vt.size(),
							"face_count", model->vt_index.size()/3,
							"mat_count", model->mat.size(),
							"bone_count", model->bone.size(),
							
							"IK_count", model->IK_list.size(),
							"skin_count", model->skin.size(),
							"bone_group_count", model->bone_group_count,
							"bone_disp_count", model->bone_disp_count,
							
							"eng_support", model->eng_support,
							"rb_count", model->rbody_count,
							"joint_count", model->joint_count,
							"skin_index", (model->skin_index.empty() 
								? PyList_New(0)
								: Array_to_PyList_UShort(&model->skin_index[0], model->skin_index.size()))
								);
}

static PyObject* getVt(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	if(model->vt.size() <= i)Py_RETURN_NONE;
	return Py_BuildValue("{s:O,s:O,s:O,"
							"s:i,s:i,"
							"s:i,s:i}",
							"loc", Array_to_PyList_Float(model->vt[i].loc, 3),
							"nor", Array_to_PyList_Float(model->vt[i].nor, 3),
							"uv" , Array_to_PyList_Float(model->vt[i].uv , 2),
							"bone_num1", (int)model->vt[i].bone_num0,
							"bone_num2", (int)model->vt[i].bone_num1,
							"weight", (int)model->vt[i].bone_weight,
							"edge", (int)model->vt[i].edge_flag);
}

static PyObject* getFace(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	i = i*3;
	if(model->vt_index.size()+3 < i)Py_RETURN_NONE;
	return Array_to_PyList_UShort(&model->vt_index[i], 3);
}

static PyObject* getMat(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	if(model->mat.size() <= i)Py_RETURN_NONE;
	return Py_BuildValue("{s:O,s:f,s:f,"
							"s:O,s:O,"
							"s:i,s:i,s:i,"
							"s:y,s:y,s:y,s:y}",
							"diff_col", Array_to_PyList_Float(model->mat[i].diffuse, 3),
							"alpha", model->mat[i].alpha,
							"spec", model->mat[i].spec,
							"spec_col", Array_to_PyList_Float(model->mat[i].spec_col, 3),
							"mirr_col", Array_to_PyList_Float(model->mat[i].mirror_col, 3),
							
							"toon", (int)model->mat[i].toon_index,
							"edge", (int)model->mat[i].edge_flag,
							"face_count", (int)model->mat[i].vt_index_count/3,
							"tex", model->mat[i].tex,
							"sph", model->mat[i].sph,
							"tex_path", model->mat[i].tex_path,
							"sph_path", model->mat[i].sph_path);
}

static PyObject* getBone(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	if(model->bone.size() <= i)Py_RETURN_NONE;
	return Py_BuildValue("{s:y,s:y,"
							"s:i,s:i,s:i,s:i"
							"s:O}",
							"name", model->bone[i].name,
							"name_eng", model->bone[i].name_eng,
							
							"parent", model->bone[i].PBone_index,
							"tail", model->bone[i].TBone_index,
							"type", model->bone[i].type,
							"IK", model->bone[i].IKBone_index,
							
							"loc", Array_to_PyList_Float(model->bone[i].loc, 3));
}

static PyObject* getIK(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	if(model->IK_list.size() <= i)Py_RETURN_NONE;
	printf("IKchainlen :%d\n", model->IK_list[i].IKCBone_index.size());
	return Py_BuildValue("{s:i,s:i,s:i,s:i,s:f,s:O}",
							"index", (int)model->IK_list[i].IKBone_index,
							"tail", (int)model->IK_list[i].IKTBone_index,
							"len", (int)model->IK_list[i].IKCBone_index.size(),
							"ite", (int)model->IK_list[i].iterations,
							"weight", (float)model->IK_list[i].weight,
							"child", Array_to_PyList_UShort(&model->IK_list[i].IKCBone_index[0], (int)model->IK_list[i].IKCBone_index.size()));
}

static PyObject* getSkin(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	if(model->skin.size() <= i)Py_RETURN_NONE;
	return Py_BuildValue("{s:y,s:y,"
							"s:i,s:i}",
							"name", model->skin[i].name,
							"name_eng", model->skin[i].name_eng,
							"count", (int)model->skin[i].data.size(),
							"type", (int)model->skin[i].type);
}

static PyObject* getSkindata(PyObject *self, PyObject *args)
{
	int num, i, j;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "iii", &num, &i, &j))return NULL;
	model = &g_model[num];
	return Py_BuildValue("{s:i,s:[fff]}",
							"index", model->skin[i].data[j].index,
							"loc", model->skin[i].data[j].loc[0],
							model->skin[i].data[j].loc[1],
							model->skin[i].data[j].loc[2]);
}

static PyObject* getBone_group(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	return Py_BuildValue("{s:y,s:y}",
							"name", model->bone_group[i].name,
							"name_eng", model->bone_group[i].name_eng);
}

static PyObject* getBone_disp(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	return Py_BuildValue("{s:i,s:i}",
							"index", (int)model->bone_disp[i].index,
							"bone_group", (int)model->bone_disp[i].bone_group);
}

static PyObject* getToon(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	model = &g_model[num];
	return Py_BuildValue("[y,y,y,y,y,"
							"y,y,y,y,y]",
							model->toon[0],
							model->toon[1],
							model->toon[2],
							model->toon[3],
							model->toon[4],
							model->toon[5],
							model->toon[6],
							model->toon[7],
							model->toon[8],
							model->toon[9]);
}

static PyObject* getToonPath(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	model = &g_model[num];
	//printf("%s\n", model->toon_path[0]);
	return Py_BuildValue("[y,y,y,y,y,"
							"y,y,y,y,y]",
							model->toon_path[0],
							model->toon_path[1],
							model->toon_path[2],
							model->toon_path[3],
							model->toon_path[4],
							model->toon_path[5],
							model->toon_path[6],
							model->toon_path[7],
							model->toon_path[8],
							model->toon_path[9]);
}

static PyObject* getRb(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	return Py_BuildValue("{s:y,s:i,s:i,s:i,s:i,"
							"s:[f,f,f],s:[f,f,f],s:[f,f,f],"
							"s:[f,f,f,f,f],"
							"s:i}",
							"name",   model->rbody[i].name,
							"bone",   (int)model->rbody[i].bone,
							"group",  (int)model->rbody[i].group,
							"target", (int)model->rbody[i].target,
							"shape",  (int)model->rbody[i].shape,
							"size",   model->rbody[i].size[0], model->rbody[i].size[1], model->rbody[i].size[2],
							"loc",    model->rbody[i].loc[0], model->rbody[i].loc[1], model->rbody[i].loc[2],
							"rot",    model->rbody[i].rot[0], model->rbody[i].rot[1], model->rbody[i].rot[2],
							"prop",
								model->rbody[i].property[0],
								model->rbody[i].property[1],
								model->rbody[i].property[2],
								model->rbody[i].property[3],
								model->rbody[i].property[4],
							"t",      (int)model->rbody[i].type);
}

static PyObject* getJoint(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	
	if(!PyArg_ParseTuple(args, "ii", &num, &i))return NULL;
	model = &g_model[num];
	return Py_BuildValue("{s:y,s:[I,I],"
							"s:[f,f,f],s:[f,f,f],"
							"s:[f,f,f,f,f,f,f,f,f,f,f,f],"
							"s:[f,f,f,f,f,f]}",
							"name",   model->joint[i].name,
							"rbody",  model->joint[i].rbody[0], model->joint[i].rbody[1],
							"loc",
								model->joint[i].loc[0],
								model->joint[i].loc[1],
								model->joint[i].loc[2],
							"rot",
								model->joint[i].rot[0],
								model->joint[i].rot[1],
								model->joint[i].rot[2],
							"limit",
								model->joint[i].limit[0],
								model->joint[i].limit[1],
								model->joint[i].limit[2],
								model->joint[i].limit[3],
								model->joint[i].limit[4],
								model->joint[i].limit[5],
								model->joint[i].limit[6],
								model->joint[i].limit[7],
								model->joint[i].limit[8],
								model->joint[i].limit[9],
								model->joint[i].limit[10],
								model->joint[i].limit[11],
							"spring",
								model->joint[i].spring[0],
								model->joint[i].spring[1],
								model->joint[i].spring[2],
								model->joint[i].spring[3],
								model->joint[i].spring[4],
								model->joint[i].spring[5]);
}

static PyObject* Create_FromInfo(PyObject *self, PyObject *args)
{
	int num, i, size;
	MODEL model, *p;
	PyObject *PyTmp;
	char *str[4];
	
	create_PMD(&model);
	
	int vt_count;
	int vt_index_count;
	int mat_count;
	int bone_count;
	int IK_count;
	int skin_count;
	int skin_disp_count;
	if(!PyArg_ParseTuple(args, "i"
							"yyyy"
							"iiii"
							"iiii"
							"iii"
							"iO",
							&num,
							&str[0],
							&str[1],
							&str[2],
							&str[3],
							
							&vt_count,
							&vt_index_count,
							&mat_count,
							&bone_count,
							
							&IK_count,
							&skin_count,
							&model.bone_group_count,
							&model.bone_disp_count,
							
							&model.eng_support,
							&model.rbody_count,
							&model.joint_count,
							&skin_disp_count,
							&PyTmp))return NULL;
	
	model.header.name=str[0];
	model.header.comment=str[1];
	model.header.name_eng=str[2];
	model.header.comment_eng=str[3];
	
	p = &g_model[num];
	

	
	delete_PMD(p);
	*p = model;
	
	/*メモリ確保************************************************************************/
	p->vt.resize(vt_count);
	p->vt_index.resize(vt_index_count * 3);
	p->mat.resize(mat_count);
	p->bone.resize(bone_count);
	
	//IKリスト
	p->IK_list.resize(IK_count);
	
	//表情
	p->skin.resize(skin_count);
	
	//表情表示
	p->skin_index.resize(skin_disp_count);
	PyList_to_Array_UShort(&p->skin_index[0], PyTmp, p->skin_index.size());
	
	//ボーン表示グループ
	size = p->bone_group_count * sizeof(BONE_GROUP);
	p->bone_group = (BONE_GROUP*)MALLOC(size);
	memset(p->bone_group, 0, size);
	
	//表示ボーン
	size = p->bone_disp_count * sizeof(BONE_DISP);
	p->bone_disp = (BONE_DISP*)MALLOC(size);
	memset(p->bone_disp, 0, size);
	
	//剛体
	size = p->rbody_count * sizeof(RIGID_BODY);
	p->rbody = (RIGID_BODY*)MALLOC(size);
	memset(p->rbody, 0, size);
	
	//ジョイント
	size = p->joint_count * sizeof(JOINT);
	p->joint = (JOINT*)MALLOC(size);
	memset(p->joint, 0, size);
	
	return Py_BuildValue("i", 0);
}


static PyObject* setVt(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *PyTmp[3];
	VERTEX vt;
	if(!PyArg_ParseTuple(args,
							"iiOOO"
							"hh"
							"bb",
							&num, &i,
							&PyTmp[0],
							&PyTmp[1],
							&PyTmp[2],
							&vt.bone_num0,
							&vt.bone_num1,
							&vt.bone_weight,
							&vt.edge_flag))return NULL;
	PyList_to_Array_Float(vt.loc, PyTmp[0], 3);
	PyList_to_Array_Float(vt.nor, PyTmp[1], 3);
	PyList_to_Array_Float(vt.uv , PyTmp[2], 2);
	
	model = &g_model[num];
	if(model->vt.size() <= i)Py_RETURN_NONE;
	model->vt[i] = vt;
	return Py_BuildValue("i", 0);
}

static PyObject* setFace(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *PyTmp;
	if(!PyArg_ParseTuple(args,
							"iiO",
							&num, &i,
							&PyTmp))return NULL;
	
	model = &g_model[num];
	if(model->vt_index.size() < i*3+3)Py_RETURN_NONE;
	
	PyList_to_Array_UShort(&model->vt_index[i*3], PyTmp, 3);
	return Py_BuildValue("i", 0);
}

static PyObject* setMat(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *PyTmp[3];
	MATERIAL mat;
	char *str[4];
	if(!PyArg_ParseTuple(args, "iiOffOOiiiyyyy",
							&num, &i,
							&PyTmp[0],
							&mat.alpha,
							&mat.spec,
							&PyTmp[1],
							&PyTmp[2],
							
							&mat.toon_index,
							&mat.edge_flag,
							&mat.vt_index_count,
							&str[0],
							&str[1],
							&str[2],
							&str[3]))return NULL;
	
	model = &g_model[num];
	if(model->mat.size() <= i)Py_RETURN_NONE;
	
	mat.vt_index_count = mat.vt_index_count*3;
	PyList_to_Array_Float(mat.diffuse, PyTmp[0], 3);
	PyList_to_Array_Float(mat.spec_col, PyTmp[1], 3);
	PyList_to_Array_Float(mat.mirror_col, PyTmp[2], 3);
	
	strncpy(mat.tex, str[0], NAME_LEN);
	strncpy(mat.sph, str[1], NAME_LEN);
	strncpy(mat.tex_path, str[2], PATH_LEN);
	strncpy(mat.sph_path, str[3], PATH_LEN);
	model->mat[i] = mat;
	return Py_BuildValue("i", 0);
}

static PyObject* setBone(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *PyTmp;
	BONE bone;
	char *str[2];
	if(!PyArg_ParseTuple(args, "iiyyiiiiO",
									&num, &i,
									&str[0],
									&str[1],

									&bone.PBone_index,
									&bone.TBone_index,
									&bone.type,
									&bone.IKBone_index,

									&PyTmp))return NULL;
	model = &g_model[num];
	if(model->bone.size() <= i)Py_RETURN_NONE;
	
	strncpy(bone.name,     str[0], NAME_LEN);
	strncpy(bone.name_eng, str[1], NAME_LEN);
	
	PyList_to_Array_Float(bone.loc, PyTmp, 3);
	model->bone[i] = bone;
	return Py_BuildValue("i", 0);
}

static PyObject* setIK(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *PyTmp;
	IK_LIST IK_list;
	int IK_chain_len;
	if(!PyArg_ParseTuple(args, "iiiiiifO",
							&num, &i,
							&IK_list.IKBone_index,
							&IK_list.IKTBone_index,
							&IK_chain_len,
							&IK_list.iterations,
							&IK_list.weight,
							&PyTmp))return NULL;
	model = &g_model[num];
	if(model->IK_list.size() <= i)Py_RETURN_NONE;
	
	//printf("%d %d\n", IK_list.IK_chain_len, model->IK_list[i].IK_chain_len);
	IK_list.IKCBone_index.resize(IK_chain_len);
	IK_list.IKCBone_index = model->IK_list[i].IKCBone_index;
	
	PyList_to_Array_UShort(&IK_list.IKCBone_index[0], PyTmp, IK_list.IKCBone_index.size());
	
	model->IK_list[i] = IK_list;
	return Py_BuildValue("i", 0);
}

static PyObject* setSkin(PyObject *self, PyObject *args)
{
	int num, i, size;
	MODEL *model;
	SKIN skin;
	char *str[2];
	
	int skin_vt_count;
	if(!PyArg_ParseTuple(args, "iiyyib",
							&num, &i,
							&str[0],
							&str[1],
							&skin_vt_count,
							&skin.type))return NULL;
	model = &g_model[num];
	if(model->skin.size() <= i)Py_RETURN_NONE;
	
	strncpy(skin.name,     str[0], NAME_LEN);
	strncpy(skin.name_eng, str[1], NAME_LEN);
	
	//メモリ確保
	skin.data.resize(skin_vt_count);
	
	model->skin[i] = skin;
	
	return Py_BuildValue("i", 0);
}

static PyObject* setSkindata(PyObject *self, PyObject *args)
{
	int num, i, j;
	MODEL *model;
	PyObject *PyTmp;
	SKIN_DATA data;
	if(!PyArg_ParseTuple(args, "iiii(fff)",
							&num, &i, &j,
							&data.index,
							&data.loc[0],
							&data.loc[1],
							&data.loc[2]))return NULL;
	
	model = &g_model[num];
	
	if(model->skin.size() <= i)Py_RETURN_NONE;
	if(model->skin[i].data.size() <= j)Py_RETURN_NONE;
	
	model->skin[i].data[j] = data;
	return Py_BuildValue("i", 0);
}

static PyObject* setBone_group(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	BONE_GROUP bone_group;
	char *str[2];
	if(!PyArg_ParseTuple(args, "iiyy",
							&num, &i,
							&str[0],
							&str[1]))return NULL;
	model = &g_model[num];
	
	strncpy(bone_group.name,     str[0], NAME_LEN);
	strncpy(bone_group.name_eng, str[1], NAME_LEN);
	
	model->bone_group[i] = bone_group;
	
	return Py_BuildValue("i", 0);
}

static PyObject* setBone_disp(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	BONE_DISP bone_disp;
	if(!PyArg_ParseTuple(args, "iiHB",
							&num, &i,
							&bone_disp.index,
							&bone_disp.bone_group))return NULL;
	model = &g_model[num];
	model->bone_disp[i] = bone_disp;
	
	return Py_BuildValue("i", 0);
}

static PyObject* setToon(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *tmp;
	char *p[10];
	
	if(!PyArg_ParseTuple(args, "iO",
							&num,/*
							&model->toon[0],
							&model->toon[1],
							&model->toon[2],
							&model->toon[3],
							&model->toon[4],
							&model->toon[5],
							&model->toon[6],
							&model->toon[7],
							&model->toon[8],
							&model->toon[9]*/
							&tmp))return NULL;
	model = &g_model[num];
	for(i=0; i<10; i++){
		p[i] = model->toon[i];
	}
	
	PyList_to_Array_Str(p, tmp, 10, 100);
	/*
	for(i=0; i<10; i++){
		strncpy(model->toon[i], p[i], 100);
		//printf("%s %s\n",model->toon[i], p[i]);
	}*/
	
	return Py_BuildValue("i", 0);
}

static PyObject* setToonPath(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	PyObject *tmp;
	char *p[10];
	if(!PyArg_ParseTuple(args, "iO",
							&num,
							&tmp))return NULL;
	model = &g_model[num];
	for(i=0; i<10; i++){
		p[i] = model->toon_path[i];
	}
	
	PyList_to_Array_Str(p, tmp, 10, PATH_LEN);
	/*
	for(i=0; i<10; i++){
		strncpy(model->toon_path[i], p[i], PATH_LEN);
		//printf("%s %s\n",model->toon[i], p[i]);
	}
	*/
	return Py_BuildValue("i", 0);
}

static PyObject* setRb(PyObject *self, PyObject *args)
{
	int num=0, i=0;
	MODEL *model;
	RIGID_BODY rbody;
	char *str;
	
	if(!PyArg_ParseTuple(args, "ii"
							"yHBHB"
							"(fff)(fff)(fff)"
							"fffffB",
							&num, &i,
							&str,
							&rbody.bone,
							&rbody.group,
							&rbody.target,
							&rbody.shape,
							&rbody.size[0], &rbody.size[1], &rbody.size[2],
							&rbody.loc[0], &rbody.loc[1], &rbody.loc[2],
							&rbody.rot[0], &rbody.rot[1], &rbody.rot[2],
							
							&rbody.property[0],
							&rbody.property[1],
							&rbody.property[2],
							&rbody.property[3],
							&rbody.property[4],
							&rbody.type))return NULL;
	model = &g_model[num];
	
	strncpy(rbody.name, str, NAME_LEN);
	
	model->rbody[i] = rbody;
	
	return Py_BuildValue("i", 0);
}

static PyObject* setJoint(PyObject *self, PyObject *args)
{
	int num, i;
	MODEL *model;
	JOINT joint;
	char *str;
	if(!PyArg_ParseTuple(args, "ii"
							"y(II)(fff)(fff)"
							"(ffffffffffff)"
							"(ffffff)",
							&num, &i,
							&str,
							&joint.rbody[0], &joint.rbody[1],
							&joint.loc[0],
							&joint.loc[1],
							&joint.loc[2],
							&joint.rot[0],
							&joint.rot[1],
							&joint.rot[2],
							&joint.limit[0],
							&joint.limit[1],
							&joint.limit[2],
							&joint.limit[3],
							&joint.limit[4],
							&joint.limit[5],
							&joint.limit[6],
							&joint.limit[7],
							&joint.limit[8],
							&joint.limit[9],
							&joint.limit[10],
							&joint.limit[11],
							&joint.spring[0],
							&joint.spring[1],
							&joint.spring[2],
							&joint.spring[3],
							&joint.spring[4],
							&joint.spring[5]))return NULL;
	model = &g_model[num];
	strncpy(joint.name, str, NAME_LEN);
	model->joint[i] = joint;
	return Py_BuildValue("i", 0);
}
/*******************************************************************************/
static PyObject* Set_List(PyObject *self, PyObject *args)
{
	PyObject *bn, *bne, *sn, *sne, *gn, *gne;
	int bone_count;
	int skin_count;
	int disp_count;
	if (!PyArg_ParseTuple(args, "iOOiOOiOO",
		&bone_count, &bn, &bne,
		&skin_count, &sn, &sne,
		&disp_count, &gn, &gne))return NULL;

	list.clear();


	// ボーン
	for (int i = 0; i < bone_count; i++) {
		list.bone.push_back(NameWithEnglish());
		char *p = NULL;
		PyObject *tmp;
		Py_ssize_t len = NAME_LEN;

		tmp = PyList_GetItem(bn, i);
		PyBytes_AsStringAndSize(tmp, &p, &len);
		list.bone.back().name = p;

		tmp = PyList_GetItem(bne, i);
		PyBytes_AsStringAndSize(tmp, &p, &len);
		list.bone.back().english = p;
	}

	// 表情
	for (int i = 0; i < skin_count; i++) {
		list.skin.push_back(NameWithEnglish());
		char *p = NULL;
		PyObject *tmp;
		Py_ssize_t len = NAME_LEN;

		tmp = PyList_GetItem(sn, i);
		PyBytes_AsStringAndSize(tmp, &p, &len);
		list.skin.back().name = p;

		tmp = PyList_GetItem(sne, i);
		PyBytes_AsStringAndSize(tmp, &p, &len);
		list.skin.back().english = p;
	}

	// ボーングループ
	for (int i = 0; i < disp_count; i++) {
		list.disp.push_back(NameWithEnglish());
		char *p = NULL;
		PyObject *tmp;
		Py_ssize_t len = NAME_LEN;

		tmp = PyList_GetItem(gn, i);
		PyBytes_AsStringAndSize(tmp, &p, &len);
		list.disp.back().name = p;

		tmp = PyList_GetItem(gne, i);
		PyBytes_AsStringAndSize(tmp, &p, &len);
		list.disp.back().english = p;
	}

	return Py_BuildValue("i", 0);
}

/*******************************************************************************/

static PyObject* Set_Name_Comment(PyObject *self, PyObject *args)
{
	const char *name;
	const char *comment;
	const char *name_eng;
	const char *comment_eng;
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "iyyyy", &num, &name, &comment, &name_eng, &comment_eng))return NULL;
	g_model[num].header.name=name;
	g_model[num].header.comment=comment;
	g_model[num].header.name_eng=name_eng;
	g_model[num].header.comment_eng=comment_eng;
	return Py_BuildValue("i", 0);
}

/*******************************************************************************/
static PyObject* Init_PMD(PyObject *self, PyObject *args)
{
	int i;
	
	for(i=0; i<MODEL_COUNT; i++){
		create_PMD(&g_model[i]);
	}
	return Py_BuildValue("i", 0);
}

static PyObject* Load_PMD(PyObject *self, PyObject *args)
{
	const char *str;
	int num;
	int ret;
	
	if(!PyArg_ParseTuple(args, "iy", &num, &str))return NULL;
	delete_PMD(&g_model[num]);
	ret = load_PMD(&g_model[num], str);
	
	return Py_BuildValue("i", ret);
}

static PyObject* Write_PMD(PyObject *self, PyObject *args)
{
	const char *str;
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "iy", &num, &str))return NULL;
	ret = write_PMD(&g_model[num], str);
	return Py_BuildValue("i", ret);
}

static PyObject* Add_PMD(PyObject *self, PyObject *args)
{
	int num,add;
	int ret=1;
	MODEL model;
	create_PMD(&model);
	if(!PyArg_ParseTuple(args, "ii", &num, &add))return NULL;
	
	add_PMD(&g_model[num], &g_model[add]);
	delete_PMD(&model);
	return Py_BuildValue("i", ret);
}

static PyObject* Copy_PMD(PyObject *self, PyObject *args)
{
	int src, dst;
	int ret=1;
	if(!PyArg_ParseTuple(args, "ii", &src, &dst))return NULL;
	delete_PMD(&g_model[dst]);
	ret = copy_PMD(&g_model[dst], &g_model[src]);
	if(ret != 0){
		return Py_BuildValue("i", ret);
	}
	return Py_BuildValue("i", ret);
}

static PyObject* Create_PMD(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	ret = delete_PMD(&g_model[num]);
	return Py_BuildValue("i", ret);
}

static PyObject* Marge_PMD(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	puts("ボーンマージ");
	ret = marge_bone(&g_model[num]);
	puts("材質マージ");
	ret += marge_mat(&g_model[num]);
	puts("IKマージ");
	ret += marge_IK(&g_model[num]);
	puts("ボーングループマージ");
	ret += marge_bone_disp(&g_model[num]);
	puts("剛体マージ");
	ret += marge_rb(&g_model[num]);
	return Py_BuildValue("i", ret);
}

static PyObject* Sort_PMD(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	
	rename_tail(&g_model[num]);
	puts("ボーンマージ");
	ret = marge_bone(&g_model[num]);
	
	puts("ボーンソート");
	ret = sort_bone(&g_model[num], &list);
	puts("表情ソート");
	ret += sort_skin(&g_model[num], &list);
	puts("ボーングループソート");
	ret += sort_disp(&g_model[num], &list);
		
	//-0ボーン削除
	if(strcmp(g_model[num].bone[g_model[num].bone.size()-1].name, "-0") == 0){
		g_model[num].bone.resize(g_model[num].bone.size()-1);
	}
	puts("英語対応化");
	translate(&g_model[num], &list, 1);
	return Py_BuildValue("i", ret);
}
/*************************************************************************************************/
static PyObject* Resize_Model(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	double size;
	if(!PyArg_ParseTuple(args, "id", &num, &size))return NULL;
	ret = resize_model(&g_model[num], size);
	return Py_BuildValue("i", ret);
}

static PyObject* Move_Model(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	double s[3];
	if(!PyArg_ParseTuple(args, "iddd", &num, &s[0], &s[1], &s[2]))return NULL;
	ret = move_model(&g_model[num], s);
	return Py_BuildValue("i", ret);
}


static PyObject* Resize_Bone(PyObject *self, PyObject *args)
{
	const char *str;
	int num, index;
	int ret;
	double len,thi;
	if(!PyArg_ParseTuple(args, "iydd", &num, &str, &len, &thi))return NULL;
	for(index=0; index<g_model[num].bone.size(); index++){
		if(strcmp(g_model[num].bone[index].name,str)==0){
			break;
		}
	}
	if(index==g_model[num].bone.size()){
		return Py_BuildValue("i", -1);
	}
	ret=scale_bone(&g_model[num], index, thi, len, thi);
	return Py_BuildValue("i", ret);
}

static PyObject* Move_Bone(PyObject *self, PyObject *args)
{
	const char *str;
	int num, index;
	int ret;
	double pos[3];
	if(!PyArg_ParseTuple(args, "iyddd", &num, &str, &pos[0], &pos[1], &pos[2]))return NULL;
	for(index=0; index<g_model[num].bone.size(); index++){
		if(strcmp(g_model[num].bone[index].name,str)==0){
			break;
		}
	}
	if(index==g_model[num].bone.size()){
		return Py_BuildValue("i", -1);
	}
	ret=move_bone(&g_model[num], index, pos);
	return Py_BuildValue("i", ret);
}

static PyObject* Update_Skin(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	
	ret=update_skin(&g_model[num]);
	return Py_BuildValue("i", ret);
}

static PyObject* Adjust_Joints(PyObject *self, PyObject *args)
{
	int num;
	int ret;
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	
	ret=adjust_joint(&g_model[num]);
	return Py_BuildValue("i", ret);
}
/*************************************************************************************************/
static PyObject* getWHT(PyObject *self, PyObject *args)
{
	const char *str;
	int num, i, j;
	double wht[3];
	double min[3] = {0.0,0.0,0.0};
	double max[3] = {0.0,0.0,0.0};
	
	if(!PyArg_ParseTuple(args, "i", &num))return NULL;
	
	for(i=0; i<g_model[num].vt.size(); i++){
		for(j=0; j<3; j++){
			if(g_model[num].vt[i].loc[j] > max[j]){
				max[j] = g_model[num].vt[i].loc[j];
			}else if(g_model[num].vt[i].loc[j] < min[j]){
				min[j] = g_model[num].vt[i].loc[j];
			}
		}
	}
	
	for(i=0; i<3; i++){
		wht[i] = (max[i] - min[i])*8;
	}
	
	return Py_BuildValue("(fff)", wht[0],wht[1],wht[2]);
}

static PyMethodDef PMCAMethods[] = {
	{"getInfo", getInfo, METH_VARARGS,
	"Get Info of PMD"},
	{"getVt", getVt, METH_VARARGS,
	"Get Vertex of PMD"},
	{"getFace", getFace, METH_VARARGS,
	"Get Face of PMD"},
	{"getMat", getMat, METH_VARARGS,
	"Get Material of PMD"},
	{"getBone", getBone, METH_VARARGS,
	"Get Bone of PMD"},
	{"getIK", getIK, METH_VARARGS,
	"Get IK_List of PMD"},
	{"getSkin", getSkin, METH_VARARGS,
	"Get Skin of PMD"},
	{"getSkindata", getSkindata, METH_VARARGS,
	"Get Skin_data of PMD"},
	{"getBone_group", getBone_group, METH_VARARGS,
	"Get Bone_group of PMD"},
	{"getBone_disp", getBone_disp, METH_VARARGS,
	"Get Bone_disp of PMD"},
	{"getToon", getToon, METH_VARARGS,
	"Get Toon textures of PMD"},
	{"getToonPath", getToonPath, METH_VARARGS,
	"Get Toon textures path of PMD"},
	{"getRb", getRb, METH_VARARGS,
	"Get Rigid bodies of PMD"},
	{"getJoint", getJoint, METH_VARARGS,
	"Get Joints of PMD"},
	/******************************************************************/
	{"Create_FromInfo", Create_FromInfo, METH_VARARGS,
	"Create PMD"},
	{"setVt", setVt, METH_VARARGS,
	"Set Vertex of PMD"},
	{"setFace", setFace, METH_VARARGS,
	"Set Face of PMD"},
	{"setMat", setMat, METH_VARARGS,
	"Set Material of PMD"},
	{"setBone", setBone, METH_VARARGS,
	"Set Bone of PMD"},
	{"setIK", setIK, METH_VARARGS,
	"Set IK_List of PMD"},
	{"setSkin", setSkin, METH_VARARGS,
	"Set Skin of PMD"},
	{"setSkindata", setSkindata, METH_VARARGS,
	"Set Skin_data of PMD"},
	{"setBone_group", setBone_group, METH_VARARGS,
	"Set Bone_group of PMD"},
	{"setBone_disp", setBone_disp, METH_VARARGS,
	"Set Bone_disp of PMD"},
	{"setToon", setToon, METH_VARARGS,
	"Set Toon textures of PMD"},
	{"setToonPath", setToonPath, METH_VARARGS,
	"Set Toon textures path of PMD"},
	{"setRb", setRb, METH_VARARGS,
	"Set Rigid bodies of PMD"},
	{"setJoint", setJoint, METH_VARARGS,
	"Set Joints of PMD"},
	/***********************************************************************/
	{"Set_List", Set_List, METH_VARARGS,
	"Set List of bone or things"},
	/***********************************************************************/
	{"Set_Name_Comment", Set_Name_Comment, METH_VARARGS,
	"Set Name and Comment"},
	/***********************************************************************/
	{"Init_PMD", Init_PMD, METH_VARARGS,
	"Initialize"},
	{"Load_PMD", Load_PMD, METH_VARARGS,
	"Load PMD from file"},
	{"Write_PMD", Write_PMD, METH_VARARGS,
	"Write PMD from file"},
	{"Add_PMD", Add_PMD, METH_VARARGS,
	"Add PMD from file"},
	{"Copy_PMD", Copy_PMD, METH_VARARGS,
	"Copy PMD"},
	{"Create_PMD", Create_PMD, METH_VARARGS,
	"Create enpty PMD"},
	{"Marge_PMD", Marge_PMD, METH_VARARGS,
	"Marge PMD"},
	{"Sort_PMD", Sort_PMD, METH_VARARGS,
	"Sort PMD"},

	{"Resize_Model", Resize_Model, METH_VARARGS,
	"Resize_Model"},
	{"Move_Model", Move_Model, METH_VARARGS,
	"Move_Model"},
	{"Resize_Bone", Resize_Bone, METH_VARARGS,
	"Resize_Bone"},
	{"Move_Bone", Move_Bone, METH_VARARGS,
	"Move_Bone"},
	{"Update_Skin", Update_Skin, METH_VARARGS,
	"Update_Skin"},
	{"Adjust_Joints", Adjust_Joints, METH_VARARGS,
	"Adjust_Joints"},
	
	{"getWHT", getWHT, METH_VARARGS,
	"get height, width, thickness from model"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef PMCAmodule = {
    PyModuleDef_HEAD_INIT,
    "PMCA",
    NULL,
    -1,
    PMCAMethods,
    NULL,
    NULL,
    NULL,
    NULL
};

// モジュール登録
PyMODINIT_FUNC PyInit_PMCA(void) {
	PyObject *m;
	//static void *PySpam_API[PyPMCA_API_pointers];
	//PyObject *c_api_object;
	
	
	m = PyModule_Create(&PMCAmodule);
	if (m == NULL)
		return NULL;
	
	PMCAError = PyErr_NewException("PMCA.error", NULL, NULL);
	Py_INCREF(PMCAError);
	PyModule_AddObject(m, "error", PMCAError);
		
	/*
	// Initialize the C API pointer array
	PyPMCA_API[PyPMCA_System_NUM] = (void *)PyPMCA_System;
	
	// Create a Capsule containing the API pointer array's address
	c_api_object = PyCapsule_New((void *)PyPMCA_API, "PMCA._C_API", NULL);
	
	if (c_api_object != NULL)
        PyModule_AddObject(m, "_C_API", c_api_object);
	*/
	return m;
}

#ifdef __cplusplus
}
#endif