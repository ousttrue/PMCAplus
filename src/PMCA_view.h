#pragma once
struct MODEL;
struct DSP_MODEL;

struct FLAGS {
  int button1;
  int button2;
  int button3;
  int model_lock;
  int quit;
};
extern struct FLAGS myflags;

int viewer_thread(void *);
void quit(int code);
void qmul(double r[], const double p[], const double q[]);
void qrot(double r[], double q[]);
void *model_mgr(int flag, int num, void *p);
int render_model(int num);
int load_texture(struct MODEL *model);
int load_tex(struct MODEL *model, struct DSP_MODEL *dsp_model);
int make_dsp_model(struct MODEL *model, struct DSP_MODEL *dsp_model);
