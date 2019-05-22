import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import numpy
import glm
import sys

def read_obj_file(filename, swapyz=False):
    vertices = []
    normals = []
    texcoords = []
    faces = []

    material = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = values[1:4]
            if swapyz:
                v = v[0], v[2], v[1]
            vertices.append(v)
        elif values[0] == 'vn':
            v = values[1:4]
            if swapyz:
                v = v[0], v[2], v[1]
            normals.append(v)
        elif values[0] == 'vt':
            texcoords.append(map(float, values[1:3]))
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'mtllib':
            mtl = MTL(values[1])
        elif values[0] == 'f':
            face = []
            texcoords = []
            norms = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    texcoords.append(int(w[1]))
                else:
                    texcoords.append(0)
                if len(w) >= 3 and len(w[2]) > 0:
                    norms.append(int(w[2]))
                else:
                    norms.append(0)
            faces.append((face, norms, texcoords, material))
    
    return (vertices, normals, faces)

teapot_faces = read_obj_file("teapot_2.obj")

def draw_faces(obj):
    vertices = obj[0]
    normals = obj[1]
    faces = obj[2]

    glBegin(GL_TRIANGLES)
    for face in faces:
        face_vertices = face[0]
        face_normals = face[1]
        for i in range(3):
            glVertex3f(float(vertices[face_vertices[i]-1][0]), float(vertices[face_vertices[i]-1][1]), float(vertices[face_vertices[i]-1][2]))
            glNormal3f(float(normals[face_normals[i]-1][0]), float(normals[face_normals[i]-1][1]), float(normals[face_normals[i]-1][2]))
    glEnd()


def draw_objects(shader):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Create perspective matrix
    pers = glm.perspective(0.5,1.0,0.1,50.0)

    # Create rotation matrix
    rot_x = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(1.0,0.0,0.0))
    rot_y = glm.rotate(glm.mat4(1.0),0.5 * glfw.get_time(),glm.vec3(0.0,1.0,0.0))

    # Create normal transformation matrix
    normal_matrix = glm.mat4(1.0)
    normalMatrixLoc = glGetUniformLocation(shader, "normal_matrix")
    glUniformMatrix4fv(normalMatrixLoc, 1, GL_FALSE, glm.value_ptr(normal_matrix*rot_x*rot_y))

    # Create tranformation matrix for sphere
    trans = glm.translate(glm.mat4(1.0), glm.vec3(-0.8,0.8,-5.5))

    modelViewLoc = glGetUniformLocation(shader, "model_view_matrix")
    glUniformMatrix4fv(modelViewLoc, 1, GL_FALSE, glm.value_ptr(trans*rot_x*rot_y))

    modelViewProjLoc = glGetUniformLocation(shader, "model_view_projection_matrix")
    glUniformMatrix4fv(modelViewProjLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

    # Draw Sphere
    sphere_quadric = gluNewQuadric()
    gluQuadricNormals(sphere_quadric, GLU_SMOOTH)
    gluSphere(sphere_quadric, 0.35, 20, 20)

    # Create tranformation matrix for teapot
    trans = glm.translate(glm.mat4(1.0), glm.vec3(0.0,0.0,-20.5))

    scale = glm.scale(glm.mat4(1.0), glm.vec3(0.1, 0.1, 0.1))
    
    modelViewLoc = glGetUniformLocation(shader, "model_view_matrix")
    glUniformMatrix4fv(modelViewLoc, 1, GL_FALSE, glm.value_ptr(trans*scale*rot_x*rot_y))

    modelViewProjLoc = glGetUniformLocation(shader, "model_view_projection_matrix")
    glUniformMatrix4fv(modelViewProjLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*scale*rot_x*rot_y))
    
    draw_faces(teapot_faces)

    # Create tranformation matrix for cylinder
    trans = glm.translate(glm.mat4(1.0), glm.vec3(0.8,-0.8,-5.5))

    modelViewLoc = glGetUniformLocation(shader, "model_view_matrix")
    glUniformMatrix4fv(modelViewLoc, 1, GL_FALSE, glm.value_ptr(trans*rot_x*rot_y))

    modelViewProjLoc = glGetUniformLocation(shader, "model_view_projection_matrix")
    glUniformMatrix4fv(modelViewProjLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*rot_x*rot_y))

    # Draw cylinder
    cylinder_quad = gluNewQuadric()
    gluQuadricNormals(cylinder_quad, GLU_SMOOTH)
    gluCylinder(cylinder_quad, 0.25, 0.25, 0.5, 10, 10)

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
    #version 130

    uniform mat4 model_view_matrix;
    uniform mat4 normal_matrix;
    uniform mat4 model_view_projection_matrix;     

    out vec3 Normal;
    out vec3 Vertex;

    void main()
    {
        Vertex = vec3(model_view_matrix * gl_Vertex);
        Normal = vec3(normalize(normal_matrix * vec4(gl_Normal, 0.0)));
        gl_Position = model_view_projection_matrix * gl_Vertex;
    }

    """

    fragment_shader = """
    #version 130

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

    while not glfw.window_should_close(window):
        glfw.poll_events()

        draw_objects(shader)

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
    #version 130

    uniform mat4 model_view_matrix;
    uniform mat4 normal_matrix;
    uniform mat4 model_view_projection_matrix;   
      
    uniform vec3 aColor;
    uniform vec3 lPosition;
    uniform vec3 lColor;
    uniform vec3 lSpecular;
    uniform float mShininess;

    out vec4 newColor;
    void main()
    {
        vec3 Vertex = vec3(model_view_matrix * gl_Vertex);
        vec3 Normal = vec3(normalize(normal_matrix * vec4(gl_Normal, 0.0)));
        gl_Position = model_view_projection_matrix * gl_Vertex;

        vec3 L = normalize(lPosition - Vertex);
        vec3 E = normalize(-Vertex);
        vec3 R = normalize(-reflect(L, Normal));

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(L, Normal), 0) * lColor, 0.0);
        vec4 specular = vec4(lSpecular * pow(max(dot(R, E), 0.0), 0.3 * mShininess), 0.0);
        
        newColor =  ambient + diffuse + specular;
    }

    """

    fragment_shader = """
    #version 130

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

        draw_objects(shader)

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
    #version 130

    uniform mat4 model_view_matrix;
    uniform mat4 model_view_projection_matrix;   

    out vec3 Vertex;
    
    void main()
    {
        Vertex = vec3(model_view_matrix * gl_Vertex);
        gl_Position = model_view_projection_matrix * gl_Vertex;
    }

    """

    fragment_shader = """
    #version 130

    in vec3 Vertex;

    uniform vec3 aColor;
    uniform vec3 lPosition;
    uniform vec3 lColor;
    uniform vec3 lSpecular;
    uniform float mShininess;

    void main()
    {
        vec3 Normal = normalize(cross(dFdx(Vertex), dFdy(Vertex)));

        vec3 L = normalize(lPosition - Vertex);
        vec3 E = normalize(-Vertex);
        vec3 R = normalize(-reflect(L, Normal));

        vec4 ambient = vec4(aColor, 0);
        vec4 diffuse = vec4(max(dot(L, Normal), 0) * lColor, 0.0);
        vec4 specular = vec4(lSpecular * pow(max(dot(R, E), 0.0), 0.3 * mShininess), 0.0);
        
        gl_FragColor =  ambient + diffuse + specular;
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

        draw_objects(shader)

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
