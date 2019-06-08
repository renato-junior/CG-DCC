from math import sqrt, pi, tan
from random import random, seed
import argparse
from multiprocessing import Process, Queue, cpu_count

import sys

MAXFLOAT = float("inf")

# seed(2000)

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

    def reflect(self, other):
        return self - other*self.dot(other)*2

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
    def __init__(self, a, b, ti=0.0):
        self.A = a
        self.B = b
        self.time = ti
    
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
        self.material = None
        self.time = 0.0

    def copy(self, other):
        self.t = other.t
        self.p = other.p
        self.normal = other.normal
        self.material = other.material
        self.time = other.time

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
        temp_rec.time = r.time
        hit_anything = False
        closest_so_far = t_max
        for i in range(self.list_size):
            if self.list[i].hit(r, t_min, closest_so_far, temp_rec):
                hit_anything = True
                closest_so_far = temp_rec.t
                # rec = temp_rec
                rec.copy(temp_rec)
        return hit_anything

class sphere(hitable):
    def __init__(self, center, r, material):
        self.center = center
        self.radius = r
        self.material = material
    
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
                rec.material = self.material
                return True
            temp = (-b + sqrt(b*b - a*c))/a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.p = r.point_at_parameter(rec.t)
                rec.normal = (rec.p - self.center) / self.radius
                rec.material = self.material
                return True
        return False

class moving_sphere(hitable):
    def __init__(self, cen0, cen1, r, material, t0, t1):
        self.radius = r
        self.material = material
        self.time0 = t0
        self.time1 = t1
        self.center0 = cen0
        self.center1 = cen1
    
    def hit(self, r, t_min, t_max, rec):
        oc = r.origin() - self.center(r.time)
        a = r.direction().dot(r.direction())
        b = oc.dot(r.direction())
        c = oc.dot(oc) - self.radius*self.radius
        discriminant = b*b - a*c
        if discriminant > 0:
            temp = (-b - sqrt(b*b - a*c))/a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.p = r.point_at_parameter(rec.t)
                rec.normal = (rec.p - self.center(r.time)) / self.radius
                rec.material = self.material
                return True
            temp = (-b + sqrt(b*b - a*c))/a
            if temp < t_max and temp > t_min:
                rec.t = temp
                rec.p = r.point_at_parameter(rec.t)
                rec.normal = (rec.p - self.center(r.time)) / self.radius
                rec.material = self.material
                return True
        return False
    
    def center(self, time):
        return self.center0 + (self.center1 - self.center0)*((time - self.time0) / (self.time1 - self.time0))

class xy_rect(hitable):
    def __init__(self, x0, x1, y0, y1, k, material):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.k = k
        self.material = material
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k-r.origin().z())/r.direction().z()
        if t < t_min or t > t_max:
            return False
        x = r.origin().x() + t*r.direction().x()
        y = r.origin().y() + t*r.direction().y()
        if x < self.x0 or x > self.x1 or y < self.y0 or y > self.y1:
            return False
        rec.t = t
        rec.material = self.material
        rec.p = r.point_at_parameter(t)
        rec.normal = vec3(0,0,1)
        return True

class xz_rect(hitable):
    def __init__(self, x0, x1, z0, z1, k, material):
        self.x0 = x0
        self.x1 = x1
        self.z0 = z0
        self.z1 = z1
        self.k = k
        self.material = material
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k-r.origin().y())/r.direction().y()
        if t < t_min or t > t_max:
            return False
        x = r.origin().x() + t*r.direction().x()
        z = r.origin().z() + t*r.direction().z()
        if x < self.x0 or x > self.x1 or z < self.z0 or z > self.z1:
            return False
        rec.t = t
        rec.material = self.material
        rec.p = r.point_at_parameter(t)
        rec.normal = vec3(0,1,0)
        return True

