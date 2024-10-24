#pragma once
#include <stdio.h>

#define FREAD dbg_fread
#define FGETS dbg_fgets
#define MALLOC dbg_malloc
#define FREE dbg_free

size_t dbg_fread(void *p, size_t s, size_t n, FILE *fp);
void *dbg_fgets(char *, size_t, FILE *);
void *dbg_malloc(size_t);
void dbg_free(void *);
