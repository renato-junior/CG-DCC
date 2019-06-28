from ctypes import *
import struct
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import time
import glfw
import glm
import numpy as np

MD2_IDENT = 844121161
MD2_VERSION = 8

NUMVERTEXNORMALS = 162
SHADEDOT_QUANT = 16

phong_vertex_shader = """
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

phong_fragment_shader = """
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

anorms =   [(0.525731,  0.000000,  0.850651), 
            (0.442863,  0.238856,  0.864188), 
            (0.295242,  0.000000,  0.955423), 
            (0.309017,  0.500000,  0.809017), 
            (0.162460,  0.262866,  0.951056), 
            (0.000000,  0.000000,  1.000000), 
            (0.000000,  0.850651,  0.525731), 
            (0.147621,  0.716567,  0.681718), 
            (0.147621,  0.716567,  0.681718), 
            (0.000000,  0.525731,  0.850651), 
            (0.309017,  0.500000,  0.809017), 
            (0.525731,  0.000000,  0.850651), 
            (0.295242,  0.000000,  0.955423), 
            (0.442863,  0.238856,  0.864188), 
            (0.162460,  0.262866,  0.951056), 
            (0.681718,  0.147621,  0.716567), 
            (0.809017,  0.309017,  0.500000), 
            (0.587785,  0.425325,  0.688191), 
            (0.850651,  0.525731,  0.000000), 
            (0.864188,  0.442863,  0.238856), 
            (0.716567,  0.681718,  0.147621), 
            (0.688191,  0.587785,  0.425325), 
            (0.500000,  0.809017,  0.309017), 
            (0.238856,  0.864188,  0.442863), 
            (0.425325,  0.688191,  0.587785), 
            (0.716567,  0.681718, -0.147621), 
            (0.500000,  0.809017, -0.309017), 
            (0.525731,  0.850651,  0.000000), 
            (0.000000,  0.850651, -0.525731), 
            (0.238856,  0.864188, -0.442863), 
            (0.000000,  0.955423, -0.295242), 
            (0.262866,  0.951056, -0.162460), 
            (0.000000,  1.000000,  0.000000), 
            (0.000000,  0.955423,  0.295242), 
            (0.262866,  0.951056,  0.162460), 
            (0.238856,  0.864188,  0.442863), 
            (0.262866,  0.951056,  0.162460), 
            (0.500000,  0.809017,  0.309017), 
            (0.238856,  0.864188, -0.442863), 
            (0.262866,  0.951056, -0.162460), 
            (0.500000,  0.809017, -0.309017), 
            (0.850651,  0.525731,  0.000000), 
            (0.716567,  0.681718,  0.147621), 
            (0.716567,  0.681718, -0.147621), 
            (0.525731,  0.850651,  0.000000), 
            (0.425325,  0.688191,  0.587785), 
            (0.864188,  0.442863,  0.238856), 
            (0.688191,  0.587785,  0.425325), 
            (0.809017,  0.309017,  0.500000), 
            (0.681718,  0.147621,  0.716567), 
            (0.587785,  0.425325,  0.688191), 
            (0.955423,  0.295242,  0.000000), 
            (1.000000,  0.000000,  0.000000), 
            (0.951056,  0.162460,  0.262866), 
            (0.850651, -0.525731,  0.000000), 
            (0.955423, -0.295242,  0.000000), 
            (0.864188, -0.442863,  0.238856), 
            (0.951056, -0.162460,  0.262866), 
            (0.809017, -0.309017,  0.500000), 
            (0.681718, -0.147621,  0.716567), 
            (0.850651,  0.000000,  0.525731), 
            (0.864188,  0.442863, -0.238856), 
            (0.809017,  0.309017, -0.500000), 
            (0.951056,  0.162460, -0.262866), 
            (0.525731,  0.000000, -0.850651), 
            (0.681718,  0.147621, -0.716567), 
            (0.681718, -0.147621, -0.716567), 
            (0.850651,  0.000000, -0.525731), 
            (0.809017, -0.309017, -0.500000), 
            (0.864188, -0.442863, -0.238856), 
            (0.951056, -0.162460, -0.262866), 
            (0.147621,  0.716567, -0.681718), 
            (0.309017,  0.500000, -0.809017), 
            (0.425325,  0.688191, -0.587785), 
            (0.442863,  0.238856, -0.864188), 
            (0.587785,  0.425325, -0.688191), 
            (0.688191,  0.587785, -0.425325), 
            (0.147621,  0.716567, -0.681718), 
            (0.309017,  0.500000, -0.809017), 
            (0.000000,  0.525731, -0.850651), 
            (0.525731,  0.000000, -0.850651), 
            (0.442863,  0.238856, -0.864188), 
            (0.295242,  0.000000, -0.955423), 
            (0.162460,  0.262866, -0.951056), 
            (0.000000,  0.000000, -1.000000), 
            (0.295242,  0.000000, -0.955423), 
            (0.162460,  0.262866, -0.951056), 
            (0.442863, -0.238856, -0.864188), 
            (0.309017, -0.500000, -0.809017), 
            (0.162460, -0.262866, -0.951056), 
            (0.000000, -0.850651, -0.525731), 
            (0.147621, -0.716567, -0.681718), 
            (0.147621, -0.716567, -0.681718), 
            (0.000000, -0.525731, -0.850651), 
            (0.309017, -0.500000, -0.809017), 
            (0.442863, -0.238856, -0.864188), 
            (0.162460, -0.262866, -0.951056), 
            (0.238856, -0.864188, -0.442863), 
            (0.500000, -0.809017, -0.309017), 
            (0.425325, -0.688191, -0.587785), 
            (0.716567, -0.681718, -0.147621), 
            (0.688191, -0.587785, -0.425325), 
            (0.587785, -0.425325, -0.688191), 
            (0.000000, -0.955423, -0.295242), 
            (0.000000, -1.000000,  0.000000), 
            (0.262866, -0.951056, -0.162460), 
            (0.000000, -0.850651,  0.525731), 
            (0.000000, -0.955423,  0.295242), 
            (0.238856, -0.864188,  0.442863), 
            (0.262866, -0.951056,  0.162460), 
            (0.500000, -0.809017,  0.309017), 
            (0.716567, -0.681718,  0.147621), 
            (0.525731, -0.850651,  0.000000), 
            (0.238856, -0.864188, -0.442863), 
            (0.500000, -0.809017, -0.309017), 
            (0.262866, -0.951056, -0.162460), 
            (0.850651, -0.525731,  0.000000), 
            (0.716567, -0.681718, -0.147621), 
            (0.716567, -0.681718,  0.147621), 
            (0.525731, -0.850651,  0.000000), 
            (0.500000, -0.809017,  0.309017), 
            (0.238856, -0.864188,  0.442863), 
            (0.262866, -0.951056,  0.162460), 
            (0.864188, -0.442863,  0.238856), 
            (0.809017, -0.309017,  0.500000), 
            (0.688191, -0.587785,  0.425325), 
            (0.681718, -0.147621,  0.716567), 
            (0.442863, -0.238856,  0.864188), 
            (0.587785, -0.425325,  0.688191), 
            (0.309017, -0.500000,  0.809017), 
            (0.147621, -0.716567,  0.681718), 
            (0.425325, -0.688191,  0.587785), 
            (0.162460, -0.262866,  0.951056), 
            (0.442863, -0.238856,  0.864188), 
            (0.162460, -0.262866,  0.951056), 
            (0.309017, -0.500000,  0.809017), 
            (0.147621, -0.716567,  0.681718), 
            (0.000000, -0.525731,  0.850651), 
            (0.425325, -0.688191,  0.587785), 
            (0.587785, -0.425325,  0.688191), 
            (0.688191, -0.587785,  0.425325), 
            (0.955423,  0.295242,  0.000000), 
            (0.951056,  0.162460,  0.262866), 
            (1.000000,  0.000000,  0.000000), 
            (0.850651,  0.000000,  0.525731), 
            (0.955423, -0.295242,  0.000000), 
            (0.951056, -0.162460,  0.262866), 
            (0.864188,  0.442863, -0.238856), 
            (0.951056,  0.162460, -0.262866), 
            (0.809017,  0.309017, -0.500000), 
            (0.864188, -0.442863, -0.238856), 
            (0.951056, -0.162460, -0.262866), 
            (0.809017, -0.309017, -0.500000), 
            (0.681718,  0.147621, -0.716567), 
            (0.681718, -0.147621, -0.716567), 
            (0.850651,  0.000000, -0.525731), 
            (0.688191,  0.587785, -0.425325), 
            (0.587785,  0.425325, -0.688191), 
            (0.425325,  0.688191, -0.587785), 
            (0.425325, -0.688191, -0.587785), 
            (0.587785, -0.425325, -0.688191), 
            (0.688191, -0.587785, -0.425325)]

