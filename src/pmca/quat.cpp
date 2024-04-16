#include "quat.h"

/*
** クォータニオンの積 r <- p x q
*/
void qmul(double r[], const double p[], const double q[]) {
  r[0] = p[0] * q[0] - p[1] * q[1] - p[2] * q[2] - p[3] * q[3];
  r[1] = p[0] * q[1] + p[1] * q[0] + p[2] * q[3] - p[3] * q[2];
  r[2] = p[0] * q[2] - p[1] * q[3] + p[2] * q[0] + p[3] * q[1];
  r[3] = p[0] * q[3] + p[1] * q[2] - p[2] * q[1] + p[3] * q[0];
}

/*
** 回転の変換行列 r <- クォータニオン q
*/
void qrot(double r[], double q[]) {
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