class yz_rect(hitable):
    def __init__(self, y0, y1, z0, z1, k, material):
        self.y0 = y0
        self.y1 = y1
        self.z0 = z0
        self.z1 = z1
        self.k = k
        self.material = material
    
    def hit(self, r, t_min, t_max, rec):
        t = (self.k-r.origin().x())/r.direction().x()
        if t < t_min or t > t_max:
            return False
        y = r.origin().y() + t*r.direction().y()
        z = r.origin().z() + t*r.direction().z()
        if z < self.z0 or z > self.z1 or y < self.y0 or y > self.y1:
            return False
        rec.t = t
        rec.material = self.material
        rec.p = r.point_at_parameter(t)
        rec.normal = vec3(1,0,0)
        return True

class flip_normals(hitable):
    def __init__(self, p):
        self.ptr = p
    
    def hit(self, r, t_min, t_max, rec):
        if self.ptr.hit(r, t_min, t_max, rec):
            rec.normal = -rec.normal
            return True
        return False

class box(hitable):
    def __init__(self, p0, p1, material):
        self.pmin = p0
        self.pmax = p1
        h_list = []
        h_list.append(xy_rect(p0.x(), p1.x(), p0.y(), p1.y(), p1.z(), material))
        h_list.append(flip_normals(xy_rect(p0.x(), p1.x(), p0.y(), p1.y(), p0.z(), material)))
        h_list.append(xz_rect(p0.x(), p1.x(), p0.z(), p1.z(), p1.y(), material))
        h_list.append(flip_normals(xz_rect(p0.x(), p1.x(), p0.z(), p1.z(), p0.y(), material)))
        h_list.append(yz_rect(p0.y(), p1.y(), p0.z(), p1.z(), p1.x(), material))
        h_list.append(flip_normals(yz_rect(p0.y(), p1.y(), p0.z(), p1.z(), p0.x(), material)))
        self.hit_list = hitable_list(h_list, 6)
    
    def hit(self, r, t_min, t_max, rec):
        return self.hit_list.hit(r, t_min, t_max, rec)

class camera():
    def __init__(self, lookfrom, lookat, vup, vfov, aspect, aperture, focus_dist, t0, t1):
        self.lens_radius = aperture/2
        theta = vfov*pi/180
        half_height = tan(theta/2)
        half_width = aspect * half_height
        self.origin = lookfrom
        self.w = (lookfrom - lookat).unit_vector()
        self.u = (vup.cross(self.w)).unit_vector()
        self.v = self.w.cross(self.u)
        self.lower_left_corner = self.origin - self.u*half_width*focus_dist - self.v*half_height*focus_dist - self.w*focus_dist
        self.horizontal = self.u*2*half_width*focus_dist
        self.vertical = self.v*2*half_height*focus_dist
        self.time0 = t0
        self.time1 = t1

    def get_ray(self, s, t):
        rd = random_in_unit_disk()*self.lens_radius
        offset = self.u*rd.x() + self.v*rd.y()
        time = self.time0 + random()*(self.time1-self.time0)
        return ray(self.origin + offset, self.lower_left_corner + self.horizontal*s + self.vertical*t - self.origin - offset, time)

class material():
    def scatter(self, r_in, rec):
        pass

class lambertian(material):
    def __init__(self, a):
        self.albedo = a

    def scatter(self, r_in, rec):
        target = rec.p + rec.normal +random_in_unit_sphere()
        scattered = ray(rec.p, target-rec.p, rec.time)
        attenuation = self.albedo
        return True, attenuation, scattered

class metal(material):
    def __init__(self, a, f):
        self.albedo = a
        self.fuzz = f if f < 1.0 else 1.0

    def scatter(self, r_in, rec):
        reflected = r_in.direction().unit_vector().reflect(rec.normal)
        scattered = ray(rec.p, reflected + random_in_unit_sphere()*self.fuzz, rec.time)
        attenuation = self.albedo
        return (scattered.direction().dot(rec.normal) > 0), attenuation, scattered

