#include <thread>

#include "PMCA_PyMod.h"
#include "PMCA_renderer.h"
#include "quat.h"

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <stdio.h>
#ifdef __APPLE__
#define GL_SILENCE_DEPRECATION
#endif

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
  auto window = glfwCreateWindow(1024, 768, WM_TITLE, NULL, NULL);
  if (!window) {
    glfwTerminate();
    return -1;
  }
  glfwMakeContextCurrent(window);

  glfwSwapInterval(1); // Enable vsync

  // Decide GL+GLSL versions
#if defined(IMGUI_IMPL_OPENGL_ES2)
                       // GL ES 2.0 + GLSL 100
  const char *glsl_version = "#version 100";
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
  glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
#elif defined(__APPLE__)
                       // GL 3.2 + GLSL 150
  const char *glsl_version = "#version 150";
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE); // 3.2+ only
  glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // Required on Mac
#else
                       // GL 3.0 + GLSL 130
  const char *glsl_version = "#version 130";
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
  // glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+
  // only glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // 3.0+ only
#endif

  // Setup Dear ImGui context
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImGuiIO &io = ImGui::GetIO();
  (void)io;
  io.ConfigFlags |=
      ImGuiConfigFlags_NavEnableKeyboard; // Enable Keyboard Controls
  io.ConfigFlags |=
      ImGuiConfigFlags_NavEnableGamepad; // Enable Gamepad Controls

  // Setup Dear ImGui style
  ImGui::StyleColorsDark();
  // ImGui::StyleColorsLight();

  // Setup Platform/Renderer backends
  ImGui_ImplGlfw_InitForOpenGL(window, true);
  ImGui_ImplOpenGL3_Init(glsl_version);

  // Load Fonts
  // - If no fonts are loaded, dear imgui will use the default font. You can
  // also load multiple fonts and use ImGui::PushFont()/PopFont() to select
  // them.
  // - AddFontFromFileTTF() will return the ImFont* so you can store it if you
  // need to select the font among multiple.
  // - If the file cannot be loaded, the function will return a nullptr. Please
  // handle those errors in your application (e.g. use an assertion, or display
  // an error and quit).
  // - The fonts will be rasterized at a given size (w/ oversampling) and stored
  // into a texture when calling ImFontAtlas::Build()/GetTexDataAsXXXX(), which
  // ImGui_ImplXXXX_NewFrame below will call.
  // - Use '#define IMGUI_ENABLE_FREETYPE' in your imconfig file to use Freetype
  // for higher quality font rendering.
  // - Read 'docs/FONTS.md' for more instructions and details.
  // - Remember that in C/C++ if you want to include a backslash \ in a string
  // literal you need to write a double backslash \\ !
  // - Our Emscripten build process allows embedding fonts to be accessible at
  // runtime from the "fonts/" folder. See Makefile.emscripten for details.
  // io.Fonts->AddFontDefault();
  // io.Fonts->AddFontFromFileTTF("c:\\Windows\\Fonts\\segoeui.ttf", 18.0f);
  // io.Fonts->AddFontFromFileTTF("../../misc/fonts/DroidSans.ttf", 16.0f);
  // io.Fonts->AddFontFromFileTTF("../../misc/fonts/Roboto-Medium.ttf", 16.0f);
  // io.Fonts->AddFontFromFileTTF("../../misc/fonts/Cousine-Regular.ttf", 15.0f);
  // ImFont* font =
  // io.Fonts->AddFontFromFileTTF("c:\\Windows\\Fonts\\ArialUni.ttf", 18.0f,
  // nullptr, io.Fonts->GetGlyphRangesJapanese()); IM_ASSERT(font != nullptr);

  // Our state
  bool show_demo_window = true;
  bool show_another_window = false;
  ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);

  setup_opengl();

  // Main loop
#ifdef __EMSCRIPTEN__
  // For an Emscripten build we are disabling file-system access, so let's not
  // attempt to do a fopen() of the imgui.ini file. You may manually call
  // LoadIniSettingsFromMemory() to load settings from your own storage.
  io.IniFilename = nullptr;
  EMSCRIPTEN_MAINLOOP_BEGIN
#else
  while (!glfwWindowShouldClose(window))
