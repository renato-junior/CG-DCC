from ctypes import *

MD2_IDENT = 844121161
MD2_VERSION = 8

NUMVERTEXNORMALS = 0
SHADEDOT_QUANT = 0

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

class vertex():
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
        self.verts = None

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

class CMD2Model():
    def __init__(self):
        self.anorms = [vec3() for i in range(NUMVERTEXNORMALS)]
        self.anorms_dots = [[ 0.0 for j in range(256)] for i in range(SHADEDOT_QUANT)]
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

    def LoadModel(self, filename):
        f = open(filename, "rb")
        if not f:
            return False
        # Reading Header
        header = md2_t()
        f.readinto(header) == sizeof(header)

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

        buffer = [0 for i in range(self.num_frames * header.framesize)]

        # Reading file data
        f.seek(header.ofs_frames, 0)
        for i in range(self.num_frames * header.framesize):
            value = int.from_bytes(f.read(1), byteorder='little', signed=True)
            # print(value)
            buffer[i] = value
        
        f.seek(header.ofs_glcmds, 0)
        print(header.ofs_glcmds, header.ofs_end)
        for i in range(self.num_glcmds):
            value = int.from_bytes(f.read(4), byteorder='little', signed=True)
            # print(value)
            self.m_glcmds[i] = value

        # Vertex array initialization
        # for j in range(self.num_frames):


        f.close()
    
if __name__ == '__main__':
    cmd2model = CMD2Model()
    cmd2model.LoadModel("horse/horse.md2")

    