class dieletric(material):
    def __init__(self, ri):
        self.ref_idx = ri

    def scatter(self, r_in, rec):
        reflected = r_in.direction().reflect(rec.normal)
        attenuation = vec3(1.0, 1.0, 1.0)
        if r_in.direction().dot(rec.normal) > 0:
            outward_normal = -rec.normal
            ni_over_nt = self.ref_idx
            cosine = self.ref_idx * r_in.direction().dot(rec.normal) / r_in.direction().length()
        else:
            outward_normal = rec.normal
            ni_over_nt = 1.0 / self.ref_idx
            cosine = -(r_in.direction().dot(rec.normal)) / r_in.direction().length()
        refracted_bool, refracted = refract(r_in.direction(), outward_normal, ni_over_nt)
        if refracted_bool:
            reflect_prob = schlick(cosine, self.ref_idx)
        else:
            reflect_prob = 1.0
        if random() < reflect_prob:
            scattered = ray(rec.p, reflected, rec.time)
        else:
            scattered = ray(rec.p, refracted, rec.time)
        return True, attenuation, scattered

def random_in_unit_disk():
    p = vec3(random(), random(), 0.0)*2.0 - vec3(1, 1, 0)
    while p.dot(p) >= 1.0:
        p = vec3(random(), random(), 0.0)*2.0 - vec3(1, 1, 0)
    return p   

def random_in_unit_sphere():
    p = vec3(random(), random(), random())*2.0 - vec3(1, 1, 1)
    while p.squared_length() >= 1.0:
        p = vec3(random(), random(), random())*2.0 - vec3(1, 1, 1)
    return p

def refract(v, n, ni_over_nt):
    uv = v.unit_vector()
    dt = uv.dot(n)
    discriminant = 1.0 - ni_over_nt*ni_over_nt*(1-dt*dt)
    if discriminant > 0:
        refracted = (uv - n*dt)*ni_over_nt - n*sqrt(discriminant)
        return True, refracted
    return False, None

def schlick(cosine, ref_idx):
    r0 = (1-ref_idx) / (1+ref_idx)
    r0 = r0**2
    return r0 + (1-r0)*((1-cosine)**5)

def color(r, world, depth):
    rec = hit_record()
    if world.hit(r, 0.001, MAXFLOAT, rec):
        if depth < 50:
            scatter, attenuation, scattered = rec.material.scatter(r, rec)
            if scatter:
                return attenuation*color(scattered, world, depth+1)
        return vec3(0,0,0)
    else:
        unit_direction = r.direction().unit_vector()
        t = 0.5*(unit_direction.y() + 1.0)
        return vec3(1.0, 1.0, 1.0)*(1.0-t) + vec3(0.5, 0.7, 1.0)*t

def random_scene():
    n = 500
    h_list = []
    h_list.append(sphere(vec3(0, -1000, 0), 1000, lambertian(vec3(0.5, 0.5, 0.5))))
    i = 1
    for a in range(-11, 11):
        for b in range(-11, 11):
            choose_mat = random()
            center = vec3(a+0.9*random(), 0.2, b+0.9*random())
            if (center-vec3(4, 0.2, 0)).length() > 0.9:
                if choose_mat < 0.8: # diffuse
                    mov_prob = random()
                    if mov_prob < 0.6:
                        h_list.append(sphere(center, 0.2, lambertian(vec3(random()*random(), random()*random(), random()*random()))))
                    else:
                        h_list.append(moving_sphere(center, center+vec3(0,0.5*random(),0), 0.2, lambertian(vec3(random()*random(), random()*random(), random()*random())), 0.0, 1.0))
                    i += 1
                elif choose_mat < 0.95: # metal
                    h_list.append(sphere(center, 0.2, metal(vec3(0.5*(1 + random()), 0.5*(1 + random()), 0.5*(1 + random())), 0.5*random())))
                    i += 1
                else: # glass
                    h_list.append(sphere(center, 0.2, dieletric(1.5)))
                    i += 1
    h_list.append(sphere(vec3(0, 1, 0), 1.0, dieletric(1.5)))
    h_list.append(sphere(vec3(-4, 1, 0), 1.0, lambertian(vec3(0.4, 0.2, 0.1))))
    h_list.append(sphere(vec3(4, 1, 0), 1.0, metal(vec3(0.7, 0.6, 0.5), 0.0)))
    i += 3
    return hitable_list(h_list, i)

