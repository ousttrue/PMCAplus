#include "PMCA_renderer.h"
#include "mPMD.h"
#include "quat.h"
#include "dbg.h"

#include <Windows.h>

#include <GL/GL.h>
#include <GL/GLU.h>

#include <math.h>

#include <chrono>
#include <string.h>
#include <thread>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

FLAGS myflags;

struct MODEL;
struct DSP_MODEL;
int make_dsp_model(MODEL *model, DSP_MODEL *dsp_model);
int load_tex(MODEL *model, DSP_MODEL *dsp_model);
int render_model(int num);

VIEW_STATE::VIEW_STATE() {
  double tmp[4] = {1.0, 0.0, 0.0, 0.0};
  memcpy(this->tq, tmp, 4 * sizeof(double));
  memcpy(this->cq, tmp, 4 * sizeof(double));
  qrot(this->rt, this->tq);
  this->scale = 15.0;
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
  DSP_MAT *mats;
  unsigned int *texid;
};

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

  render_model(0);
  glFinish();
  myflags.model_lock = 0;
}

/*描画用のモデルを管理する関数*/
void *model_mgr(Mode flag, int num, void *p) {
  static MODEL model[16];
  static DSP_MODEL dsp_model[16];
  static int init = 1;

  /*
  num
  0:表示
  */
  if (flag == Mode::Init) {
    for (int i = 0; i < 16; i++) {
      create_PMD(&model[i]);
      make_dsp_model(&model[i], &dsp_model[i]);
    }
    init = 1;
  } else if (flag == Mode::Write) {
    init = -1;
    delete_PMD(&model[num]);
    copy_PMD(&model[num], (MODEL *)p);
    make_dsp_model(&model[num], &dsp_model[num]);
    init = 1;
  } else if (flag == Mode::Read) {
    // if(myflags.model_lock != 0)return NULL;
    if (init == 1) {
      load_tex(&model[num], &dsp_model[num]);
      init = 0;
    } else if (init == -1) {
      return NULL;
    }
    return &model[num];

  } else if (flag == Mode::ReadModel) {
    return &dsp_model[num];

  } else if (flag == Mode::Reset) {
    init = -1;
    delete_PMD(&model[num]);
    copy_PMD(&model[num], (MODEL *)p);
    make_dsp_model(&model[num], &dsp_model[num]);
    init = 0;
  }

  return 0;
}