class md2_t(Structure):
    _fields_ = [('ident', c_int),
                ('version', c_int),
                ('skinwidth', c_int),
                ('skinheight', c_int),
                ('framesize', c_int),
                ('num_skins', c_int),
                ('num_xyz', c_int),
                ('num_st', c_int),
                ('num_tris', c_int),
                ('num_glcmds', c_int),
                ('num_frames', c_int),
                ('ofs_skins', c_int),
                ('ofs_st', c_int),
                ('ofs_tris', c_int),
                ('ofs_frames', c_int),
                ('ofs_glcmds', c_int),
                ('ofs_end', c_int)]


class vec3():
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.vec = []
        self.vec.append(x)
        self.vec.append(y)
        self.vec.append(z)
    
    def __getitem__(self, key):
        return self.vec[key]

    def __setitem__(self, key, value):
        self.vec[key] = value

class vertex_t():
    def __init__(self):
        self.v = [0 for i in range(3)]
        self.lightnormalindex = 0

class texCoord_t():
    def __init__(self):
        self.s = 0
        self.t = 0

class frame_t():
    def __init__(self):
        self.scale = [0 for i in range(3)]
        self.translate = [0 for i in range(3)]
        self.name = ""
        self.verts = []

class triangle_t():
    def __init__(self):
        self.index_xyz = [0 for i in range(3)]
        self.index_st = [0 for i in range(3)]

