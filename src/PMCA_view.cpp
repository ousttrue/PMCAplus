#define PMCA_BUILD

extern "C" {
#include "PMCA_view.h"
#include "dbg.h"
#include "dsp.h"
#include "mlib_PMD_rw01.h"
#include "quat.h"
}

#include <GL/GL.h>
#include <GL/GLU.h>
#include <GLFW/glfw3.h>
#include <Windows.h>
#include <math.h>
#include <stb_image.h>

#include <mutex>
#include <thread>

static std::mutex mtx_;
static struct MODEL g_model;
static int g_copy = 0;
void view_model_copy(struct MODEL *src) {
  std::lock_guard<std::mutex> lock(mtx_);
  delete_PMD(&g_model);
  copy_PMD(&g_model, src);
  ++g_copy;
}

std::thread viewer_th;

static struct DSP_MODEL g_dsp_model;

#define SCALE (2.0 * 3.14159265358979323846)
#define WM_TITLE "PMCA 3D View"

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

static int setup_opengl() {

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

  {
    double tmp[4] = {1.0, 0.0, 0.0, 0.0};
    memcpy(vs.tq, tmp, 4 * sizeof(double));
    memcpy(vs.cq, tmp, 4 * sizeof(double));
    qrot(vs.rt, vs.tq);
    vs.scale = 15.0;
  }

  return 0;
}

// テクスチャ読み込み
static int load_tex(struct MODEL *model, struct DSP_MODEL *dsp_model) {
  auto mats = dsp_model->mats;
  if (dsp_model->mats_c != model->mat_count) {
    return -1;
  }

  glDeleteTextures(model->mat_count, dsp_model->texid);

  for (int i = 0; i < dsp_model->mats_c; i++) {
    for (int j = 0; j < 3; j++) {
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
          for (int j = 0; j < floor(log_w); j++) {
            w = w * 2;
          }
          for (int j = 0; j < floor(log_h); j++) {
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

  for (int i = 0; i < model->mat_count; i++) {
    if (mats[i].texbits != NULL) {
      glBindTexture(GL_TEXTURE_2D, dsp_model->texid[i]);
    }
  }

  return 0;
}

/*モデルデータを描画*/
static void render_model() {
  if (g_copy) {
    std::lock_guard<std::mutex> lock(mtx_);
    make_dsp_model(&g_model, &g_dsp_model);
    load_tex(&g_model, &g_dsp_model);
    g_copy = 0;
  }

  auto model = &g_model;
  auto dsp = &g_dsp_model;

  auto loc = dsp->loc;
  auto nor = dsp->nor;
  auto uv = dsp->uv;
  auto mats = dsp->mats;

  if (loc == NULL)
    return;
  if (nor == NULL)
    return;
  if (uv == NULL)
    return;
  if (mats == NULL)
    return;

  int c = 0;
  for (int i = 0; i < model->mat_count; i++) {
    if (mats[i].texbits != NULL) {
      glEnable(GL_TEXTURE_2D);
      // glBindTexture(GL_TEXTURE_2D , dsp->texid[i]);

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
    }

    glEnd();
    glDisable(GL_TEXTURE_2D);
  }
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

  render_model();
  glFinish();
}

static void createwindow() {
  if (!glfwInit()) {
    return;
  }

  auto window = glfwCreateWindow(640, 480, WM_TITLE, NULL, NULL);
  if (!window) {
    glfwTerminate();
    return;
  }
  glfwMakeContextCurrent(window);

  setup_opengl();

  while (myflags.quit != 1 && !glfwWindowShouldClose(window)) {
    glfwPollEvents();
    int w, h;
    glfwGetFramebufferSize(window, &w, &h);
    draw_screen(w, h);
    glfwSwapBuffers(window);
  }

  glfwTerminate();
}

void view_begin() {
  create_PMD(&g_model);
  g_copy = 1;
  viewer_th = std::thread(&createwindow);
}

void view_end() {
  myflags.quit = 1;
  viewer_th.join();
}
