#include "PMCA_renderer.h"
#include "dsp_model.h"
#include "flags.h"
#include "quat.h"

#include <Windows.h>

#include <GL/GL.h>
#include <GL/GLU.h>
#include <chrono>
#include <plog/Log.h>
#include <string.h>
#include <thread>

FLAGS myflags;

VIEW_STATE::VIEW_STATE() {
  double tmp[4] = {1.0, 0.0, 0.0, 0.0};
  memcpy(this->tq, tmp, 4 * sizeof(double));
  memcpy(this->cq, tmp, 4 * sizeof(double));
  qrot(this->rt, this->tq);
  this->scale = 15.0;
}

int setup_opengl() {

  /* シェーディングモデルは Gouraud (なめらか) */
  // glShadeModel( GL_SMOOTH );

  /* 裏面を取り除く */
  glEnable(GL_CULL_FACE);
  glFrontFace(GL_CCW);
  glCullFace(GL_FRONT);

  /* 消去時の色をセット */
  glClearColor(0, 0, 0, 0);

  /*
   * 射影行列を変更し、ビューボリュームにセット。
   */
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();

  /*アルファブレンドを有効に*/
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  /*Zバッファを有効に*/
  glEnable(GL_DEPTH_TEST);

  glTranslatef(0.0, -10.0, -20.0);
  // glFrustum( -1.0, 1.0, -ratio, ratio, -20, 20 );

  return 0;
}

void draw_screen(const VIEW_STATE &vs) {
  double asp = (double)vs.width / (double)vs.height;

  while (myflags.model_lock != 0) {
    std::this_thread::sleep_for(std::chrono::minutes(30));
  }
  myflags.model_lock = 1;

  /* ビューポートを設定 */
  glViewport(0, 0, vs.width, vs.height);

  /* 色・デプスバッファを消去 */
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  /*ビュー設定*/
  glLoadIdentity();
  glOrtho(-vs.scale * asp, vs.scale * asp, -vs.scale, vs.scale, -20, 20);

  /* z 軸の方向に下げる */
  glTranslatef(0.0, -10.0, 0.0);
  /* 回転移動 */
  glMultMatrixd(vs.rt);
  glTranslatef(vs.move[0], vs.move[1], vs.move[2]);

  /*座標軸描画*/
  glBegin(GL_LINES);
  if (0 != (vs.show_axis & 0x02)) { // y_axis
    glColor4f(0.0, 1.0, 0.0, 1.0);
    glVertex3f(0.0, 0.0, 0.0);
    glVertex3f(0.0, 40.0, 0.0);
  }
  if (0 != (vs.show_axis & 0x01)) { // x_axis
    glColor4f(1.0, 0.0, 0.0, 1.0);
    glVertex3f(40.0, 0.0, 0.0);
    glVertex3f(-40.0, 0.0, 0.0);
  }
  if (0 != (vs.show_axis & 0x04)) { // z_axis
    glColor4f(0.0, 0.0, 1.0, 1.0);
    glVertex3f(0.0, 0.0, 40.0);
    glVertex3f(0.0, 0.0, -40.0);
  }
  glEnd();

  render_model(myflags.current_model);

  glFinish();
  myflags.model_lock = 0;
}

/*描画用のモデルを管理する関数*/
// struct MODEL;
// void model_mgr(Mode flag, int num, void *p) {
//   static std::shared_ptr<MODEL> model[16];
//   static int init = 1;
//
//   /*
//   num
//   0:表示
//   */
//   if (flag == Mode::Init) {
//     for (int i = 0; i < 16; i++) {
//       model[i] = MODEL::create();
//       make_dsp_model(model[i].get(), i);
//     }
//     init = 1;
//   } else if (flag == Mode::Write) {
//     init = -1;
//     *model[num] = *((MODEL *)p);
//     make_dsp_model(model[num].get(), num);
//     init = 1;
//   } else if (flag == Mode::Read) {
//     if (init == 1) {
//       load_tex(model[num].get(), num);
//       init = 0;
//     } else if (init == -1) {
//       // return NULL;
//     }
//     // return &model[num];
//   } else if (flag == Mode::Reset) {
//     init = -1;
//     *model[num] = *((MODEL *)p);
//     make_dsp_model(model[num].get(), num);
//     init = 0;
//   }
//   // return 0;
// }