class anim_t():
    def __init__(self, first_frame=0, last_frame=0, fps=0):
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.fps = fps

class animState_t():
    def __init__(self):
        self.startframe = 0
        self.endframe = 0
        self.fps = 0
        self.curr_time = 0.0
        self.old_time = 0.0
        self.interpol = 0.0
        self.type = 0
        self.curr_frame = 0
        self.next_frame = 0

class CMD2Model():
    def __init__(self):
        self.num_frames = 0
        self.num_xyz = 0
        self.num_glcmds = 0
        
        self.m_vertices = None
        self.m_glcmds = None
        self.m_lightnormals = None

        self.m_texid = 0
        self.m_anim = animState_t()
        self.m_scale = 1.0

        self.vertlist = []

        self.SetAnim(0)

    def LoadModel(self, filename):
        f = open(filename, "rb")
        if not f:
            return False
        # Reading Header
        header = md2_t()
        f.readinto(header)

        # Verify that this is a MD2 file
        if header.ident != MD2_IDENT or header.version != MD2_VERSION:
            print("Error")
            f.close()
            return False
        
        # Initialize member variables
        self.num_frames = header.num_frames
        self.num_xyz = header.num_xyz
        self.num_glcmds = header.num_glcmds

        self.m_vertices = [vec3() for i in range(self.num_xyz * self.num_frames)]
        self.m_glcmds = [0 for i in range(self.num_glcmds)]
        self.m_lightnormals = [0 for i in range(self.num_xyz * self.num_frames)]

        frames = []

        # Reading file data
        f.seek(header.ofs_frames, 0)
        for i in range(self.num_frames):
            frame_s = frame_t()
            # Read Scale
            for j in range(3):
                value = struct.unpack('<f', f.read(4))[0]
                frame_s.scale[j] = value
            # Read Translate
            for j in range(3):
                value = struct.unpack('<f', f.read(4))[0]
                frame_s.translate[j] = value
            # Read Name
            value = f.read(16)
            frame_s.name = value
            # Read verts
            for k in range(header.num_xyz):
                vert = vertex_t()
                for j in range(3):
                    value = int.from_bytes(f.read(1), byteorder='little', signed=False)
                    vert.v[j] = value
                value = int.from_bytes(f.read(1), byteorder='little', signed=False)
                vert.lightnormalindex = value
                frame_s.verts.append(vert)

            frames.append(frame_s)
        
        f.seek(header.ofs_glcmds, 0)
        for i in range(self.num_glcmds):
            value = int.from_bytes(f.read(4), byteorder='little', signed=True)
            self.m_glcmds[i] = value

        for j in range(self.num_frames):
            for i in range(self.num_xyz):
                self.m_vertices[j*self.num_xyz + i][0] = (frames[j].verts[i].v[0] * frames[j].scale[0]) + frames[j].translate[0]
                self.m_vertices[j*self.num_xyz + i][1] = (frames[j].verts[i].v[1] * frames[j].scale[1]) + frames[j].translate[1]
                self.m_vertices[j*self.num_xyz + i][2] = (frames[j].verts[i].v[2] * frames[j].scale[2]) + frames[j].translate[2]

                self.m_lightnormals[j*self.num_xyz + i] = frames[j].verts[i].lightnormalindex

        f.close()
        return True
    
    def Interpolate(self):
        for i in range(self.num_xyz):
            curr_v = self.m_vertices[self.num_xyz * self.m_anim.curr_frame + i]
            next_v = self.m_vertices[self.num_xyz * self.m_anim.next_frame + i]
            try: 
                self.vertlist[i][0] = (curr_v[0] + self.m_anim.interpol * (next_v[0] - curr_v[0])) * self.m_scale
                self.vertlist[i][1] = (curr_v[1] + self.m_anim.interpol * (next_v[1] - curr_v[1])) * self.m_scale
                self.vertlist[i][2] = (curr_v[2] + self.m_anim.interpol * (next_v[2] - curr_v[2])) * self.m_scale
            except IndexError:
                self.vertlist.append(vec3())
                self.vertlist[i][0] = (curr_v[0] + self.m_anim.interpol * (next_v[0] - curr_v[0])) * self.m_scale
                self.vertlist[i][1] = (curr_v[1] + self.m_anim.interpol * (next_v[1] - curr_v[1])) * self.m_scale
                self.vertlist[i][2] = (curr_v[2] + self.m_anim.interpol * (next_v[2] - curr_v[2])) * self.m_scale
    
    def RenderFrame(self):
        self.Interpolate()

        cmd_pointer = 0
        while cmd_pointer < len(self.m_glcmds):
            n = self.m_glcmds[cmd_pointer]
            if n < 0:
                glBegin( GL_TRIANGLE_FAN )
                n = -n
            else:
                glBegin( GL_TRIANGLE_STRIP )
            
            for j in range(n):
                cmd_pointer += 3

                glNormal3fv( anorms[ self.m_lightnormals[ self.m_glcmds[cmd_pointer] ] ] )

                vertex = self.vertlist[ self.m_glcmds[cmd_pointer] ]
                glVertex3fv( (vertex[0], vertex[1], vertex[2]) )
            glEnd()
            cmd_pointer += 1
    
    def SetAnim(self, type_v):
        if type_v < 0 or type_v > 20:
            type_v = 0
        
        self.m_anim.startframe = animlist[type_v].first_frame
        self.m_anim.endframe = animlist[type_v].last_frame
        self.m_anim.next_frame = animlist[type_v].first_frame + 1
        self.m_anim.fps = animlist[type_v].fps
        self.m_anim.type = type_v
    
    def DrawModel(self, time):
        if time > 0.0:
            self.Animate(time)
        self.RenderFrame()

    def ScaleModel(self, s):
        self.m_scale = s

    def Animate(self, time):
        self.m_anim.curr_time = time

        if self.m_anim.curr_time - self.m_anim.old_time > (1.0/self.m_anim.fps):
            self.m_anim.curr_frame = self.m_anim.next_frame
            self.m_anim.next_frame += 1

            if self.m_anim.next_frame > self.m_anim.endframe:
                self.m_anim.next_frame = self.m_anim.startframe

            self.m_anim.old_time = self.m_anim.curr_time
        
        if self.m_anim.curr_frame > (self.num_frames - 1):
            self.m_anim.curr_frame = 0
        
        if self.m_anim.next_frame > (self.num_frames - 1):
            self.m_anim.next_frame = 0
        
        self.m_anim.interpol = self.m_anim.fps * (self.m_anim.curr_time - self.m_anim.old_time)

