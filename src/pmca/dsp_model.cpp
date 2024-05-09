#include <Windows.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include "dsp_model.h"
#include "mPMD.h"
#include <GL/GL.h>
#include <stdint.h>
#include <vector>

struct DSP_MAT {
  float col[4];
  char texname[128];
  int width = 0;
  int height = 0;
  std::vector<int8_t> texbits;
};

struct DSP_MODEL {
  std::vector<float> loc;
  std::vector<float> nor;
  std::vector<float> uv;
  std::vector<uint32_t> index;
  std::vector<DSP_MAT> mats;
  std::vector<uint32_t> texid;

  void make(const std::shared_ptr<MODEL> &model) {

    // auto loc = (float *)MALLOC(model->vt.size() * 3 * sizeof(float));
    // auto nor = (float *)MALLOC(model->vt.size() * 3 * sizeof(float));
    // auto uv = (float *)MALLOC(model->vt.size() * 2 * sizeof(float));
    // auto mats = (DSP_MAT *)MALLOC(model->mat.size() * sizeof(DSP_MAT));
    // memset(mats, 0, model->mat.size() * sizeof(DSP_MAT));
    // auto texid = (GLuint *)MALLOC(model->mat.size() * sizeof(GLuint));
    // if (loc == NULL || nor == NULL || uv == NULL || mats == NULL) {
    //   // myflags.model_lock=0;
    //   return -1;
    // }
    // dsp_model->loc = loc;
    // dsp_model->nor = nor;
    // dsp_model->uv = uv;
    // dsp_model->mats = mats;
    // dsp_model->texid = texid;
    // dsp_model->mats_c = model->mat.size();
    //
    // for (int i = 0; i < model->vt.size(); i++) {
    //   memcpy(loc, model->vt[i].loc, 2 * sizeof(float));
    //   loc += 2;
    //   *loc = -model->vt[i].loc[2];
    //   memcpy(nor, model->vt[i].nor, 3 * sizeof(float));
    //   memcpy(uv, model->vt[i].uv, 2 * sizeof(float));
    //   loc++;
    //   nor += 3;
    //   uv += 2;
    // }
    //
    // for (int i = 0; i < dsp_model->mats_c; i++) {
    //   dsp_model->mats[i].texbits = NULL;
    //   memset(dsp_model->mats[i].texsize, 0, 2 * sizeof(int));
    // }
    //
    // // myflags.model_lock=0;
  }
};

