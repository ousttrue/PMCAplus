#define PMCA_BUILD

extern "C" {
#include "PMCA_view.h"
#include "dbg.h"
#include "mlib_PMD_rw01.h"
}

#include <GL/GL.h>
#include <GL/GLU.h>
#include <GLFW/glfw3.h>
#include <Windows.h>
#include <math.h>
#include <stb_image.h>

#include <mutex>
#include <thread>

#define SCALE (2.0 * 3.14159265358979323846)
#define WM_TITLE "PMCA 3D View"

std::thread viewer_th;
std::mutex mtx_;

/*
** クォータニオンの積 r <- p x q
*/
static void qmul(double r[], const double p[], const double q[]) {
  r[0] = p[0] * q[0] - p[1] * q[1] - p[2] * q[2] - p[3] * q[3];
  r[1] = p[0] * q[1] + p[1] * q[0] + p[2] * q[3] - p[3] * q[2];
  r[2] = p[0] * q[2] - p[1] * q[3] + p[2] * q[0] + p[3] * q[1];
  r[3] = p[0] * q[3] + p[1] * q[2] - p[2] * q[1] + p[3] * q[0];
}

/*
** 回転の変換行列 r <- クォータニオン q
*/
static void qrot(double r[], double q[]) {
  double x2 = q[1] * q[1] * 2.0;
  double y2 = q[2] * q[2] * 2.0;
  double z2 = q[3] * q[3] * 2.0;
  double xy = q[1] * q[2] * 2.0;
  double yz = q[2] * q[3] * 2.0;
  double zx = q[3] * q[1] * 2.0;
  double xw = q[1] * q[0] * 2.0;
  double yw = q[2] * q[0] * 2.0;
  double zw = q[3] * q[0] * 2.0;

  r[0] = 1.0 - y2 - z2;
  r[1] = xy + zw;
  r[2] = zx - yw;
  r[4] = xy - zw;
  r[5] = 1.0 - z2 - x2;
  r[6] = yz + xw;
  r[8] = zx + yw;
  r[9] = yz - xw;
  r[10] = 1.0 - x2 - y2;
  r[3] = r[7] = r[11] = r[12] = r[13] = r[14] = 0.0;
  r[15] = 1.0;
}

struct DSP_MAT {
  float col[4];
  char texname[128];
  int texsize[2];
  unsigned char *texbits;
};

struct DSP_MODEL {
  float *loc;
  float *nor;
  float *uv;
  // unsigned int *index;
  int mats_c;
  struct DSP_MAT *mats;
  unsigned int *texid;
};

struct FLAGS {
  int button1;
  int button2;
  int button3;
  int quit;
};

struct FLAGS myflags;

struct VIEW_STATE {
  /*NbNJ[\W*/
  int sx;
  int sy;

  /*fr[]*/
  double rt[16];
  double cq[4];
  double tq[4];

  /*s*/
  double move[3];

  /*TCY*/
  double scale;

  /*\*/
  int show_axis;
};

struct VIEW_STATE vs;

static int setup_opengl(int width, int height) {

  /* シェーディングモデルは Gouraud (なめらか) */
  // glShadeModel( GL_SMOOTH );

  /* 裏面を取り除く */
  glEnable(GL_CULL_FACE);
  glFrontFace(GL_CCW);
  glCullFace(GL_FRONT);

  /* 消去時の色をセット */
  glClearColor(0, 0, 0, 0);

  /* ビューポートを設定 */
  glViewport(0, 0, width, height);

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

  {
    double tmp[4] = {1.0, 0.0, 0.0, 0.0};
    memcpy(vs.tq, tmp, 4 * sizeof(double));
    memcpy(vs.cq, tmp, 4 * sizeof(double));
    qrot(vs.rt, vs.tq);
    vs.scale = 15.0;
  }

  return 0;
}

