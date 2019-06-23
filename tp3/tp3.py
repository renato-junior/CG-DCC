from ctypes import *
import struct
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

MD2_IDENT = 844121161
MD2_VERSION = 8
MAX_MD2_VERTS = 10000000

NUMVERTEXNORMALS = 162
SHADEDOT_QUANT = 16

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
    def __init__(self):
        self.first_frame = 0
        self.last_frame = 0
        self.fps = 0

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

g_lightcolor    = [1.0, 1.0, 1.0]
g_ambientlight  = 32
g_shadelight    = 128
g_angle         = 0.0
lcolor          = vec3()

class CMD2Model():
    def __init__(self):
        self.anorms = [vec3() for i in range(NUMVERTEXNORMALS)]
        # self.anorms_dots = [[ 0.0 for j in range(256)] for i in range(SHADEDOT_QUANT)]
        self.animlist = [anim_t() for i in range(21)]

        self.num_frames = 0
        self.num_xyz = 0
        self.num_glcmds = 0
        
        self.m_vertices = None
        self.m_glcmds = None
        self.m_lightnormals = None

        self.m_texid = 0
        self.m_anim = animState_t()
        self.m_scale = 1.0

        # self.SetAnim(0)

        self.vertlist = [vec3() for i in range(MAX_MD2_VERTS)]

        self.anorms =  [(0.525731,  0.000000,  0.850651), 
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
        print(header.framesize)
        for i in range(self.num_frames):
            frame_s = frame_t()
            # Read Scale
            for j in range(3):
                value = struct.unpack('<f', f.read(4))
                frame_s.scale[j] = value
            # Read Translate
            for j in range(3):
                value = struct.unpack('<f', f.read(4))
                frame_s.translate[j] = value
            # Read Name
            value = f.read(16)
            print(value)
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
        print(header.ofs_glcmds, header.ofs_end)
        for i in range(self.num_glcmds):
            value = int.from_bytes(f.read(4), byteorder='little', signed=True)
            # print(value)
            self.m_glcmds[i] = value

        for j in range(self.num_frames):
            for i in range(self.num_xyz):
                self.m_vertices[i][0] = (frames[j].verts[i].v[0] * frames[j].scale[0]) + frames[j].translate[0]
                self.m_vertices[i][1] = (frames[j].verts[i].v[1] * frames[j].scale[1]) + frames[j].translate[1]
                self.m_vertices[i][2] = (frames[j].verts[i].v[2] * frames[j].scale[2]) + frames[j].translate[2]

                self.m_lightnormals[i] = frames[j].verts[i].lightnormalindex

        f.close()
        return True
    
    # def LoadSkin(filename):
    #     self.m_texid = LoadTexture(filename)
    #     return (m_texid != self.LoadTexture("default"))

    def DrawModel(self, time):
        glPushMatrix()
        glRotatef( -90.0, 1.0, 0.0, 0.0 )
        glRotatef( -90.0, 0.0, 0.0, 1.0 )
        self.RenderFrame()
        glPopMatrix()
    
    def Interpolate(self, vertlist):
        for i in range(self.num_xyz):
            vertlist[i][0] = self.m_vertices[ i + (self.num_xyz * self.m_anim.curr_frame) ][0] * self.m_scale;
            vertlist[i][1] = self.m_vertices[ i + (self.num_xyz * self.m_anim.curr_frame) ][1] * self.m_scale;
            vertlist[i][2] = self.m_vertices[ i + (self.num_xyz * self.m_anim.curr_frame) ][2] * self.m_scale;

    def ProcessLighting(self):
        global lcolor

        lightvar = float(((g_shadelight + g_ambientlight)/256.0))

        lcolor[0] = g_lightcolor[0] * lightvar
        lcolor[1] = g_lightcolor[1] * lightvar
        lcolor[2] = g_lightcolor[2] * lightvar

        # shadedots = self.anorms_dots[ ((int)(g_angle * (SHADEDOT_QUANT / 360.0))) & (SHADEDOT_QUANT - 1) ];
    
    def RenderFrame(self):
        glPushAttrib( GL_POLYGON_BIT )
        glFrontFace( GL_CW )

        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

        self.ProcessLighting()

        # self.Interpolate( self.vertlist )

        # glBindTexture( GL_TEXTURE_2D, m_texid )

        for i in range(0, len(self.m_glcmds), 3):
            i_val = self.m_glcmds[i]
            if i_val < 0:
                glBegin( GL_TRIANGLE_FAN )
                i_val = -i_val
            else:
                glBegin( GL_TRIANGLE_STRIP )
            while True:
                if i_val <= 0:
                    break
                
                # l = shadedots[ m_lightnormals[ ptricmds[2] ] ]
                l = 1.0
                glColor3f( l * lcolor[0], l * lcolor[1], l * lcolor[2] )

                # glTexCoord2f( ((float *)ptricmds)[0], ((float *)ptricmds)[1] )

                glNormal3fv( self.anorms[ self.m_lightnormals[ self.m_glcmds[i+2] ] ] )

                glVertex3fv( self.vertlist[ self.m_glcmds[i+2] ] )
            glEnd()    
        
        glDisable( GL_CULL_FACE )
        glPopAttrib()


glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(800, 600)
glutInitWindowPosition(100, 100)
glutCreateWindow("hello")

glClearColor(1, 1, 1, 0)
cmd2model = CMD2Model()
cmd2model.LoadModel("horse/horse.md2")


glutDisplayFunc(cmd2model.RenderFrame())
glutMainLoop()


    
# if __name__ == '__main__':
#     cmd2model = CMD2Model()
#     cmd2model.LoadModel("horse/horse.md2")

    



