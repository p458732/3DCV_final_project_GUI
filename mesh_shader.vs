#version 330

//uniform mat4 mvpmatrix;

layout (location = 0) in vec3 position;

uniform mat4 mvp_matrix;

void main() {
    gl_Position = mvp_matrix * vec4(position, 1.0);
}