/*モデルデータを描画*/
int render_model(int num) {
  int i, j;
  int index, c;

  static float *loc;
  static float *nor;
  static float *uv;
  static DSP_MAT *mats;

  auto model = (MODEL *)model_mgr(Mode::Read, num, NULL);
  if (model == NULL) {
    return -1;
  }

  auto dsp_model = (DSP_MODEL *)model_mgr(Mode::ReadModel, num, NULL);

  loc = dsp_model->loc;
  nor = dsp_model->nor;
  uv = dsp_model->uv;
  mats = dsp_model->mats;

  if (loc == NULL)
    return -1;
  if (nor == NULL)
    return -1;
  if (uv == NULL)
    return -1;
  if (mats == NULL)
    return -1;

  c = 0;
  for (i = 0; i < model->mat_count; i++) {
    if (mats[i].texbits != NULL) {
      glEnable(GL_TEXTURE_2D);
      // glBindTexture(GL_TEXTURE_2D , dsp_model->texid[i]);

      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, mats[i].texsize[0],
                   mats[i].texsize[1], 0, GL_RGBA, GL_UNSIGNED_BYTE,
                   mats[i].texbits);
    }
    glBegin(GL_TRIANGLES);
    glColor4fv(mats[i].col);

    for (j = 0; j < model->mat[i].vt_index_count; j++) {
      index = model->vt_index[c++];
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

// テクスチャ読み込み
int load_tex(MODEL *model, DSP_MODEL *dsp_model) {

  // DSP_MAT *mats;

  // char tex_name[128];
  // int i, j, tmp;
  // SDL_Surface *image = NULL;

  // mats = dsp_model->mats;

  if (dsp_model->mats_c != model->mat_count) {
    return -1;
  }

  glDeleteTextures(model->mat_count, dsp_model->texid);

  for (int i = 0; i < dsp_model->mats_c; i++) {
    auto &mat = dsp_model->mats[i];
    for (int j = 0; j < 3; j++) {
      printf("%f %f %f\n", model->mat[i].diffuse[j],
             model->mat[i].mirror_col[j], model->mat[i].spec_col[j]);
      mat.col[j] =
          (model->mat[i].diffuse[j] * 2 + model->mat[i].mirror_col[j]) / 2.5 +
          model->mat[i].spec_col[j] / 4;
    }
    printf("col %f %f %f %f\n", mat.col[0], mat.col[1], mat.col[2], mat.col[3]);
    mat.col[3] = model->mat[i].alpha;
    mat.texname[0] = '\0';
    memset(mat.texsize, 0, 2 * sizeof(int));
    if (mat.texbits != NULL) {
      FREE(mat.texbits);
      mat.texbits = NULL;
    }

    // STBIDEF stbi_uc *stbi_load            (char const *filename, int *x, int
    // *y, int *channels_in_file, int desired_channels);
    auto texbits = stbi_load(model->mat[i].tex_path, &mat.texsize[0],
                             &mat.texsize[1], nullptr, 4);
    // image = IMG_Load(model->mat[i].tex_path);
    // GLubyte *texbits = NULL;
    if (texbits == NULL) {
      memset(mat.texsize, 0, 2 * sizeof(int));
      texbits = NULL;
      printf("画像が読み込めません %s\n", model->mat[i].tex_path);
    } else {
      double log_w = log(mat.texsize[0]) / log(2);
      double log_h = log(mat.texsize[1]) / log(2);
      if (ceil(log_w) != floor(log_w) || ceil(log_h) != floor(log_h)) {
        GLubyte *tmp_bits;
        int w, h;
        w = 2;
        h = 2;
        for (int j = 0; j < floor(log_w); j++) {
          w = w * 2;
        }
        for (int j = 0; j < floor(log_h); j++) {
          h = h * 2;
        }
        tmp_bits = (GLubyte *)MALLOC(h * w * sizeof(GLubyte) * 6);
        if (tmp_bits == NULL)
          puts("メモリ確保失敗");

        auto tmp = gluScaleImage(GL_RGBA, mat.texsize[0], mat.texsize[1],
                                 GL_UNSIGNED_BYTE, texbits, w, h,
                                 GL_UNSIGNED_BYTE, tmp_bits);
        mat.texsize[0] = w;
        mat.texsize[1] = h;
#ifdef DEBUG
        printf("log %f x %f\n", log_w, log_h);
        printf("リサイズ %d x %d  %x %s\n", w, h, tmp, gluErrorString(tmp));
#endif
        // FREE(texbits);
        stbi_image_free(texbits);
        texbits = tmp_bits;
      }
    }
    mat.texbits = texbits;
  }
  glGenTextures(model->mat_count, dsp_model->texid);

  for (int i = 0; i < model->mat_count; i++) {
    if (dsp_model->mats[i].texbits != NULL) {
      glBindTexture(GL_TEXTURE_2D, dsp_model->texid[i]);
    }
  }

  // myflags.model_lock=0;

  return 0;
}

int make_dsp_model(MODEL *model, DSP_MODEL *dsp_model) {
  int i, j;
  float *loc;
  float *nor;
  float *uv;
  DSP_MAT *mats;
  GLuint *texid;
  // unsigned int index;

  /*
  while(myflags.model_lock != 0){
          SDL_Delay(30);
          printf("B");
  }
  myflags.model_lock=1;
  */
  FREE(dsp_model->loc);
  FREE(dsp_model->nor);
  FREE(dsp_model->uv);
  for (i = 0; i < dsp_model->mats_c; i++) {
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

  loc = (float *)MALLOC(model->vt_count * 3 * sizeof(float));
  nor = (float *)MALLOC(model->vt_count * 3 * sizeof(float));
  uv = (float *)MALLOC(model->vt_count * 2 * sizeof(float));
  mats = (DSP_MAT *)MALLOC(model->mat_count * sizeof(DSP_MAT));
  memset(mats, 0, model->mat_count * sizeof(DSP_MAT));
  texid = (GLuint *)MALLOC(model->mat_count * sizeof(GLuint));
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

  for (i = 0; i < model->vt_count; i++) {
    memcpy(loc, model->vt[i].loc, 2 * sizeof(float));
    loc += 2;
    *loc = -model->vt[i].loc[2];
    memcpy(nor, model->vt[i].nor, 3 * sizeof(float));
    memcpy(uv, model->vt[i].uv, 2 * sizeof(float));
    loc++;
    nor += 3;
    uv += 2;
  }

  for (i = 0; i < dsp_model->mats_c; i++) {
    dsp_model->mats[i].texbits = NULL;
    memset(dsp_model->mats[i].texsize, 0, 2 * sizeof(int));
  }

  // myflags.model_lock=0;
  return 0;
}
