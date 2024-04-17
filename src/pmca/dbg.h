#pragma once
#include <stdio.h>

size_t FREAD(void *p, size_t s, size_t n, FILE *fp);
void *FGETS(char *p, size_t s, FILE *fp);
void *MALLOC(size_t s);
void FREE(void *p);
