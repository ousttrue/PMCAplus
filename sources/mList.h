#pragma once
#include <vector>
#include <string>


struct NameWithEnglish
{
	std::string name;
	std::string english;
};

struct LIST 
{
    std::vector<NameWithEnglish> bone;
	std::vector<NameWithEnglish> skin;
	std::vector<NameWithEnglish> disp;
    bool load(const std::string &dir);
	void clear()
	{
		bone.clear();
		skin.clear();
		disp.clear();
	}
};
