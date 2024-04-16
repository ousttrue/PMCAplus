#include <thread>

#include "PMCA_glfw.h"
#include "PMCA_renderer.h"
#include "quat.h"

#include <GLFW/glfw3.h>

#define WM_TITLE "PMCA 3D View"
#define SCALE (2.0 * 3.14159265358979323846)

static void key_callback(GLFWwindow *window, int key, int scancode, int action,
                         int mods) {
  if (key == GLFW_KEY_ESCAPE && action == GLFW_PRESS) {
    myflags.quit = 1;
  }
}

VIEW_STATE vs;

static void cursor_position_callback(GLFWwindow *window, double xpos,
                                     double ypos) {

  if (myflags.button1) {
    auto dx = static_cast<double>(xpos - vs.x);
    auto dy = static_cast<double>(ypos - vs.y);
    auto a = sqrt(dx * dx + dy * dy);
    if (a != 0.0) {
      double tmp[3];
      tmp[0] = dx * 0.1;
      tmp[1] = dy * 0.1;
      tmp[2] = 0.0;
      // 変換行列から移動ベクトルを回転
      for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
          if (i == 0) {
            vs.move[i] += tmp[j] * vs.rt[j * 4 + i];
          } else {
            vs.move[i] -= tmp[j] * vs.rt[j * 4 + i];
          }
        }
      }
    }
  }
  if (myflags.button2 == 1) {
    auto dx = static_cast<double>(xpos - vs.sx);
    auto dy = static_cast<double>(ypos - vs.sy);
    dx /= vs.width;
    dy /= vs.height;
    auto a = sqrt(dx * dx + dy * dy);
    if (a != 0.0) {
      // マウスのドラッグに伴う回転のクォータニオン dq を求める
      double ar = a * SCALE * 0.5;
      double as = sin(ar) / a;
      double dq[4] = {cos(ar), dy * as, dx * as, 0.0};

      // 回転の初期値 cq に dq を掛けて回転を合成
      qmul(vs.tq, dq, vs.cq);

      // クォータニオンから回転の変換行列を求める
      qrot(vs.rt, vs.tq);
    }
  }

  if (myflags.button3 == 1) {
    // auto dx = static_cast<double>(xpos - vs.x);
    auto dy = static_cast<double>(ypos - vs.y);
    vs.scale -= dy * 0.1;
    if (vs.scale < 0) {
      vs.scale = 0.001;
    }
  }

  vs.x = xpos;
  vs.y = ypos;
}

static void mouse_button_callback(GLFWwindow *window, int button, int action,
                                  int mods) {
  if (action == GLFW_PRESS) {
    switch (button) {
    case GLFW_MOUSE_BUTTON_LEFT:
      myflags.button1 = 1;
      break;
    case GLFW_MOUSE_BUTTON_RIGHT:
      myflags.button2 = 1;
      break;
    case GLFW_MOUSE_BUTTON_MIDDLE:
      myflags.button3 = 1;
      break;
    }
    vs.sx = vs.x;
    vs.sy = vs.y;
  } else if (action == GLFW_RELEASE) {
    switch (button) {
    case GLFW_MOUSE_BUTTON_LEFT:
      myflags.button1 = 0;
      break;
    case GLFW_MOUSE_BUTTON_RIGHT:
      myflags.button2 = 0;
      break;
    case GLFW_MOUSE_BUTTON_MIDDLE:
      myflags.button3 = 0;
      break;
    }
    memcpy(vs.cq, vs.tq, 4 * sizeof(double));
  }
}

static void scroll_callback(GLFWwindow *window, double xoffset,
                            double yoffset) {}

static int viewer_thread() {
  myflags.model_lock = 0;

  /* Initialize the library */
  if (!glfwInit()) {
    return -1;
  }

  /* Create a windowed mode window and its OpenGL context */
  auto window = glfwCreateWindow(640, 480, WM_TITLE, NULL, NULL);
  if (!window) {
    glfwTerminate();
    return -1;
  }

  glfwSetCursorPosCallback(window, cursor_position_callback);
  glfwSetMouseButtonCallback(window, mouse_button_callback);
  glfwSetKeyCallback(window, key_callback);
  glfwSetScrollCallback(window, scroll_callback);

  /* Make the window's context current */
  glfwMakeContextCurrent(window);

  setup_opengl();

  /* Loop until the user closes the window */
  while (!glfwWindowShouldClose(window)) {
    /* Poll for and process events */
    glfwPollEvents();

    glfwGetFramebufferSize(window, &vs.width, &vs.height);

    /* Render here */
    /*座標軸表示*/
    vs.show_axis = 0x01 | 0x02 | 0x04;
    draw_screen(vs);

    /* Swap front and back buffers */
    glfwSwapBuffers(window);
  }

  glfwTerminate();

  return 0;
}

//
// python export
//

std::thread g_thread;

PyObject *CreateViewerThread(PyObject *self, PyObject *args) {
  g_thread = std::thread([]() { viewer_thread(); });
  Py_RETURN_NONE;
}

PyObject *WaitViewerThread(PyObject *self, PyObject *args) {
  g_thread.join();
  Py_RETURN_NONE;
}

PyObject *QuitViewerThread(PyObject *self, PyObject *args) {
  myflags.quit = 1;
  g_thread.join();
  Py_RETURN_NONE;
}

PyObject *KillViewerThread(PyObject *self, PyObject *args) {
  g_thread.detach();
  Py_RETURN_NONE;
}

PyObject *GetViewerThreadState(PyObject *self, PyObject *args) {
  return Py_BuildValue("i", myflags.quit);
}

PyObject *show3Dview(PyObject *self, PyObject *args) {
  if (myflags.quit == 1) {
    g_thread = std::thread([]() { viewer_thread(); });
  }
  Py_RETURN_NONE;
}
