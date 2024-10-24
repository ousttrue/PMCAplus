#include <memory.h>

#include "mPMD.h"
#define SCALE (2.0 * 3.14159265358979323846)
#define MODEL_COUNT 16

typedef struct {
  float col[4];
  char texname[128];
  int texsize[2];
  unsigned char *texbits;
} DSP_MAT;

typedef struct {
  float *loc;
  float *nor;
  float *uv;
  // unsigned int *index;
  int mats_c;
  DSP_MAT *mats;
  unsigned int *texid;
} DSP_MODEL;

typedef struct {
  int button1;
  int button2;
  int button3;
  int model_lock;
  int quit;
} FLAGS;

typedef struct {
  /* EBhE@ */
  int width;
  int height;

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
} VIEW_STATE;

/*****************************************************************/
/*PMDr[AA*/
int viewer_thread(void *);
void quit(int code);
void qmul(double r[], const double p[], const double q[]);
void qrot(double r[], double q[]);
void *model_mgr(int flag, int num, void *p);
int render_model(int num);
int load_texture(struct MODEL *model);
int load_tex(struct MODEL *model, DSP_MODEL *dsp_model);
int make_dsp_model(struct MODEL *model, DSP_MODEL *dsp_model);

extern FLAGS myflags;

/*****************************************************************/
extern struct MODEL g_model[16];
extern struct LIST list;
