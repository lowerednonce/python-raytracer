#!/usr/bin/python3
"""
A simplistic raytracer in python, exports draw, intersection, and vector math functions
"""
import math
import random as r
from PIL import Image

WIDTH=500
HEIGHT=500
FOCAL_LENGHT = 50
SAMPLE_RATE = 25
MAX_STEPS = 3

# color is emission
objects = [
        {
            "shape" : "sphere",
            "pos" : [0,20,40],
            "extra" : 30,
            "color" : [255,0,0],
            "reflectivity" : [1,1,1],
            "roughness" : 0,
        },
        {
            "shape" : "sphere",
            "pos" : [-10,0,20],
            "extra" : 10,
            "color" : [0,100,0],
            "reflectivity" : [1,1,1],
            "roughness" : 2,
        },
        {
            "shape" : "sphere",
            "pos" : [40,-50,60],
            "extra" : 10,
            "color" : [200,200,200],
            "reflectivity" : [1,1,1],
            "roughness" : 0.4,
        },
        {
            "shape" : "sphere",
            "pos" : [0,150,0],
            "extra" : 130,
            "color" : [50,0,100],
            "reflectivity" : [1,1,1],
            "roughness" : 0.4,
        },
        {
            "shape" : "sphere",
            "pos" : [10,10,15],
            "extra" : 7.5,
            "color" : [0,50,50],
            "reflectivity" : [1,1,1],
            "roughness" : 0.1,
        },
        ]

def draw(origin: [int], ray_direction: [int], objs: [dict], steps : int):
    "Returns a pixel's color with a ray and objects passed in"
    intersect = intersection(origin, ray_direction, objs)
    if intersect["collided"] and steps > 0:
        reflect_origin = intersect["point"]
        reflect_direction = reflect(ray_direction, intersect["normal"])

        # might be worth looking into removing the intersected object from the list of objects
        return add(
                intersect["obj"]["color"],
                mult_2(
                    draw(reflect_origin, reflect_direction, objs, steps-1),
                    intersect["obj"]["reflectivity"]))
    return [0,0,0]

def reflect(ray_direction : [int], normal : [int]):
    "Mathematics for ray reflection"
    norm_len = dot(ray_direction, normal) * 2
    return sub(ray_direction, mult(normal, norm_len))

def normalize(vec : [int]):
    "Normalize a 3 element vector"
    lenght=modulus(vec)
    return [vec[0]/lenght, vec[1]/lenght, vec[2]/lenght]

def mult(vec: [int], a: int):
    "Scalar multiplication of a three element vector"
    return [vec[0]*a, vec[1]*a, vec[2]*a]

def mult_2(vec1: [int], vec2: [int]):
    "Multiply two vectors' elements by each dimension"
    return [vec1[0]*vec2[0], vec1[1]*vec2[1], vec1[2]*vec2[2]]

def sub(vec1: [int], vec2: [int]):
    "Subtract two 3 element vectors"
    return [vec1[0]-vec2[0], vec1[1]-vec2[1], vec1[2]-vec2[2]]

def add(vec1: [int], vec2: [int]):
    "Add two 3 element vectors"
    return [vec1[0]+vec2[0], vec1[1]+vec2[1], vec1[2]+vec2[2]]

def dot(vec1: [int], vec2: [int]):
    "Calculate the dot product of two 3 element vectors"
    return vec1[0]*vec2[0] + vec1[1]*vec2[1] + vec1[2]*vec2[2]

def modulus(vec : [int]):
    "Calculate the magnitude of a 3 element vector"
    return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2 )

def gen_rand():
    "Generate a 3 element vector with random values between -0.5 and 0.5"
    return [r.random()-0.5, r.random()-0.5, r.random()-0.5]

def to_tuple_int(vec: [int]):
    "Return a 3 element tuple from a 3 element vector with its values rounded to an integer"
    return (round(vec[0]), round(vec[1]), round(vec[2]))

def intersection(origin, ray_direction, scan_objects):
    "Return information about the closest intersection of a ray"
    min_dist = None
    closest_intersection = None
    closest_object = None
    collided = False

    for o in scan_objects:
        if o["shape"] == "sphere":
            o_intersection = sphere_intersection(origin, ray_direction, o)
            if min_dist is None:
                min_dist = o_intersection["dist"]
                closest_intersection = intersection
                closest_object = o
                min_dist = o_intersection["dist"]
            elif o_intersection["dist"] is not None:
                if o_intersection["dist"] < min_dist:
                    closest_intersection = intersection
                    closest_object = o
                    min_dist = o_intersection["dist"]
            # OR equal, set the variable to true the first time it collides
            collided |= o_intersection["collided"]

    return {
        "collided" : collided,
        "point" : closest_intersection["point"],
        "dist" : closest_intersection["dist"],
        "normal": closest_intersection["normal"],
        "obj" : closest_object
        }


def sphere_intersection(origin: [int], ray_direction: [int], sphere: dict):
    "Calculate sphere intersection for a ray and a sphere"
    ray_sphere = sub(sphere["pos"], origin)
    dist_sphere = modulus(ray_sphere)
    dist_hit = dot(ray_sphere, ray_direction)
    dist_sphere_hit = math.sqrt(abs(dist_sphere**2 - dist_hit**2))

    dist_intersection = dist_hit - math.sqrt(abs(sphere["extra"]**2 - dist_sphere_hit**2))
    point = add(origin, mult(ray_direction, dist_intersection))
    normal = normalize(sub(point, sphere["pos"]))
    normal = normalize(add(normal, mult(gen_rand(), sphere["roughness"])))

    if(dist_hit > 0 and dist_sphere_hit < sphere["extra"]):
        return {
            "collided" : True,
            "dist" : dist_intersection,
            "normal" : normal,
            "point" : point
        }
    return {
        "collided": False,
        "dist": None,
        "normal" : None,
        "point": None
    }

if __name__ == "__main__":
    img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
    pixmap = img.load()

    TOTAL_RAYS = WIDTH*HEIGHT*SAMPLE_RATE
    PROGRESS=0
    print(f"Total rays to be cast: {TOTAL_RAYS*MAX_STEPS}")
    for i in range(0, WIDTH):
        for j in range(0,HEIGHT):
            x = i-(WIDTH/2)
            y = j-(HEIGHT/2)
            direction = normalize([x,y,FOCAL_LENGHT])

            col = [0,0,0]
            for s in range(SAMPLE_RATE):
                col = add(col, draw([0,0,0], direction, objects, MAX_STEPS))
            col = mult(col, 1/SAMPLE_RATE)

            pixmap[i,j] = (round(col[0]), round(col[1]), round(col[2]))
            PROGRESS += SAMPLE_RATE
            if PROGRESS % 100000 == 0:
                print(f"[PROGRESS] {round(PROGRESS/TOTAL_RAYS*100, 2)}%")
    img.save("result.png")
    print("DONE")