def load_model(filename):
    print("Loading model...")
    model = CMD2Model()
    if not model.LoadModel(filename):
        return None
    model.ScaleModel(0.01)
    print("Loaded model")
    return model

def display(model):
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
    model.DrawModel(time.time())

def define_ambient_parameters(shader):
    aColor = [0.0, 0.0, 0.5]
    lPosition = [300, 300, 300]
    lColor = [0.5, 0.5, 0.5]
    lSpecular = [1.0, 1.0, 1.0]
    mShininess = 25

    aColor = np.array(aColor, dtype = np.float32)
    lPosition = np.array(lPosition, dtype = np.float32)
    lColor = np.array(lColor, dtype = np.float32)
    lSpecular = np.array(lSpecular, dtype = np.float32)

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

animlist = []

animlist.append(anim_t(   0,  39,  9 )) 
animlist.append(anim_t(  40,  45, 10 )) 
animlist.append(anim_t(  46,  53, 10 )) 
animlist.append(anim_t(  54,  57,  7 )) 
animlist.append(anim_t(  58,  61,  7 )) 
animlist.append(anim_t(  62,  65,  7 )) 
animlist.append(anim_t(  66,  71,  7 )) 
animlist.append(anim_t(  72,  83,  7 )) 
animlist.append(anim_t(  84,  94,  7 )) 
animlist.append(anim_t(  95, 111, 10 )) 
animlist.append(anim_t( 112, 122,  7 )) 
animlist.append(anim_t( 123, 134,  6 )) 
animlist.append(anim_t( 135, 153, 10 )) 
animlist.append(anim_t( 154, 159,  7 )) 
animlist.append(anim_t( 160, 168, 10 )) 
animlist.append(anim_t( 196, 172,  7 )) 
animlist.append(anim_t( 173, 177,  5 )) 
animlist.append(anim_t( 178, 183,  7 )) 
animlist.append(anim_t( 184, 189,  7 )) 
animlist.append(anim_t( 190, 197,  7 )) 
animlist.append(anim_t( 198, 198,  5 )) 

