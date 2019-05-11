import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import numpy
import glm


def flat_shading():

    # initialize glfw
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "My OpenGL window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    vertex_shader = """
    #version 330

    in vec3 position;
    in vec3 normal;

    uniform mat4 transform;
    uniform vec3 aColor;
    uniform vec3 lDirection;
    uniform vec3 lColor;

    out vec4 newColor;
    void main()
    {
        gl_Position = transform * vec4(position, 1.0f);

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(lDirection, -normal), 0) * lColor, 0);
        
        newColor = ambient + diffuse;
    }

    """

    fragment_shader = """
    #version 330

    in vec4 newColor;

    void main()
    {
        gl_FragColor = newColor;
    }
    """
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))
   
    glUseProgram(shader)

    aColor = [0.0, 0.0, 1.0]
    lDirection = [-1.0, 0.0, 0.0]
    lColor = [1.0, 1.0, 1.0]

    aColor = numpy.array(aColor, dtype = numpy.float32)
    lDirection = numpy.array(lDirection, dtype = numpy.float32)
    lColor = numpy.array(lColor, dtype = numpy.float32)

    aColorLoc = glGetUniformLocation(shader, "aColor")
    glUniform3fv(aColorLoc, 1, aColor)

    lDirectionLoc = glGetUniformLocation(shader, "lDirection")
    glUniform3fv(lDirectionLoc, 1, lDirection)

    lColorLoc = glGetUniformLocation(shader, "lDirection")
    glUniform3fv(lColorLoc, 1, lColor)



    glClearColor(0.2, 0.3, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)

    pers = glm.perspective(0.5,1.0,0.1,10.0)
    trans = glm.translate(glm.mat4(1.0), glm.vec3(0.0,0.0,-5.5))

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # glDrawArrays(GL_TRIANGLES, 0, 3)
        
        sphere_quadric = gluNewQuadric()
        gluSphere(sphere_quadric, 0.5, 10, 10)

        transformLoc = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(pers*trans))

        # glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    flat_shading()
