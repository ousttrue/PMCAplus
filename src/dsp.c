#include "dsp.h"
#include "dbg.h"
#include "dsp.h"
#include "mlib_PMD_rw01.h"
#include <string.h>

void make_dsp_model(struct MODEL *model, struct DSP_MODEL *dsp_model) {
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

  dsp_model->loc = (float *)MALLOC(model->vt_count * 3 * sizeof(float));
  dsp_model->nor = (float *)MALLOC(model->vt_count * 3 * sizeof(float));
  dsp_model->uv = (float *)MALLOC(model->vt_count * 2 * sizeof(float));
  dsp_model->mats =
      (struct DSP_MAT *)MALLOC(model->mat_count * sizeof(struct DSP_MAT));
  memset(dsp_model->mats, 0, model->mat_count * sizeof(struct DSP_MAT));
  dsp_model->texid =
      (unsigned int *)MALLOC(model->mat_count * sizeof(unsigned int));
  dsp_model->mats_c = model->mat_count;

  auto loc = dsp_model->loc;
  auto nor = dsp_model->nor;
  auto uv = dsp_model->uv;
  for (int i = 0; i < model->vt_count; i++, loc += 3, nor += 3, uv += 2) {
    memcpy(loc, model->vt[i].loc, 2 * sizeof(float));
    loc[2] = -model->vt[i].loc[2];
    memcpy(nor, model->vt[i].nor, 3 * sizeof(float));
    memcpy(uv, model->vt[i].uv, 2 * sizeof(float));
  }

  for (int i = 0; i < dsp_model->mats_c; i++) {
    dsp_model->mats[i].texbits = NULL;
    memset(dsp_model->mats[i].texsize, 0, 2 * sizeof(int));
  }
}
