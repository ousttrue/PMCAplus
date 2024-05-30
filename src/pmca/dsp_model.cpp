#include <GL/glew.h>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

#include "dsp_model.h"
#include "pmd_model.h"
#include <stdint.h>
#include <vector>

static const char *vertex_shader_text = R"(#version 330
uniform mat4 MVP;
in vec3 vCol;
in vec2 vPos;
out vec3 color;
void main()
{
    gl_Position = MVP * vec4(vPos, 0.0, 1.0);
    color = vCol;
}
)";

static const char *fragment_shader_text = R"(#version 330
in vec3 color;
out vec4 fragment;
void main()
{
    fragment = vec4(color, 1.0);
}
)";

struct Vertex {
  float pos[2];
  float col[3];
};

// CCW
//   2
// 0  1
// static const Vertex vertices[3] = {{{-0.6f, -0.4f}, {1.f, 0.f, 0.f}},
//                                    {{0.6f, -0.4f}, {0.f, 1.f, 0.f}},
//                                    {{0.f, 0.6f}, {0.f, 0.f, 1.f}}};

// CW
//  1
// p 2
static const Vertex vertices[3] = {
    {{-0.6f, -0.4f}, {1.f, 0.f, 0.f}},
    {{0.f, 0.6f}, {0.f, 0.f, 1.f}},
    {{0.6f, -0.4f}, {0.f, 1.f, 0.f}},
};

struct Triangle {

  GLuint vertex_shader = 0;
  GLuint fragment_shader = 0;
  GLuint program = 0;
  GLint mvp_location = -1;
  GLint vpos_location = -1;
  GLint vcol_location = -1;

  GLuint vertex_buffer = 0;
  GLuint vertex_array = 0;

  Triangle() {
    // shader
    vertex_shader = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vertex_shader, 1, &vertex_shader_text, NULL);
    glCompileShader(vertex_shader);

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fragment_shader, 1, &fragment_shader_text, NULL);
    glCompileShader(fragment_shader);

    program = glCreateProgram();
    glAttachShader(program, vertex_shader);
    glAttachShader(program, fragment_shader);
    glLinkProgram(program);

    mvp_location = glGetUniformLocation(program, "MVP");
    vpos_location = glGetAttribLocation(program, "vPos");
    vcol_location = glGetAttribLocation(program, "vCol");

    // vbo
    glGenBuffers(1, &vertex_buffer);
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // vao
    glGenVertexArrays(1, &vertex_array);
    glBindVertexArray(vertex_array);
    glEnableVertexAttribArray(vpos_location);
    glVertexAttribPointer(vpos_location, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex),
                          (void *)offsetof(Vertex, pos));
    glEnableVertexAttribArray(vcol_location);
    glVertexAttribPointer(vcol_location, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex),
                          (void *)offsetof(Vertex, col));

    glBindVertexArray(0);
  }

  void Draw() {
    float mvp[16] = {
        1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
    };
    glUseProgram(program);
    glUniformMatrix4fv(mvp_location, 1, GL_FALSE, (const GLfloat *)&mvp);
    glBindVertexArray(vertex_array);
    glDrawArrays(GL_TRIANGLES, 0, 3);
  }

  static std::shared_ptr<Triangle> create() {
    auto p = std::make_shared<Triangle>();
    return p;
  }
};

struct DSP_MAT {
  float col[4];
  char texname[128];
  int width = 0;
  int height = 0;
  std::vector<int8_t> texbits;
};

struct DSP_MODEL {
  std::vector<DSP_MAT> mats;
  std::vector<uint32_t> texid;

  void make(const std::shared_ptr<MODEL> &model) {
    if (texid.size()) {
      glDeleteTextures(texid.size(), texid.data());
    }
    mats.clear();

    texid.resize(model->mat.size());
    glGenTextures(texid.size(), texid.data());
    for (size_t i = 0; i < model->mat.size(); i++) {
      mats.push_back({});

      int width;
      int height;
      auto texbits =
          stbi_load(model->mat[i].tex_path, &width, &height, nullptr, 4);
      if (texbits) {
        double log_w = log(width) / log(2);
        double log_h = log(height) / log(2);
        if (ceil(log_w) != floor(log_w) || ceil(log_h) != floor(log_h)) {
          int w = 2;
          int h = 2;
          for (int j = 0; j < floor(log_w); j++) {
            w = w * 2;
          }
          for (int j = 0; j < floor(log_h); j++) {
            h = h * 2;
          }

          std::vector<uint8_t> tmp_bits(h * w * sizeof(GLubyte) * 6);
          gluScaleImage(GL_RGBA, width, height, GL_UNSIGNED_BYTE, texbits, w, h,
                        GL_UNSIGNED_BYTE, tmp_bits.data());
          width = w;
          height = h;
          mats.back().texbits.assign(tmp_bits.data(),
                                     tmp_bits.data() + width * height * 4);
          mats.back().width = width;
          mats.back().height = height;
        } else {
          mats.back().texbits.assign(texbits, texbits + width * height * 4);
          mats.back().width = width;
          mats.back().height = height;
        }
        stbi_image_free(texbits);
      } else {
        printf("画像が読み込めません %s\n", model->mat[i].tex_path);
      }
    }
  }
};

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

  int c = 0;
  for (int i = 0; i < model->mat.size(); i++) {
    if (s_dsp.mats[i].texbits.size()) {
      glEnable(GL_TEXTURE_2D);
      glBindTexture(GL_TEXTURE_2D, s_dsp.texid[i]);

      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
      glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, s_dsp.mats[i].width,
                   s_dsp.mats[i].height, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                   s_dsp.mats[i].texbits.data());
    }

    glBegin(GL_TRIANGLES);
    for (int j = 0; j < model->mat[i].vt_index_count; j++) {
      auto index = model->vt_index[c++];
      auto v = model->vt[index];
      glTexCoord2fv(v.uv);
      glVertex3fv(v.loc);
    }

    glEnd();
    glDisable(GL_TEXTURE_2D);
  }

  // static auto s_triangle = Triangle::create();
  //
  // s_triangle->Draw();
}
