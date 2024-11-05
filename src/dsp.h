#pragma once

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

struct MODEL;
void make_dsp_model(struct MODEL *model, struct DSP_MODEL *dsp_model);