def create_ppm_file(filename, nx, ny):
    ppm_file = open(filename, "w")
    ppm_file.write("P3\n")
    ppm_file.write("{} {}\n".format(nx, ny))
    ppm_file.write("255\n")
    return ppm_file

def write_ppm(filename, width, height, rays, multicore=False):
    nx = width
    ny = height
    ns = rays
    
    hit_list = []
    # hit_list.append(sphere(vec3(0.0, 0.0, -1.0), 0.5, lambertian(vec3(0.1, 0.2, 0.5))))
    hit_list.append(box(vec3(-0.25,-0.25,-1), vec3(0.25,0.25,0), lambertian(vec3(0.1, 0.2, 0.5))))
    # hit_list.append(moving_sphere(vec3(0.0, 0.0, -1.0), vec3(0.0, 0.25, 0.0), 0.5, lambertian(vec3(0.1, 0.2, 0.5)), 0.0, 1.0))
    hit_list.append(sphere(vec3(0.0, -100.5, -1.0), 100.0, lambertian(vec3(0.8, 0.8, 0.0))))
    hit_list.append(sphere(vec3(1.0, 0.0, -1.0), 0.5, metal(vec3(0.8, 0.6, 0.2), 0.0)))
    hit_list.append(sphere(vec3(-1.0, 0.0, -1.0), 0.5, dieletric(1.5)))
    # hit_list.append(xy_rect(0, 2, 0, 2, -3, lambertian(vec3(0,0,1))))
    world = hitable_list(hit_list, 4)

    lookfrom = vec3(0.0, 1.0, 4.5)
    lookat = vec3(0, 0, -1)
    dist_to_focus = 2.0
    aperture = 0.01
    cam = camera(lookfrom, lookat, vec3(0, 1, 0), 30, float(nx)/float(ny), aperture, dist_to_focus, 0.0, 1.0)

    # hit_list = []
    # # hit_list.append(sphere(vec3(0.0, 0.0, -1.0), 0.5, lambertian(vec3(0.1, 0.2, 0.5))))
    # hit_list.append(moving_sphere(vec3(0.0, 0.0, -1.0), vec3(0.0, 0.25, 0.0), 0.5, lambertian(vec3(0.1, 0.2, 0.5)), 0.0, 1.0))
    # hit_list.append(sphere(vec3(0.0, -100.5, -1.0), 100.0, lambertian(vec3(0.8, 0.8, 0.0))))
    # hit_list.append(sphere(vec3(1.0, 0.0, -1.0), 0.5, metal(vec3(0.8, 0.6, 0.2), 0.0)))
    # hit_list.append(sphere(vec3(-1.0, 0.0, -1.0), 0.5, dieletric(1.5)))
    # world = hitable_list(hit_list, 4)

    # lookfrom = vec3(-4, 1.0, 0.5)
    # lookat = vec3(0, 0, -1)
    # dist_to_focus = 2.0
    # aperture = 0.01
    # cam = camera(lookfrom, lookat, vec3(0, 1, 0), 30, float(nx)/float(ny), aperture, dist_to_focus, 0.0, 1.0)

    # world = random_scene()

    # lookfrom = vec3(13, 2, 3)
    # lookat = vec3(0, 0, 0)
    # dist_to_focus = 10.0
    # aperture = 0.1
    # cam = camera(lookfrom, lookat, vec3(0, 1, 0), 20, float(nx)/float(ny), aperture, dist_to_focus, 0.0, 1.0)

    if multicore:
        ppm_file = create_ppm_file(filename, nx, ny)
        process_multi_core(ppm_file, nx, ny, ns, world, cam)
        ppm_file.close()
    else:
        run_sub_image(0, nx, 0, ny, nx, ny, ns, world, cam, filename)