// テクスチャ読み込み
int load_tex(MODEL *model, int i) {
  //   if (dsp_model->mats_c != model->mat.size()) {
  //     return -1;
  //   }
  //
  //   glDeleteTextures(model->mat.size(), dsp_model->texid);
  //
  //   for (int i = 0; i < dsp_model->mats_c; i++) {
  //     auto &mat = dsp_model->mats[i];
  //     for (int j = 0; j < 3; j++) {
  //       LOGD << model->mat[i].diffuse[j] << " " <<
  //       model->mat[i].mirror_col[j]
  //            << " " << model->mat[i].spec_col[j];
  //       mat.col[j] =
  //           (model->mat[i].diffuse[j] * 2 + model->mat[i].mirror_col[j])
  //           / 2.5 + model->mat[i].spec_col[j] / 4;
  //     }
  //     LOGD << "col " << mat.col[0] << " " << mat.col[1] << " " << mat.col[2]
  //          << " " << mat.col[3];
  //     mat.col[3] = model->mat[i].alpha;
  //     mat.texname[0] = '\0';
  //     memset(mat.texsize, 0, 2 * sizeof(int));
  //     if (mat.texbits != NULL) {
  //       FREE(mat.texbits);
  //       mat.texbits = NULL;
  //     }
  //
  //     // STBIDEF stbi_uc *stbi_load            (char const *filename, int *x,
  //     int
  //     // *y, int *channels_in_file, int desired_channels);
  //     auto texbits = stbi_load(model->mat[i].tex_path, &mat.texsize[0],
  //                              &mat.texsize[1], nullptr, 4);
  //     // image = IMG_Load(model->mat[i].tex_path);
  //     // GLubyte *texbits = NULL;
  //     if (texbits == NULL) {
  //       memset(mat.texsize, 0, 2 * sizeof(int));
  //       texbits = NULL;
  //       printf("画像が読み込めません %s\n", model->mat[i].tex_path);
  //     } else {
  //       double log_w = log(mat.texsize[0]) / log(2);
  //       double log_h = log(mat.texsize[1]) / log(2);
  //       if (ceil(log_w) != floor(log_w) || ceil(log_h) != floor(log_h)) {
  //         GLubyte *tmp_bits;
  //         int w, h;
  //         w = 2;
  //         h = 2;
  //         for (int j = 0; j < floor(log_w); j++) {
  //           w = w * 2;
  //         }
  //         for (int j = 0; j < floor(log_h); j++) {
  //           h = h * 2;
  //         }
  //         tmp_bits = (GLubyte *)MALLOC(h * w * sizeof(GLubyte) * 6);
  //         if (tmp_bits == NULL) {
  //           LOGE << "メモリ確保失敗";
  //         }
  //
  //         auto tmp = gluScaleImage(GL_RGBA, mat.texsize[0], mat.texsize[1],
  //                                  GL_UNSIGNED_BYTE, texbits, w, h,
  //                                  GL_UNSIGNED_BYTE, tmp_bits);
  //         mat.texsize[0] = w;
  //         mat.texsize[1] = h;
  // #ifdef DEBUG
  //         printf("log %f x %f\n", log_w, log_h);
  //         printf("リサイズ %d x %d  %x %s\n", w, h, tmp,
  //         gluErrorString(tmp));
  // #endif
  //         // FREE(texbits);
  //         stbi_image_free(texbits);
  //         texbits = tmp_bits;
  //       }
  //     }
  //     mat.texbits = texbits;
  //   }
  //   glGenTextures(model->mat.size(), dsp_model->texid);
  //
  //   for (int i = 0; i < model->mat.size(); i++) {
  //     if (dsp_model->mats[i].texbits != NULL) {
  //       glBindTexture(GL_TEXTURE_2D, dsp_model->texid[i]);
  //     }
  //   }
  //
  //   // myflags.model_lock=0;
  //
  return 0;
}

/*モデルデータを描画*/
void render_model(const std::shared_ptr<MODEL> &model) {
  if (!model) {
    return;
  }

  static DSP_MODEL s_dsp;
  static std::shared_ptr<MODEL> s_last;
  if (s_last != model) {
    s_last = model;
    s_dsp.make(model);
  }

  // auto loc = s_dsp.loc.data();
  // auto uv = s_dsp.uv.data();

  int c = 0;
  for (int i = 0; i < model->mat.size(); i++) {
    // if (s_dsp.mats[i].texbits.size()) {
    //     glEnable(GL_TEXTURE_2D);
    //     // glBindTexture(GL_TEXTURE_2D , dsp_model->texid[i]);
    //
    //     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    //     glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    //     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    //     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    //
    //     glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, mats[i].texsize[0],
    //                  mats[i].texsize[1], 0, GL_RGBA, GL_UNSIGNED_BYTE,
    //                  mats[i].texbits);
    // }

    glBegin(GL_TRIANGLES);
    // glColor4fv(s_dsp.mats[i].col);

    for (int j = 0; j < model->mat[i].vt_index_count; j++) {
      auto index = model->vt_index[c++];
      auto v = model->vt[index];
      glTexCoord2fv(v.uv);
      glVertex3fv(v.loc);
    }

    glEnd();
    glDisable(GL_TEXTURE_2D);
  }

  // glDeleteTextures(model->mat_count, dsp_model->texid);
}

// void model_set(int num, MODEL *p) {}
