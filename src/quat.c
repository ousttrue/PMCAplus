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


