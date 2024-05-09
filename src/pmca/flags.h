#pragma once
#include <memory>

struct FLAGS {
  std::shared_ptr<struct MODEL> current_model;
  int button1;
  int button2;
  int button3;
  int model_lock;
  int quit;
};

extern FLAGS myflags;
