#include "dbg.h"
#include <stdlib.h>

size_t dbg_fread(void *p, size_t s, size_t n, FILE *fp) {
  size_t r;
  if (s * n == 0)
    return 0;
  r = fread(p, s, n, fp);
  if (r < n) {
    printf("ファイル読み込みに失敗\nFILE:%p\nn:%d < %d\n", fp, (int)r, (int)n);
    exit(1);
  }

  return r;
}

void *dbg_fgets(char *p, size_t s, FILE *fp) {
  void *r;
  r = fgets(p, s, fp);
  if (r == NULL) {
    printf("ファイル読み込みに失敗\nFILE:%p %p\n", fp, r);
    exit(1);
  }

  return r;
}

void *dbg_malloc(size_t s) {
  void *p;
  p = malloc(s);
  if (p == NULL) {
    puts("メモリの確保に失敗しました");
    exit(-1);
  }
  return p;
}

void dbg_free(void *p) {
  if (p == NULL)
    return;
  free(p);
  p = NULL;
  // exit(1);
}
