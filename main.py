#!/usr/bin/python3
from PIL import Image
import math
import random as r
import time

width=500
height=500
focalLenght = 50
sample_rate = 25
max_steps = 3

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

def draw(origin: [int], direction: [int], objs: [dict], steps : int):
    intersect = intersection(origin, direction, objs)
    if intersect["collided"] and steps > 0:
        reflect_origin = intersect["point"]
        reflect_direction = reflect(direction, intersect["normal"]) 

        # TODO: should remove the intersected object from the list of objects passed in
        col = add(intersect["obj"]["color"], mult_2(draw(reflect_origin, reflect_direction, objs, steps-1), intersect["obj"]["reflectivity"]))
        return col
    else:
        return [0,0,0]

def reflect(direction : [int], normal : [int]):
    norm_len = dot(direction, normal) * 2
    return sub(direction, mult(normal, norm_len))

def normalize(vec : [int]):
    lenght=modulus(vec)
    return [vec[0]/lenght, vec[1]/lenght, vec[2]/lenght]

def mult(vec: [int], a: int):
    return [vec[0]*a, vec[1]*a, vec[2]*a]

def mult_2(vec1: [int], vec2: [int]):
    return [vec1[0]*vec2[0], vec1[1]*vec2[1], vec1[2]*vec2[2]]

def sub(vec1: [int], vec2: [int]):
    return [vec1[0]-vec2[0], vec1[1]-vec2[1], vec1[2]-vec2[2]]

def add(vec1: [int], vec2: [int]):
    return [vec1[0]+vec2[0], vec1[1]+vec2[1], vec1[2]+vec2[2]]

def dot(vec1: [int], vec2: [int]):
    return vec1[0]*vec2[0] + vec1[1]*vec2[1] + vec1[2]*vec2[2]

def modulus(vec : [int]):
    return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2 )

def gen_rand():
    return [r.random()-0.5, r.random()-0.5, r.random()-0.5]

def to_tuple(vec: [int]):
    return (vec[0], vec[1], vec[2])

def to_tuple_int(vec: [int]):
    return (round(vec[0]), round(vec[1]), round(vec[2]))

def intersection(origin, direction, objects):
    min_dist = None
    closest_intersection = None
    closest_object = None
    collided = False

    for o in objects:
        if o["shape"] == "sphere":
            intersection = sphereIntersection(origin, direction, o)
            if min_dist == None:
                min_dist = intersection["dist"]
                closest_intersection = intersection
                closest_object = o
                min_dist = intersection["dist"]
            elif intersection["dist"] != None:
                if intersection["dist"] < min_dist:
                    closest_intersection = intersection
                    closest_object = o
                    min_dist = intersection["dist"]
            collided |= intersection["collided"]

    return {
        "collided" : collided,
        "point" : closest_intersection["point"],
        "dist" : closest_intersection["dist"],
        "normal": closest_intersection["normal"],
        "obj" : closest_object
        }


def sphereIntersection(origin: [int], direction: [int], sphere: dict):
    ray_sphere = sub(sphere["pos"], origin)
    dist_sphere = modulus(ray_sphere)
    dist_hit = dot(ray_sphere, direction)
    dist_sphere_hit = math.sqrt(abs(dist_sphere**2 - dist_hit**2))

    dist_intersection = dist_hit - math.sqrt(abs(sphere["extra"]**2 - dist_sphere_hit**2))
    point = add(origin, mult(direction, dist_intersection))
    normal = normalize(sub(point, sphere["pos"]))
    normal = normalize(add(normal, mult(gen_rand(), sphere["roughness"])))

    if(dist_hit > 0 and dist_sphere_hit < sphere["extra"]):
        return {
            "collided" : True,
            "dist" : dist_intersection,
            "normal" : normal,
            "point" : point
        }
    else:
        return {
            "collided": False,
            "dist": None,
            "normal" : None,
            "point": None
        }
    

if __name__ == "__main__":
    img = Image.new(mode="RGB", size=(width, height))
    pixmap = img.load()

    total_rays = width*height*sample_rate
    progress=0
    print(f"Total rays to be cast: {total_rays*max_steps}")
    
    for i in range(0, width):
        for j in range(0,height):
            x = i-(width/2)
            y = j-(height/2)
            direction = normalize([x,y,focalLenght])

            col = [0,0,0]
            # col1 = draw([0,0,0], direction, objects, 3)
            # col = add(col, col1)
            # col2 = draw([0,0,0], direction, objects, 3)
            # col = add(col, col2)
            # col3 = draw([0,0,0], direction, objects, 3)
            # col = add(col, col3)
            # if col1 != [0,0,0] or col2 != [0,0,0] or col3 != [0,0,0]:
                # print("HIT")
            for s in range(sample_rate):
                col = add(col, draw([0,0,0], direction, objects, max_steps))
            col = mult(col, 1/sample_rate)

            pixmap[i,j] = (round(col[0]), round(col[1]), round(col[2]))
            progress += sample_rate
            if (progress % 100000 == 0):
                print(f"[PROGRESS] {round(progress/total_rays*100, 2)}%")
    
    img.save("result.png")
    print("DONE")
