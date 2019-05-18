import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import numpy
import glm
import sys

def phong_shading():

    # initialize glfw
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Phong Shading", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    vertex_shader = """
    #version 330

    in vec3 gl_Vertex;
    in vec3 gl_Normal;

    uniform mat4 model_view_matrix;
    uniform mat4 normal_matrix;
    uniform mat4 model_view_projection_matrix;     

    out vec3 Normal;
    out vec3 Vertex;

    void main()
    {
        Vertex = vec3(model_view_matrix * vec4(gl_Vertex, 1.0));
        Normal = vec3(normalize(normal_matrix * vec4(gl_Normal, 0.0)));
        gl_Position = model_view_projection_matrix * vec4(gl_Vertex, 1.0);
    }

    """

    fragment_shader = """
    #version 330

    in vec3 Normal;
    in vec3 Vertex;

    uniform vec3 aColor;
    uniform vec3 lPosition;
    uniform vec3 lColor;
    uniform vec3 lSpecular;
    uniform float mShininess;

    void main()
    {
        vec3 L = normalize(lPosition - Vertex);
        vec3 E = normalize(-Vertex);
        vec3 R = normalize(-reflect(L, Normal));

        // Ambient
        vec4 ambient = vec4(aColor, 1.0);

        // Diffuse term
        vec4 diffuse = vec4(max(dot(L, Normal), 0) * lColor, 0.0);

        // Specular term
        vec4 specular = vec4(lSpecular * pow(max(dot(R, E), 0.0), 0.3 * mShininess), 0.0);

        gl_FragColor = ambient + diffuse + specular;
    }
    """
    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))
   
    glUseProgram(shader)

    aColor = [0.0, 0.0, 0.5]
    lPosition = [300, 300, 300]
    lColor = [0.5, 0.5, 0.5]
    lSpecular = [1.0, 1.0, 1.0]
    mShininess = 25

    aColor = numpy.array(aColor, dtype = numpy.float32)
    lPosition = numpy.array(lPosition, dtype = numpy.float32)
    lColor = numpy.array(lColor, dtype = numpy.float32)
    lSpecular = numpy.array(lSpecular, dtype = numpy.float32)

    aColorLoc = glGetUniformLocation(shader, "aColor")
    glUniform3fv(aColorLoc, 1, aColor)

    lPositionLoc = glGetUniformLocation(shader, "lPosition")
    glUniform3fv(lPositionLoc, 1, lPosition)

    lColorLoc = glGetUniformLocation(shader, "lColor")
    glUniform3fv(lColorLoc, 1, lColor)

    lSpecularLoc = glGetUniformLocation(shader, "lSpecular")
    glUniform3fv(lSpecularLoc, 1, lSpecular)

    mShininessLoc = glGetUniformLocation(shader, "mShininess")
    glUniform1f(mShininessLoc, mShininess)

    glClearColor(0.2, 0.3, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)

    pers = glm.perspective(0.5,1.0,0.1,10.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Create rotation matrix
        rot_x = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(1.0,0.0,0.0))
        rot_y = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(0.0,1.0,0.0))

        # Create normal transformation matrix
        normal_matrix = glm.mat4(1.0)
        normalMatrixLoc = glGetUniformLocation(shader, "normal_matrix")
        glUniformMatrix4fv(normalMatrixLoc, 1, GL_FALSE, glm.value_ptr(normal_matrix*rot_x*rot_y))

        # Create tranformation matrix for sphere
        trans = glm.translate(glm.mat4(1.0), glm.vec3(-0.5,0.0,-5.5))
        
        modelViewLoc = glGetUniformLocation(shader, "model_view_matrix")
        glUniformMatrix4fv(modelViewLoc, 1, GL_FALSE, glm.value_ptr(trans*rot_x*rot_y))

        modelViewProjLoc = glGetUniformLocation(shader, "model_view_projection_matrix")
        glUniformMatrix4fv(modelViewProjLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

        # Draw Sphere
        sphere_quadric = gluNewQuadric()
        gluQuadricNormals(sphere_quadric, GLU_SMOOTH)
        gluSphere(sphere_quadric, 0.35, 20, 20)

        # Create tranformation matrix for cylinder
        trans = glm.translate(glm.mat4(1.0), glm.vec3(0.5,0.0,-5.5))

        modelViewLoc = glGetUniformLocation(shader, "model_view_matrix")
        glUniformMatrix4fv(modelViewLoc, 1, GL_FALSE, glm.value_ptr(trans*rot_x*rot_y))

        modelViewProjLoc = glGetUniformLocation(shader, "model_view_projection_matrix")
        glUniformMatrix4fv(modelViewProjLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

        # Draw cylinder
        cylinder_quad = gluNewQuadric()
        gluQuadricNormals(cylinder_quad, GLU_SMOOTH)
        gluCylinder(cylinder_quad, 0.25, 0.25, 0.5, 10, 10)

        glfw.swap_buffers(window)

    glfw.terminate()

def gouraud_shading():

    # initialize glfw
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Gouraud Shading", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    vertex_shader = """
    #version 330

    in vec3 gl_Vertex;
    in vec3 gl_Normal;

    uniform mat4 transform;
    uniform mat4 transform_normal;
    uniform vec3 aColor;
    uniform vec3 lDirection;
    uniform vec3 lColor;

    out vec4 newColor;
    void main()
    {
        gl_Position = transform * vec4(gl_Vertex, 1.0f);

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(lDirection, -vec3(transform_normal*vec4(gl_Normal,1.0))), 0) * lColor, 0);
        
        newColor =  ambient + diffuse;
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

    aColor = [0.0, 0.0, 0.5]
    lDirection = [-1.0, -1.0, -1.0]
    lColor = [1.0, 1.0, 1.0]

    aColor = numpy.array(aColor, dtype = numpy.float32)
    lDirection = numpy.array(lDirection, dtype = numpy.float32)
    lColor = numpy.array(lColor, dtype = numpy.float32)
    # normal = numpy.array(normal, dtype = numpy.float32)

    aColorLoc = glGetUniformLocation(shader, "aColor")
    glUniform3fv(aColorLoc, 1, aColor)

    lDirectionLoc = glGetUniformLocation(shader, "lDirection")
    glUniform3fv(lDirectionLoc, 1, lDirection)

    lColorLoc = glGetUniformLocation(shader, "lColor")
    glUniform3fv(lColorLoc, 1, lColor)

    # normalLoc = glGetUniformLocation(shader, "normal")
    # glUniform3fv(normalLoc, 1, normal)

    glClearColor(0.2, 0.3, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)

    pers = glm.perspective(0.5,1.0,0.1,10.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Create rotation matrix
        rot_x = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(1.0,0.0,0.0))
        rot_y = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(0.0,1.0,0.0))

        # Create normal transformation matrix
        trans_normal = glm.mat4(1.0)
        transformNormalLoc = glGetUniformLocation(shader, "transform_normal")
        glUniformMatrix4fv(transformNormalLoc, 1, GL_FALSE, glm.value_ptr(trans_normal*rot_x*rot_y))

        # Create tranformation matrix for sphere
        trans = glm.translate(glm.mat4(1.0), glm.vec3(-0.5,0.0,-5.5))
        transformLoc = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

        # Draw Sphere
        sphere_quadric = gluNewQuadric()
        gluQuadricNormals(sphere_quadric, GLU_SMOOTH)
        gluSphere(sphere_quadric, 0.35, 20, 20)

        # Create tranformation matrix for cylinder
        trans = glm.translate(glm.mat4(1.0), glm.vec3(0.5,0.0,-5.5))
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

        # Draw cylinder
        cylinder_quad = gluNewQuadric()
        gluQuadricNormals(cylinder_quad, GLU_SMOOTH)
        gluCylinder(cylinder_quad, 0.25, 0.25, 0.5, 10, 10)

        glfw.swap_buffers(window)

    glfw.terminate()

