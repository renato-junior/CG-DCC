
def write_ppm(filename):
    ppm_file = open(filename, "w")
    nx = 200
    ny = 100
    ppm_file.write("P3\n")
    ppm_file.write("{} {}\n".format(nx, ny))
    ppm_file.write("255\n")
    for j in range(ny-1, -1, -1):
        for i in range(nx):
            r = float(i)/float(nx)
            g = float(j)/float(ny)
            b = 0.2
            ir = int(255.99*r)
            ig = int(255.99*g)
            ib = int(255.99*b)
            ppm_file.write("{} {} {}\n".format(ir, ig, ib))


if __name__ == "__main__":
    write_ppm("img.ppm")