def process_multi_core(ppm_file, nx, ny, ns, world, cam):
    # Get number of cores
    n_cores = cpu_count()
    
    # Divide image in number of cores slices
    divisions_in_x = n_cores//int(sqrt(n_cores))
    divisions_in_y = n_cores//divisions_in_x

    size_div_x = nx//divisions_in_x
    size_div_y = ny//divisions_in_y

    procs = []

    n_p = 0
    for i in range(divisions_in_y-1, -1, -1):
        sy = i*size_div_y
        if i != divisions_in_y-1:
            ey = (i+1)*size_div_y
        else:
            ey = ny
        for j in range(divisions_in_x):
            sx = j*size_div_x
            if j != divisions_in_x-1:
                ex = (j+1)*size_div_x
            else:
                ex = nx
            # Create a process
            p = Process(target=run_sub_image, args=(sx, ex, sy, ey, nx, ny, ns, world, cam, "{}.ppm".format(n_p)))
            procs.append(p)
            p.start()
            n_p+=1

    for p in procs: # Wait for all the created process to finish
        p.join()
    
    print("Ended processing")
    print("Starting writing result")
    sys.stdout.flush()

    # Combine generated images to create the final image
    n_file = 0
    for i in range(divisions_in_y-1, -1, -1):
        files_list = []
        for j in range(divisions_in_x):
            sub_ppm = open("{}.ppm".format(n_file), "r")
            sub_ppm.readline()
            sub_ppm.readline()
            sub_ppm.readline()
            n_file += 1
            files_list.append(sub_ppm)
        
        sy = i*size_div_y
        if i != divisions_in_y-1:
            ey = (i+1)*size_div_y
        else:
            ey = ny
        lines_qty = ey-sy
        for ii in range(lines_qty):
            for jj in range(divisions_in_x):
                sx = jj*size_div_x
                if jj != divisions_in_x-1:
                    ex = (jj+1)*size_div_x
                else:
                    ex = nx
                for k in range(ex-sx):
                    ppm_file.write(files_list[jj].readline())
            
        for f in files_list:
            f.close()

def run_sub_image(sx, ex, sy, ey, nx, ny, ns, world, cam, ppm_name):
    ppm_file = create_ppm_file(ppm_name, ex-sx, ey-sy)
    for j in range(ey-1, sy-1, -1):
        for i in range(sx, ex):
            col = vec3(0, 0, 0)
            for s in range(ns):
                u = float(i+random())/float(nx)
                v = float(j+random())/float(ny)
                r = cam.get_ray(u, v)
                p = r.point_at_parameter(2.0)
                col += color(r, world, 0)
            col /= float(ns)
            col = vec3(sqrt(col[0]), sqrt(col[1]), sqrt(col[2]))
            ir = int(255.99*col[0])
            ig = int(255.99*col[1])
            ib = int(255.99*col[2])
            ppm_file.write("{} {} {}\n".format(ir, ig, ib))
    print("end proc", ppm_name, sx, ex, sy, ey)
    ppm_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ray Tracer.')
    parser.add_argument('filename', help="Name of output file. (e.g. img.ppm)")
    parser.add_argument('--width', default=480, type=int, help="The width of the generated image.")
    parser.add_argument('--height', default=340, type=int, help="The height of the generated image.")
    parser.add_argument('--rays', default=10, type=int, help="The number of rays to be cast per pixel.")
    parser.add_argument('--multicore', action='store_true', default=False, help="Run the algorithm on multiple cores. If false, the algorithm will run on a single core.")
    args = parser.parse_args()
    
    write_ppm(args.filename, args.width, args.height, args.rays, args.multicore)
