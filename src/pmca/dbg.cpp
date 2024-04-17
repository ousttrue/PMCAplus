#include "dbg.h"
#include <plog/Log.h>

size_t FREAD(void *p, size_t s, size_t n, FILE *fp) {
  if (s * n == 0)
    return 0;

  auto r = fread(p, s, n, fp);
  if (r < n) {
    PLOG_ERROR << "ファイル読み込みに失敗";
    throw std::runtime_error("ファイル読み込みに失敗");
  }

  return r;
}

void *FGETS(char *p, size_t s, FILE *fp) {
  auto r = fgets(p, s, fp);
  if (r == NULL) {
    PLOG_ERROR << "ファイル読み込みに失敗";
    throw std::runtime_error("ファイル読み込みに失敗");
  }

  return r;
}

void *MALLOC(size_t s) {
  auto p = malloc(s);
  if (p == NULL) {
    PLOG_ERROR << "メモリの確保に失敗しました";
    throw std::runtime_error("メモリの確保に失敗しました");
  }

  return p;
}

void FREE(void *p) {
  if (p == NULL)
    return;
  free(p);
}
