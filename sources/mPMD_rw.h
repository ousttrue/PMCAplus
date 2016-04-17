#pragma once
#include "mPMD.h"



int load_PMD(MODEL *model, const char file_name[]);
int write_PMD(MODEL *model, const char file_name[]);
int print_PMD(MODEL *model, const char file_name[]);
int create_PMD(MODEL *model);
int delete_PMD(MODEL *model);
int copy_PMD(MODEL *out, MODEL *model);
