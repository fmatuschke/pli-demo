#version 330 core
//Input:Linien
layout(lines) in;
//Output: zusamenhängende Dreiecke
layout(triangle_strip, max_vertices = 66) out;

// Setze PI, da dies nicht in GLSL existiert
# define M_PI 3.1415926535897932384626433832795028841971

in VS_OUT {
  vec3 position;
  vec3 orientation;
} gs_in[];

out vec3 f_position;
out vec4 f_normal;
out vec3 f_color;

// uniform mat4 modelToWorld;
uniform mat4 worldToCamera;

mat4 rodrigues(vec3 vecOrientation) {
    vec3 cylinderOrientation = vec3(1, 0, 0);

    mat4 cylinderRotation = mat4(1.0);
    float c = dot(vecOrientation, cylinderOrientation);
    vec3 d = vec3(cross(vecOrientation, cylinderOrientation));
    float s = length(d);


    mat4 a_x = mat4(0.0,    -d.z,   d.y,    0,
        d.z,    0,      -d.x,   0,
        -d.y,   d.x,    0,      0,
        0,      0,      0,      0);
    cylinderRotation = mat4(1.0) + s * a_x + (1-c) * (a_x * a_x);

    return cylinderRotation;
}

void draw() {
    int corners = 66/6;
    vec4 begin = gl_in[0].gl_Position;
    vec4 end = gl_in[1].gl_Position;

    //Berechne Orientierung
    vec3 vecOrientation = gs_in[0].orientation;//(end-begin).xyz;
    //Berechne Rotationsmatrixen mittels Rodriguesformel
    mat4 rot = rodrigues(vecOrientation);

    float radius = 1;

    //Erstelle n Stuetzpunkte
    for(int j=0; j<corners; j++) {
        //Berechne winkel in radian des j-ten Stützpunktes
        float alpha = j*2*M_PI/corners;
        float nextalpha = (j+1)*2*M_PI/corners;

        gl_Position  = worldToCamera * begin;
        f_normal = rot * vec4(normalize(vecOrientation), 1);
        f_position = gl_Position.xyz;
        f_color = vec3(0, 0, 0);
        EmitVertex();

        gl_Position = worldToCamera * (begin + rot * (vec4(0, radius*cos(alpha), radius*sin(alpha), 1)));
        f_normal = rot * vec4(0, radius*cos(alpha), radius*sin(alpha), 1);
        f_position = gl_Position.xyz;
        f_color = vec3(0,0,0);
        EmitVertex();
        gl_Position = worldToCamera * (begin + rot * (vec4(0, radius*cos(nextalpha), radius*sin(nextalpha), 1)));
        f_normal = rot * vec4(0, radius*cos(nextalpha), radius*sin(nextalpha), 1);
        f_position = gl_Position.xyz;
        f_color = vec3(0, 0, 0);
        EmitVertex();

        gl_Position = worldToCamera * (end + rot * (vec4(0, radius*cos(alpha), radius*sin(alpha), 1)));
        f_normal = rot * vec4(0, radius*cos(alpha), radius*sin(alpha), 1);
        f_position = gl_Position.xyz;
        f_color = vec3(0.02, 0.431, 0.235);
        EmitVertex();
        gl_Position = worldToCamera * (end + rot * (vec4(0, radius*cos(nextalpha), radius*sin(nextalpha), 1)));
        f_normal = rot * vec4(0, radius*cos(nextalpha), radius*sin(nextalpha), 1);
        f_position = gl_Position.xyz;
        f_color = vec3(0.02, 0.431, 0.235);
        EmitVertex();

        gl_Position = worldToCamera * end;
        f_normal = rot * vec4(normalize(vecOrientation), 1);
        f_position = gl_Position.xyz;
        f_color = vec3(0.02, 0.431, 0.235);
        EmitVertex();
    }
}

void main() {
    draw();
    // gColor = vec4(1.0, 1.0, 1.0, 1.0);
    // gl_Position = gl_in[0].gl_Position;
    // EmitVertex();
    // gColor = vec4(1.0, 1.0, 1.0, 1.0);
    // gl_Position = gl_in[1].gl_Position;
    // EmitVertex();
    EndPrimitive();
}
