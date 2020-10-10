#version 330
in vec3 v_position;
in vec3 v_orientation;
out VS_OUT {
  vec3 position;
  vec3 orientation;
} vs_out;

void main() {
  gl_Position = vec4(v_position, 1.0);
  vs_out.position = v_position;
  vs_out.orientation = v_orientation;
}
