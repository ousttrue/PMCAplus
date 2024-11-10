@vs vs
in vec3 aPosition;
in vec2 aUv;
out vec2 fUv;

layout(binding=0)uniform vs_params {
  mat4 mvp;
};

void main() {
  gl_Position = mvp * vec4(aPosition, 1);
  fUv = aUv;
}
@end

@fs fs
in vec2 fUv;
out vec4 frag_color;
void main() {
  frag_color = vec4(fUv, 0, 1);
}
@end

@program PMCA_view vs fs
