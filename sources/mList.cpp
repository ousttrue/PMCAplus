#include "mList.h"


static std::string split_line(std::string &src)
{
	auto space = src.find(' ');
	auto lf = src.find('\n');
	src = std::string(src.begin() + space, src.begin() + lf);
	return src.substr(0, space);
}

bool LIST::load(const std::string &file_name)
{
	clear();

	if (file_name.empty()) {
		printf("ファイル名がありません\n");
		return false;
	}

	FILE *lst_file = fopen(file_name.c_str(), "r");
	if (lst_file == NULL) {
		printf("ファイル %s を開けません\n", file_name.c_str());
		return false;
	}
	char str[256];
	fgets(str, 256, lst_file);

	while (fgets(str, 256, lst_file) != NULL) {
		if (strcmp(str, "skin\n") == 0)break;
		std::string line(str, str + 256);
		bone.push_back(NameWithEnglish());
		bone.back().name = split_line(line);
		bone.back().english = line;
	}

	while (fgets(str, 256, lst_file) != NULL) {
		if (strcmp(str, "bone_disp\n") == 0)break;
		std::string line(str, str + 256);
		skin.push_back(NameWithEnglish());
		skin.back().name = split_line(line);
		skin.back().english = line;
	}

	while (fgets(str, 256, lst_file) != NULL) {
		if (strcmp(str, "end\n") == 0)break;
		std::string line(str, str + 256);
		disp.push_back(NameWithEnglish());
		disp.back().name = split_line(line);
		disp.back().english = line;
	}

	fclose(lst_file);
	return true;
}