if __name__ == "__main__":
    # Load Model
    model = load_model("Ogros.md2")

    # initialize glfw
    if not glfw.init():
        exit()

    window = glfw.create_window(800, 600, "Phong Shading", None, None)

    if not window:
        glfw.terminate()
        exit()

    glfw.make_context_current(window)

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(phong_vertex_shader, GL_VERTEX_SHADER),
                                                OpenGL.GL.shaders.compileShader(phong_fragment_shader, GL_FRAGMENT_SHADER))

    glUseProgram(shader)

    define_ambient_parameters(shader)

    # Create transformation matrices
    pers = glm.perspective(0.5,1.0,0.1,50.0)

    rot_x = glm.rotate(glm.mat4(1.0),-90.0,glm.vec3(1.0,0.0,0.0))
    rot_y = glm.rotate(glm.mat4(1.0),-90.0,glm.vec3(0.0,0.0,1.0))

    normal_matrix = glm.mat4(1.0)
    normalMatrixLoc = glGetUniformLocation(shader, "normal_matrix")
    glUniformMatrix4fv(normalMatrixLoc, 1, GL_FALSE, glm.value_ptr(normal_matrix))

    trans = glm.translate(glm.mat4(1.0), glm.vec3(0.0,0.0,-5.0))

    scale = glm.scale(glm.mat4(1.0), glm.vec3(2, 2, 2))
    
    modelViewLoc = glGetUniformLocation(shader, "model_view_matrix")
    glUniformMatrix4fv(modelViewLoc, 1, GL_FALSE, glm.value_ptr(trans*scale*rot_x*rot_y))

    modelViewProjLoc = glGetUniformLocation(shader, "model_view_projection_matrix")
    glUniformMatrix4fv(modelViewProjLoc, 1, GL_FALSE, glm.value_ptr(pers*trans*scale*rot_x*rot_y))

    while not glfw.window_should_close(window):
        glfw.poll_events()

        display(model)

        glfw.swap_buffers(window)

    glfw.terminate()