/*モデルデータを描画*/
static int render_model(int num) {
  auto model = reinterpret_cast<MODEL *>(model_mgr(1, num, NULL));
  if (model == NULL)
    return -1;
  auto dsp_model = reinterpret_cast<DSP_MODEL *>(model_mgr(2, num, NULL));

  auto loc = dsp_model->loc;
  auto nor = dsp_model->nor;
  auto uv = dsp_model->uv;
  auto mats = dsp_model->mats;

  if (loc == NULL)
    return -1;
  if (nor == NULL)
    return -1;
  if (uv == NULL)
    return -1;
  if (mats == NULL)
    return -1;

  int c = 0;
  for (int i = 0; i < model->mat_count; i++) {
    if (mats[i].texbits != NULL) {
      glEnable(GL_TEXTURE_2D);
      // glBindTexture(GL_TEXTURE_2D , dsp_model->texid[i]);

      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

      struct DSP_MAT *mat = &mats[i];
      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, mats[i].texsize[0],
                   mats[i].texsize[1], 0, GL_RGBA, GL_UNSIGNED_BYTE,
                   mats[i].texbits);
    }
    glBegin(GL_TRIANGLES);
    glColor4fv(mats[i].col);

    for (int j = 0; j < model->mat[i].vt_index_count; j++) {
      int index = model->vt_index[c++];
      glTexCoord2fv(uv + 2 * index);
      glVertex3fv(loc + 3 * index);
      /*
      glTexCoord2fv(model->vt[index].uv);
      glVertex3fv(model->vt[index].loc);
      */
      // c++;
    }

    glEnd();
    glDisable(GL_TEXTURE_2D);
  }
  /*
  GLenum num;
  num = glGetError;
  */
  // glDeleteTextures(model->mat_count, dsp_model->texid);
  return 0;
}

static void draw_screen(int w, int h) {
  double asp = (double)w / (double)h;

  /*座標軸表示*/
  vs.show_axis = 0x01 | 0x02 | 0x04;

  /* 色・デプスバッファを消去 */
  glViewport(0, 0, w, h);
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

  render_model(0);
  glFinish();
  // SDL_GL_SwapBuffers();
  // SDL_Delay(30);
}

// static void handle_key_down(SDL_keysym *keysym) {
//   switch (keysym->sym) {
//   case SDLK_ESCAPE:
//     myflags.quit = 1;
//     break;
//   default:
//     break;
//   }
// }

// static void process_events(void) {
//   /* SDL イベントの置き場 */
//   SDL_Event event;
//
//   /* すべてのイベントをキューからつかみ取る */
//   while (SDL_PollEvent(&event)) {
//
//     switch (event.type) {
//     case SDL_KEYDOWN:
//       /* キー押下を処理 */
//       handle_key_down(&event.key.keysym);
//       break;
//     case SDL_MOUSEBUTTONDOWN:
//       switch (event.button.button) {
//       case SDL_BUTTON_LEFT:
//         myflags.button1 = 1;
//         break;
//       case SDL_BUTTON_RIGHT:
//         myflags.button2 = 1;
//         break;
//       case SDL_BUTTON_MIDDLE:
//         myflags.button3 = 1;
//         break;
//       }
//       vs.sx = event.button.x;
//       vs.sy = event.button.y;
//       break;
//     case SDL_MOUSEBUTTONUP:
//       switch (event.button.button) {
//       case SDL_BUTTON_LEFT:
//         myflags.button1 = 0;
//         break;
//       case SDL_BUTTON_RIGHT:
//         myflags.button2 = 0;
//         break;
//       case SDL_BUTTON_MIDDLE:
//         myflags.button3 = 0;
//         break;
//       }
//       memcpy(vs.cq, vs.tq, 4 * sizeof(double));
//       break;
//     case SDL_MOUSEMOTION:
//       if (myflags.button1 == 1) {
//         double dx, dy;
//         double a;
//         dx = (event.motion.xrel) / 10.0;
//         dy = (event.motion.yrel) / 10.0;
//         a = sqrt(dx * dx + dy * dy);
//         if (a != 0.0) {
//           int i, j;
//           double tmp[3];
//           tmp[0] = dx;
//           tmp[1] = dy;
//           tmp[2] = 0.0;
//           // 変換行列から移動ベクトルを回転
//           for (i = 0; i < 3; i++) {
//             for (j = 0; j < 3; j++) {
//               if (i == 0) {
//                 vs.move[i] += tmp[j] * vs.rt[j * 4 + i];
//               } else {
//                 vs.move[i] -= tmp[j] * vs.rt[j * 4 + i];
//               }
//             }
//           }
//         }
//       }
//       if (myflags.button2 == 1) {
//         double dx, dy;
//         double a;
//
//         dx = (event.motion.x - vs.sx) / (double)vs.width;
//         dy = (event.motion.y - vs.sy) / (double)vs.height;
//         a = sqrt(dx * dx + dy * dy);
//         if (a != 0.0) {
//           // マウスのドラッグに伴う回転のクォータニオン dq を求める
//           double ar = a * SCALE * 0.5;
//           double as = sin(ar) / a;
//           double dq[4] = {cos(ar), dy * as, dx * as, 0.0};
//
//           // 回転の初期値 cq に dq を掛けて回転を合成
//           qmul(vs.tq, dq, vs.cq);
//
//           // クォータニオンから回転の変換行列を求める
//           qrot(vs.rt, vs.tq);
//         }
//       }
//       if (myflags.button3 == 1) {
//         vs.scale -= event.motion.yrel * 0.1;
//         if (vs.scale < 0) {
//           vs.scale = 0.001;
//         }
//       }
//       break;
//     case SDL_VIDEORESIZE:
//       vs.width = event.resize.w;
//       vs.height = event.resize.h;
//       if (SDL_SetVideoMode(vs.width, vs.height, bpp, flags) == 0) {
//         fprintf(stderr, "ビデオモードのセットに失敗しました: %s\n",
//                 SDL_GetError());
//         SDL_Quit();
//         return;
//       }
//       setup_opengl(vs.width, vs.height);
//       break;
//     case SDL_QUIT:
//       /* 終了要求 (Ctrl-c など) を処理 */
//       myflags.quit = 1;
//
//       return;
//     }
//   }
// }

