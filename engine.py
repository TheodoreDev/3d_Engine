import os
from lib_math import *

width, height = os.get_terminal_size()
pixel_buffer = [' '] * (width * height)

class Camera:
    def __init__(self, pos, pitch, yaw, flength=1) -> None:
        self.pos = pos
        self.pitch = pitch
        self.yaw = yaw
        self.flength = flength

    def getLookAtDir(self):
        return vec3(
            -sin(self.yaw)*cos(self.pitch),
            sin(self.pitch),
            cos(self.yaw)*cos(self.pitch)
        )

    def get_forward_direction(self):
        return vec3(-sin(self.yaw), 0, cos(self.yaw))

    def get_right_direction(self):
        return vec3(cos(self.yaw), 0, sin(self.yaw))

class LightSource:
    def __init__(self, position) -> None:
        self.position = position

def draw():
    print(''.join(pixel_buffer), end='')

def reset(char):
    for i in range(width * height):
        pixel_buffer[i] = char

def placePixel(v, char):
    px = round(v.x)
    py = round(v.y)
    if 0 <= px < width and 0 <= py < height:
        pixel_buffer[py * width + px] = char

def placeTriangle(tri, char):
    def eq(p, a, b):
        return (a.x - p.x)*(b.y - p.y) - (a.y - p.y)*(b.x - p.x)

    xmin = round(min(tri.v1.x, tri.v2.x, tri.v3.x))
    xmax = round(max(tri.v1.x, tri.v2.x, tri.v3.x)) + 1
    ymin = round(min(tri.v1.y, tri.v2.y, tri.v3.y))
    ymax = round(max(tri.v1.y, tri.v2.y, tri.v3.y)) + 1

    for y in range(ymin, ymax):
        if 0<=y<height:
            for x in range(xmin, xmax):
                if 0<=x<width:
                    pos = vec2(x, y)

                    w1 = eq(pos, tri.v3, tri.v1)
                    w2 = eq(pos, tri.v1, tri.v2)
                    w3 = eq(pos, tri.v2, tri.v3)

                    if (w1>=0 and w2>=0 and w3>=0) or (-w1>=0 and -w2>=0 and -w3>=0):
                        placePixel(pos, char)

def clip(triangle, cam_pos, plane_norm):
    def inZ(plane_norm, plane_point, triangle):
        out = []
        in_ = []

        vert1 = dot(plane_point-triangle.v1, plane_norm)
        vert2 = dot(plane_point-triangle.v2, plane_norm)
        vert3 = dot(plane_point-triangle.v3, plane_norm)

        out.append(triangle.v1) if vert1 > 0 else in_.append(triangle.v1)
        out.append(triangle.v2) if vert2 > 0 else in_.append(triangle.v2)
        out.append(triangle.v3) if vert3 > 0 else in_.append(triangle.v3)

        return out, in_, vert1*vert3>0

    zNear = cam_pos + 0.1*plane_norm
    out, in_, is_inverted = inZ(plane_norm, zNear, triangle)

    if len(out) == 0:
        return [triangle]
    elif len(out) == 3:
        return []
    elif len(out) == 1:
        col0 = linePlaneCol(plane_norm, zNear, out[0], in_[0])
        col1 = linePlaneCol(plane_norm, zNear, out[0], in_[1])
        if is_inverted:
            return [
                Triangle3D(col1, in_[1], col0),
                Triangle3D(col0, in_[1], in_[0])
            ]
        else:
            return [
                Triangle3D(col0, in_[0], col1),
                Triangle3D(col1, in_[0], in_[1])
            ]
    elif len(out) == 2:
        if is_inverted:
            return [
                Triangle3D(linePlaneCol(plane_norm, zNear, out[0], in_[0]),
                           in_[0],
                           linePlaneCol(plane_norm, zNear, out[1], in_[0]))
            ]
        else:
            return [
                Triangle3D(linePlaneCol(plane_norm, zNear, out[0], in_[0]),
                           linePlaneCol(plane_norm, zNear, out[1], in_[0]),
                           in_[0])
            ]

light_gradient = ".,;la#@"

def diffuseLight(light:LightSource, normal, v) -> str:
    light_dir = light.position - v
    intensity = dot(light_dir.normalize(), normal.normalize())
    return light_gradient[round(intensity*(len(light_gradient)-1))] if intensity >= 0 else light_gradient[0]

def loadObj(file_path):
    with open(file_path, "r") as file:
        lines = [line.rstrip('\n').split(' ') for line in file.readlines() if line.rstrip('\n')]

        vertices = []
        faces = []

        for line in lines:
            if line[0] == 'v':
                vertex = list(map(float, line[1:]))
                vertices.append(vec3(vertex[0], vertex[1], vertex[2]))
            if line[0] == 'f':
                faces.append(list(map(int, line[1:])))

        triangles = []
        for face in faces:
            if len(face) == 3:
                triangles.append(Triangle3D(vertices[face[0]-1], vertices[face[1]-1], vertices[face[2]-1]))
            if len(face) == 4:
                triangles.append(Triangle3D(vertices[face[0] - 1], vertices[face[1] - 1], vertices[face[2] - 1]))
                triangles.append(Triangle3D(vertices[face[2] - 1], vertices[face[3] - 1], vertices[face[0] - 1]))

        return triangles

def placeMesh(mesh:list[Triangle3D], cam:Camera, light:LightSource):

    def distTriangleCamera(triangle) -> float:
        position = (1/3)*(triangle.v1+triangle.v2+triangle.v3) - cam.pos
        return position.length()

    mesh.sort(key=distTriangleCamera, reverse=True)

    cam_look = cam.getLookAtDir()

    for triangle in mesh:
        clipped_triangle_list = clip(triangle, cam.pos, cam_look)

        for clipped_triangle in clipped_triangle_list:
            line1 = clipped_triangle.v2 - clipped_triangle.v1
            line2 = clipped_triangle.v3 - clipped_triangle.v1
            surface_norm = crossProd(line1, line2)

            if dot(surface_norm, clipped_triangle.v1 - cam.pos) < 0:
                light_str:str = diffuseLight(light, surface_norm, clipped_triangle.v1)
                placeTriangle(clipped_triangle.translate(-1*cam.pos)
                              .rotationY(cam.yaw)
                              .rotationX(cam.pitch)
                              .projection(cam.flength)
                              .toScreen(), light_str)