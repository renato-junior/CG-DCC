from math import sqrt

class vec3():
    def __init__(self, e0, e1, e2):
        self.e = [0 for x in range(3)]
        self.e[0] = e0
        self.e[1] = e1
        self.e[2] = e2

    def x(self):
        return self.e[0]
    
    def y(self):
        return self.e[1]
    
    def z(self):
        return self.e[2]
    
    def r(self):
        return self.e[0]
    
    def g(self):
        return self.e[1]

    def b(self):
        return self.e[2]

    def length(self):
        return sqrt(self.e[0]**2 + self.e[1]**2 + self.e[2]**2)
    
    def squared_length(self):
        return self.e[0]**2 + self.e[1]**2 + self.e[2]**2

    def make_unit_vector(self):
        k = 1.0 / sqrt(self.e[0]**2 + self.e[1]**2 + self.e[2]**2)
        self.e[0] *= k
        self.e[1] *= k
        self.e[2] *= k

    def dot(self, other):
        return self.e[0]*other.e[0] + self.e[1]*other.e[1] + self.e[2]*other.e[2]
    
    def cross(self, other):
        return vec3((self.e[1]*other.e[2] - self.e[2]*other.e[1]),
                    (-(self.e[0]*other.e[2] - self.e[2]*other.e[0])),
                    (self.e[0]*other.e[1] - self.e[1]*other.e[0]))
    
    def unit_vector(self, v):
        return v/v.length()

    # Override methods
    def __str__(self):
        return "({}, {}, {})".format(self.e[0], self.e[1], self.e[2])

    def __pos__(self):
        return self
    
    def __neg__(self):
        return vec3(-self.e[0], -self.e[1], -self.e[2])

    def __getitem__(self, key):
        return self.e[key]

    def __setitem__(self, key, value):
        self.e[key] = value

    def __iadd__(self, other):
        self.e[0] += other.e[0]
        self.e[1] += other.e[1]
        self.e[2] += other.e[2]
        return self
    
    def __isub__(self, other):
        self.e[0] -= other.e[0]
        self.e[1] -= other.e[1]
        self.e[2] -= other.e[2]
        return self
    
    def __imul__(self, other):
        if isinstance(other, float):
            self.e[0] *= other
            self.e[1] *= other
            self.e[2] *= other
        elif isinstance(other, vec3):
            self.e[0] *= other.e[0]
            self.e[1] *= other.e[1]
            self.e[2] *= other.e[2]
        return self
    
    def __itruediv__(self, other):
        if isinstance(other, float):
            k = 1.0/other
            self.e[0] /= k
            self.e[1] /= k
            self.e[2] /= k
        elif isinstance(other, vec3):
            self.e[0] /= other.e[0]
            self.e[1] /= other.e[1]
            self.e[2] /= other.e[2]
        return self
    
    def __add__(self, other):
        return vec3(self.e[0]+other.e[0], self.e[1]+other.e[1], self.e[2]+other.e[2])

    def __sub__(self, other):
        return vec3(self.e[0]-other.e[0], self.e[1]-other.e[1], self.e[2]-other.e[2])
    
    def __mul__(self, other):
        if isinstance(other, float):
            return vec3(self.e[0]*other, self.e[1]*other, self.e[2]*other)
        elif isinstance(other, vec3):
            return vec3(self.e[0]*other.e[0], self.e[1]*other.e[1], self.e[2]*other.e[2])
    
    def __truediv__(self, other):
        if isinstance(other, float):
            return vec3(self.e[0]/other, self.e[1]/other, self.e[2]/other)
        elif isinstance(other, vec3):
            return vec3(self.e[0]/other.e[0], self.e[1]/other.e[1], self.e[2]/other.e[2])

def write_ppm(filename):
    ppm_file = open(filename, "w")
    nx = 200
    ny = 100
    ppm_file.write("P3\n")
    ppm_file.write("{} {}\n".format(nx, ny))
    ppm_file.write("255\n")
    for j in range(ny-1, -1, -1):
        for i in range(nx):
            col = vec3(float(i)/float(nx), float(j)/float(ny), 0.2)
            ir = int(255.99*col[0])
            ig = int(255.99*col[1])
            ib = int(255.99*col[2])
            ppm_file.write("{} {} {}\n".format(ir, ig, ib))


if __name__ == "__main__":
    write_ppm("img.ppm")