static int createwindow() {
  if (!glfwInit())
    return -1;

  auto window = glfwCreateWindow(640, 480, WM_TITLE, NULL, NULL);
  if (!window) {
    glfwTerminate();
    return -1;
  }

  glfwMakeContextCurrent(window);

  int w, h;
  glfwGetFramebufferSize(window, &w, &h);

  setup_opengl(w, h);

  while (myflags.quit != 1 && !glfwWindowShouldClose(window)) {
    /* Poll for and process events */
    glfwPollEvents();

    glfwGetFramebufferSize(window, &w, &h);
    // process_events();
    draw_screen(w, h);
    /* Swap front and back buffers */
    glfwSwapBuffers(window);
  }

  glfwTerminate();
  return 0;
}

// int (SDLCALL *fn)(void *)
static void viewer_thread() { createwindow(); }

static int make_dsp_model(struct MODEL *model, struct DSP_MODEL *dsp_model) {
  FREE(dsp_model->loc);
  FREE(dsp_model->nor);
  FREE(dsp_model->uv);
  for (int i = 0; i < dsp_model->mats_c; i++) {
    FREE(dsp_model->mats[i].texbits);
    dsp_model->mats[i].texbits = NULL;
    memset(dsp_model->mats[i].texsize, 0, 2 * sizeof(int));
  }
  FREE(dsp_model->mats);
  FREE(dsp_model->texid);
  dsp_model->loc = NULL;
  dsp_model->nor = NULL;
  dsp_model->uv = NULL;
  dsp_model->mats = NULL;
  dsp_model->texid = NULL;

  auto loc =
      reinterpret_cast<float *>(MALLOC(model->vt_count * 3 * sizeof(float)));
  auto nor =
      reinterpret_cast<float *>(MALLOC(model->vt_count * 3 * sizeof(float)));
  auto uv =
      reinterpret_cast<float *>(MALLOC(model->vt_count * 2 * sizeof(float)));
  auto mats = reinterpret_cast<DSP_MAT *>(
      MALLOC(model->mat_count * sizeof(struct DSP_MAT)));
  memset(mats, 0, model->mat_count * sizeof(struct DSP_MAT));
  auto texid =
      reinterpret_cast<GLuint *>(MALLOC(model->mat_count * sizeof(GLuint)));
  if (loc == NULL || nor == NULL || uv == NULL || mats == NULL) {
    // myflags.model_lock=0;
    return -1;
  }
  dsp_model->loc = loc;
  dsp_model->nor = nor;
  dsp_model->uv = uv;
  dsp_model->mats = mats;
  dsp_model->texid = texid;
  dsp_model->mats_c = model->mat_count;

  for (int i = 0; i < model->vt_count; i++) {
    memcpy(loc, model->vt[i].loc, 2 * sizeof(float));
    loc += 2;
    *loc = -model->vt[i].loc[2];
    memcpy(nor, model->vt[i].nor, 3 * sizeof(float));
    memcpy(uv, model->vt[i].uv, 2 * sizeof(float));
    loc++;
    nor += 3;
    uv += 2;
  }

  for (int i = 0; i < dsp_model->mats_c; i++) {
    dsp_model->mats[i].texbits = NULL;
    memset(dsp_model->mats[i].texsize, 0, 2 * sizeof(int));
  }

  // myflags.model_lock=0;
  return 0;
}

