#pragma once
#include <memory>

struct FLAGS {
  int button1;
  int button2;
  int button3;
  int model_lock;
  int quit;
};

extern FLAGS myflags;

enum class Mode {
  // 初期化
  Init = -1,
  // 書き込み
  Write = 0,
  // 読み出し
  Read = 1,
  // 描画モデル読み出し
  ReadModel = 2,
  // テクスチャはそのままで再セット
  Reset = 3,
};

struct VIEW_STATE {
  int width;
  int height;

  int x;
  int y;
  int sx;
  int sy;

  double rt[16];
  double cq[4];
  double tq[4];

  double move[3];

  double scale;

  int show_axis;

  VIEW_STATE();
};

void *model_mgr(Mode flag, int num, void *p);
int setup_opengl();
void draw_screen(const VIEW_STATE &vs);