def flat_shading():

    # initialize glfw
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Flat Shading", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    vertex_shader = """
    #version 330

    in vec3 gl_Vertex;
    in vec3 gl_Normal;

    uniform mat4 transform;
    uniform mat4 transform_normal;
    uniform vec3 aColor;
    uniform vec3 lDirection;
    uniform vec3 lColor;

    out vec4 newColor;
    void main()
    {
        gl_Position = transform * vec4(gl_Vertex, 1.0f);

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(lDirection, -vec3(transform_normal*vec4(gl_Normal,1.0))), 0) * lColor, 0);
        
        newColor =  ambient + diffuse;
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

    aColor = [0.0, 0.0, 0.5]
    lDirection = [-1.0, -1.0, -1.0]
    lColor = [1.0, 1.0, 1.0]

    aColor = numpy.array(aColor, dtype = numpy.float32)
    lDirection = numpy.array(lDirection, dtype = numpy.float32)
    lColor = numpy.array(lColor, dtype = numpy.float32)
    # normal = numpy.array(normal, dtype = numpy.float32)

    aColorLoc = glGetUniformLocation(shader, "aColor")
    glUniform3fv(aColorLoc, 1, aColor)

    lDirectionLoc = glGetUniformLocation(shader, "lDirection")
    glUniform3fv(lDirectionLoc, 1, lDirection)

    lColorLoc = glGetUniformLocation(shader, "lColor")
    glUniform3fv(lColorLoc, 1, lColor)

    # normalLoc = glGetUniformLocation(shader, "normal")
    # glUniform3fv(normalLoc, 1, normal)

    glClearColor(0.2, 0.3, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)

    pers = glm.perspective(0.5,1.0,0.1,10.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Create rotation matrix
        rot_x = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(1.0,0.0,0.0))
        rot_y = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(0.0,1.0,0.0))

        # Create normal transformation matrix
        trans_normal = glm.mat4(1.0)
        transformNormalLoc = glGetUniformLocation(shader, "transform_normal")
        glUniformMatrix4fv(transformNormalLoc, 1, GL_FALSE, glm.value_ptr(trans_normal*rot_x*rot_y))

        # Create tranformation matrix for sphere
        trans = glm.translate(glm.mat4(1.0), glm.vec3(-0.5,0.0,-5.5))
        transformLoc = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

        # Draw Sphere
        sphere_quadric = gluNewQuadric()
        gluQuadricNormals(sphere_quadric, GLU_FLAT)
        gluSphere(sphere_quadric, 0.35, 20, 20)

        # Create tranformation matrix for cylinder
        trans = glm.translate(glm.mat4(1.0), glm.vec3(0.5,0.0,-5.5))
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

        # Draw cylinder
        cylinder_quad = gluNewQuadric()
        gluQuadricNormals(cylinder_quad, GLU_FLAT)
        gluCylinder(cylinder_quad, 0.25, 0.25, 0.5, 10, 10)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    shader = sys.argv[1]
    if shader == "flat":
        flat_shading()
    elif shader == "gouraud":
        gouraud_shading()
    elif shader == "phong":
        phong_shading()