// テクスチャ読み込み
static int load_tex(struct MODEL *model, struct DSP_MODEL *dsp_model) {
  struct DSP_MAT *mats;
  int i, j;
  /*
  while(myflags.model_lock != 0){
          SDL_Delay(30);
  }
  myflags.model_lock=1;
  */

  mats = dsp_model->mats;

  if (dsp_model->mats_c != model->mat_count) {
    return -1;
  }

  glDeleteTextures(model->mat_count, dsp_model->texid);

  for (i = 0; i < dsp_model->mats_c; i++) {
    for (j = 0; j < 3; j++) {
      mats[i].col[j] =
          (model->mat[i].diffuse[j] * 2 + model->mat[i].mirror_col[j]) / 2.5 +
          model->mat[i].spec_col[j] / 4;
    }
    mats[i].col[3] = model->mat[i].alpha;
    mats[i].texname[0] = '\0';
    memset(mats[i].texsize, 0, 2 * sizeof(int));
    if (mats[i].texbits != NULL) {
      FREE(mats[i].texbits);
      mats[i].texbits = NULL;
    }

    int w, h, ch;
    mats[i].texbits = stbi_load(model->mat[i].tex_path, &w, &h, &ch, 4);

    if (mats[i].texbits != NULL) {
      mats[i].texsize[0] = w;
      mats[i].texsize[1] = h;
      {
        double log_w = log(mats[i].texsize[0]) / log(2);
        double log_h = log(mats[i].texsize[1]) / log(2);
        if (ceil(log_w) != floor(log_w) || ceil(log_h) != floor(log_h)) {
          int w = 2;
          int h = 2;
          for (j = 0; j < floor(log_w); j++) {
            w = w * 2;
          }
          for (j = 0; j < floor(log_h); j++) {
            h = h * 2;
          }
          GLubyte *tmp_bits =
              reinterpret_cast<GLubyte *>(MALLOC(h * w * sizeof(GLubyte) * 6));
          if (tmp_bits == NULL)
            puts("メモリ確保失敗");

          int tmp = gluScaleImage(
              GL_RGBA, mats[i].texsize[0], mats[i].texsize[1], GL_UNSIGNED_BYTE,
              mats[i].texbits, w, h, GL_UNSIGNED_BYTE, tmp_bits);
          mats[i].texsize[0] = w;
          mats[i].texsize[1] = h;
          stbi_image_free(mats[i].texbits);
          mats[i].texbits = tmp_bits;
        }
      }
    } else {
      mats[i].texsize[0] = 0;
      mats[i].texsize[1] = 0;
      printf("画像が読み込めません %s\n", model->mat[i].tex_path);
    }
  }
  glGenTextures(model->mat_count, dsp_model->texid);

  for (i = 0; i < model->mat_count; i++) {
    if (mats[i].texbits != NULL) {
      glBindTexture(GL_TEXTURE_2D, dsp_model->texid[i]);
    }
  }

  return 0;
}

/*描画用のモデルを管理する関数*/
void *model_mgr(int flag, int num, void *p) {
  std::lock_guard<std::mutex> lock(mtx_);

  static struct MODEL model[16];
  static struct DSP_MODEL dsp_model[16];
  static int init = 1;

  int i;

  /*flag
  -1:初期化
  0:書き込み
  1:読み出し
  2:描画モデル読み出し
  3:テクスチャはそのままで再セット
  num
  0:表示
  */
  if (flag == -1) {
    for (i = 0; i < 16; i++) {
      create_PMD(&model[i]);
      make_dsp_model(&model[i], &dsp_model[i]);
    }
    init = 1;
  } else if (flag == 0) {
    init = -1;
    delete_PMD(&model[num]);
    copy_PMD(&model[num], (struct MODEL *)p);
    make_dsp_model(&model[num], &dsp_model[num]);
    init = 1;
  } else if (flag == 1) {
    // if(myflags.model_lock != 0)return NULL;
    if (init == 1) {
      load_tex(&model[num], &dsp_model[num]);
      init = 0;
    } else if (init == -1) {
      return NULL;
    }
    return &model[num];

  } else if (flag == 2) {
    return &dsp_model[num];

  } else if (flag == 3) {
    init = -1;
    delete_PMD(&model[num]);
    copy_PMD(&model[num], (struct MODEL *)p);
    make_dsp_model(&model[num], &dsp_model[num]);
    init = 0;
  }
  return 0;
}

DLL void CreateViewerThread() { viewer_th = std::thread(&viewer_thread); }

DLL void QuitViewerThread() {
  myflags.quit = 1;
  viewer_th.join();
}

DLL void MODEL_LOCK(int num) {
  // if (num == 1) {
  //   mtx_.lock(); // ロックを取得する
  // } else {
  //   mtx_.unlock(); // ロックを手放す
  // }
}
