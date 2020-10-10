#version 330
in vec3 f_position;
in vec4 f_normal;
in vec3 f_color;
out vec4 color;

vec3 lightPos= vec3(0, 1, 0);
vec3 viewPos = vec3(0, 0, 0);

void main() {
  color = vec4(f_color, 1.0);
  vec3 lightColor = vec3(0.9, 1.0, 0.8);
  float ambientStrength = 0.3;
  vec3 ambient = ambientStrength * lightColor;

  gl_FragDepth = clamp(f_position.z / 100., 0, 1);

  vec3 norm = normalize(f_normal.xyz);
  vec3 lightDir = normalize(f_position.xyz-lightPos);
  float diff = max(dot(norm, lightDir), 0.0);
  vec3 diffuse = diff*lightColor;

  float specularStrength = 0.3;
  vec3 viewDir = normalize(viewPos - f_position.xyz);
  vec3 reflectDir = reflect(lightDir, norm);


  float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
  vec3 specular =  specularStrength*spec * lightColor;

  vec3 result = (ambient+diffuse+specular) * color.xyz;

  color = vec4(result, 1.0);
}
