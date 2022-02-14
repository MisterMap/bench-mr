import json
import os
from bitarray import bitarray
import numpy as np
import math as math
from matplotlib.patches import Polygon, Circle

def checker(map_cell, centr, max_dist, x1, y1):
    valid = True
    points = []
    for i in range(map_cell.shape[1]):
        for j in range(map_cell.shape[0]):
            if (i-centr[1])**2 + (j-centr[0])**2 <= (max_dist+1)**2 and map_cell[i,j] == 0:
                valid = False
                points.append([i,j])
    return valid, points

def max_dist(start_point, points):
    angle = 0
    alpha = 1.
    c, s = np.cos(-angle), np.sin(-angle)
    rotation = np.array([[c, -s], [s, c]])
    poly = Polygon(start_point + np.matmul(points, rotation), True, fill=False, linestyle='--', edgecolor='b',alpha=alpha)
    coord = poly.get_xy()
    distance = []
    for i in coord: distance.append(math.dist(i, start_point))    
    return np.max(distance), poly

def nearest_point(suit_points, centr):
    distance = []
    for i in suit_points: distance.append(math.dist(i, centr))
    return suit_points[np.argmin(distance)]

def read_data(filename):
    file = open(filename, "r")
    data = json.load(file)
    file.close()
    shape = data['settings']['env']['collision']['robot_shape']
    run = data['runs'][0]
    points = np.array(shape)
    env = run['environment']
    w = env["width"]
    h = env["height"]
    map_data = np.array(list(bitarray(env["map"]))).reshape((h, w))
    map_data = 1. - map_data
    start_point = data['runs'][0]['environment']['start'][:2]
    end_point = data['runs'][0]['environment']['goal'][:2]
    return map_data, points, start_point, end_point

def find_start(map_data, start_point, points):
    a = map_data[0:25, 0:25]
    max_d, poly =max_dist(start_point, points)
    max_d = round(max_d)
    x1 = np.arange(max_d, round(a.shape[0]-max_d))
    y1 = np.arange(max_d, round(a.shape[1]-max_d))
    suit_points = []
    for i in x1:
        for j in y1:
            flag, b = checker(a, [i,j], max_d, x1, y1)
            if flag == True:
                suit_points.append([i,j])
    new_start = nearest_point(suit_points, start_point)
    return new_start

def find_end(map_data, end_point, points):
    h = map_data.shape[0]
    w = map_data.shape[1]
    end_point[0]-=h-25
    end_point[1]-=w-25
    a = map_data[-25:,-25:]
    max_d, poly =max_dist(end_point, points)
    max_d = round(max_d)
    x1 = np.arange(max_d, round(a.shape[0]-max_d))
    y1 = np.arange(max_d, round(a.shape[1]-max_d))
    suit_points = []
    for i in x1:
        for j in y1:
            flag, b = checker(a, [i,j], max_d, x1, y1)
            if flag == True:
                suit_points.append([i,j])
    new_end = nearest_point(suit_points, end_point)
    new_end[0] += h-25
    new_end[1] += w-25
    return new_end

def list_to_str(arr):
    f1 = ""
    for i in arr:
        f1 += str(i)+ " " 
    return f1

def start_end_correction(filename):
    map_data , points, start_point, end_point = read_data(filename)
    start = find_start(map_data, start_point, points)
    end = find_end(map_data, end_point, points)

    start_str = list_to_str(start)
    end_str = list_to_str(end)

    os.environ["START"] = start_str
    os.environ["END"] = end_str