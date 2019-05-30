from math import sqrt
from random import random

MAXFLOAT = 99999999999999

class vec3():
    def __init__(self, e0, e1, e2):
        self.e = [0 for x in range(3)]
        self.e[0] = float(e0)
        self.e[1] = float(e1)
        self.e[2] = float(e2)

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
    
    def unit_vector(self):
        return self/self.length()

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
        if isinstance(other, float) or isinstance(other, int):
            self.e[0] *= other
            self.e[1] *= other
            self.e[2] *= other
        elif isinstance(other, vec3):
            self.e[0] *= other.e[0]
            self.e[1] *= other.e[1]
            self.e[2] *= other.e[2]
        return self
    
    def __itruediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            k = 1.0/other
            self.e[0] *= k
            self.e[1] *= k
            self.e[2] *= k
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
        if isinstance(other, float) or isinstance(other, int):
            return vec3(self.e[0]*other, self.e[1]*other, self.e[2]*other)
        elif isinstance(other, vec3):
            return vec3(self.e[0]*other.e[0], self.e[1]*other.e[1], self.e[2]*other.e[2])
    
    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return vec3(self.e[0]/other, self.e[1]/other, self.e[2]/other)
        elif isinstance(other, vec3):
            return vec3(self.e[0]/other.e[0], self.e[1]/other.e[1], self.e[2]/other.e[2])

class ray():
    def __init__(self, a, b):
        self.A = a
        self.B = b
    
    def origin(self):
        return self.A
    
    def direction(self):
        return self.B
    
    def point_at_parameter(self, t):
        return self.A + self.B*t

class hit_record():
    def __init__(self):
        self.t = 0.0
        self.p = None
        self.normal = None

    def __str__(self):
        return "t: {}, p: {}, normal: {}".format(self.t, str(self.p), str(self.normal))

class hitable():
    def hit(self, r, t_min, t_max, rec):
        pass

class hitable_list(hitable):
    def __init__(self, l, n):
        self.list = l
        self.list_size = n
    
    def hit(self, r, t_min, t_max, rec):
        temp_rec = hit_record()
        hit_anything = False
        closest_so_far = t_max
        for i in range(self.list_size):
            if self.list[i].hit(r, t_min, closest_so_far, temp_rec):
                hit_anything = True
                closest_so_far = temp_rec.t
                # rec = temp_rec
                rec.t = temp_rec.t
                rec.p = temp_rec.p
                rec.normal = temp_rec.normal
        return hit_anything

class sphere(hitable):
    def __init__(self, center, r):
        self.center = center
        self.radius = r
    
    def hit(self, r, t_min, t_max, rec):
        oc = r.origin() - self.center
        a = r.direction().dot(r.direction())
        b = oc.dot(r.direction())
        c = oc.dot(oc) - self.radius*self.radius
        discriminant = b*b - a*c
        if discriminant > 0:
            temp = (-b - sqrt(b*b - a*c))/a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.p = r.point_at_parameter(rec.t)
                rec.normal = (rec.p - self.center) / self.radius
                return True
            temp = (-b + sqrt(b*b - a*c))/a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.p = r.point_at_parameter(rec.t)
                rec.normal = (rec.p - self.center) / self.radius
                return True
        return False

class camera():
    def __init__(self):
        self.lower_left_corner = vec3(-2.0, -1.0, -1.0)
        self.horizontal = vec3(4.0, 0.0, 0.0)
        self.vertical = vec3(0.0, 2.0, 0.0)
        self.origin = vec3(0.0, 0.0, 0.0)

    def get_ray(self, u, v):
        return ray(self.origin, self.lower_left_corner + self.horizontal*u + self.vertical*v - self.origin)
    
def color(r, world):
    rec = hit_record()
    if world.hit(r, 0.0, MAXFLOAT, rec):
        return vec3(rec.normal.x()+1, rec.normal.y()+1, rec.normal.z()+1)*0.5
    else:
        unit_direction = r.direction().unit_vector()
        t = 0.5*(unit_direction.y() + 1.0)
        return vec3(1.0, 1.0, 1.0)*(1.0-t) + vec3(0.5, 0.7, 1.0)*t

def write_ppm(filename):
    nx = 200
    ny = 100
    ns = 100

    ppm_file = open(filename, "w")
    ppm_file.write("P3\n")
    ppm_file.write("{} {}\n".format(nx, ny))
    ppm_file.write("255\n")
    
    hit_list = []
    hit_list.append(sphere(vec3(0.0, 0.0, -1.0), 0.5))
    hit_list.append(sphere(vec3(0.0, -100.5, -1.0), 100.0))
    world = hitable_list(hit_list, 2)

    cam = camera()

    for j in range(ny-1, -1, -1):
        for i in range(nx):
            col = vec3(0, 0, 0)
            for s in range(ns):
                u = float(i+random())/float(nx)
                v = float(j+random())/float(ny)
                r = cam.get_ray(u, v)
                p = r.point_at_parameter(2.0)
                col += color(r, world)
            col /= float(ns)
            ir = int(255.99*col[0])
            ig = int(255.99*col[1])
            ib = int(255.99*col[2])
            ppm_file.write("{} {} {}\n".format(ir, ig, ib))


def test(rec):
    rec.normal = "ola"

if __name__ == "__main__":
    write_ppm("img.ppm")
    # rec = hit_record()
    # print(rec.normal)
    # test(rec)
    # print(rec.normal)