#endif
  {
    // Poll and handle events (inputs, window resize, etc.)
    // You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to
    // tell if dear imgui wants to use your inputs.
    // - When io.WantCaptureMouse is true, do not dispatch mouse input data to
    // your main application, or clear/overwrite your copy of the mouse data.
    // - When io.WantCaptureKeyboard is true, do not dispatch keyboard input
    // data to your main application, or clear/overwrite your copy of the
    // keyboard data. Generally you may always pass all inputs to dear imgui,
    // and hide them from your application based on those two flags.
    glfwPollEvents();

    // Start the Dear ImGui frame
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    vs.show_axis = 0x01 | 0x02 | 0x04;
    vs.width = io.DisplaySize.x;
    vs.height = io.DisplaySize.y;

    if (!io.WantCaptureMouse) {
      // send mouse event to 3D scene
      if (io.MouseClicked[ImGuiMouseButton_Left]) {
        mouse_button_callback(window, GLFW_MOUSE_BUTTON_LEFT, GLFW_PRESS, 0);
      }
      if (io.MouseClicked[ImGuiMouseButton_Right]) {
        mouse_button_callback(window, GLFW_MOUSE_BUTTON_RIGHT, GLFW_PRESS, 0);
      }
      if (io.MouseClicked[ImGuiMouseButton_Middle]) {
        mouse_button_callback(window, GLFW_MOUSE_BUTTON_MIDDLE, GLFW_PRESS, 0);
      }

      if (io.MouseReleased[ImGuiMouseButton_Left]) {
        mouse_button_callback(window, GLFW_MOUSE_BUTTON_LEFT, GLFW_RELEASE, 0);
      }
      if (io.MouseReleased[ImGuiMouseButton_Right]) {
        mouse_button_callback(window, GLFW_MOUSE_BUTTON_RIGHT, GLFW_RELEASE, 0);
      }
      if (io.MouseReleased[ImGuiMouseButton_Middle]) {
        mouse_button_callback(window, GLFW_MOUSE_BUTTON_MIDDLE, GLFW_RELEASE,
                              0);
      }

      cursor_position_callback(window, io.MousePos.x, io.MousePos.y);
    } else {
      vs.x = io.MousePos.x;
      vs.y = io.MousePos.y;
    }

    // 1. Show the big demo window (Most of the sample code is in
    // ImGui::ShowDemoWindow()! You can browse its code to learn more about Dear
    // ImGui!).
    if (show_demo_window)
      ImGui::ShowDemoWindow(&show_demo_window);

    // 2. Show a simple window that we create ourselves. We use a Begin/End pair
    // to create a named window.
    {
      static float f = 0.0f;
      static int counter = 0;

      ImGui::Begin("Hello, world!"); // Create a window called "Hello, world!"
                                     // and append into it.

      ImGui::Text("This is some useful text."); // Display some text (you can
                                                // use a format strings too)
      ImGui::Checkbox(
          "Demo Window",
          &show_demo_window); // Edit bools storing our window open/close state
      ImGui::Checkbox("Another Window", &show_another_window);

      ImGui::SliderFloat("float", &f, 0.0f,
                         1.0f); // Edit 1 float using a slider from 0.0f to 1.0f
      ImGui::ColorEdit3(
          "clear color",
          (float *)&clear_color); // Edit 3 floats representing a color

      if (ImGui::Button("Button")) // Buttons return true when clicked (most
                                   // widgets return true when edited/activated)
        counter++;
      ImGui::SameLine();
      ImGui::Text("counter = %d", counter);

      ImGui::Text("Application average %.3f ms/frame (%.1f FPS)",
                  1000.0f / io.Framerate, io.Framerate);
      ImGui::End();
    }

    // 3. Show another simple window.
    if (show_another_window) {
      ImGui::Begin(
          "Another Window",
          &show_another_window); // Pass a pointer to our bool variable (the
                                 // window will have a closing button that will
                                 // clear the bool when clicked)
      ImGui::Text("Hello from another window!");
      if (ImGui::Button("Close Me"))
        show_another_window = false;
      ImGui::End();
    }

    // Rendering
    ImGui::Render();
    int display_w, display_h;
    glfwGetFramebufferSize(window, &display_w, &display_h);
    glViewport(0, 0, display_w, display_h);
    glClearColor(clear_color.x * clear_color.w, clear_color.y * clear_color.w,
                 clear_color.z * clear_color.w, clear_color.w);
    glClear(GL_COLOR_BUFFER_BIT);

    draw_screen(vs);

    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

    glfwSwapBuffers(window);
  }
#ifdef __EMSCRIPTEN__
  EMSCRIPTEN_MAINLOOP_END;
#endif

  // Cleanup
  ImGui_ImplOpenGL3_Shutdown();
  ImGui_ImplGlfw_Shutdown();
  ImGui::DestroyContext();

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
