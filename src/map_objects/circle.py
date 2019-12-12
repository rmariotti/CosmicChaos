#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from map_objects.shape import Shape
from random import randint, random
from math import sqrt, sin, cos, pi


class Circle(Shape):
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def center(self):
        return self.center_x, self.center_y

    def intersect(self, shape):
        for x in range(self.center_x - self.radius,
                       self.center_x + self.radius + 1):
            for y in range(self.center_y - self.radius,
                           self.center_y + self.radius + 1):
                if self.has_tile(x, y) and shape.has_tile(x, y):
                    return True
        return False

    def has_tile(self, x, y):
        return (euclidean_distance(x, y, self.center_x, self.center_y) <
                self.radius)
        # return sqrt((x - self.center_x)**2 + (y - self.center_y)**2) <
        #               self.radius

    def get_random_location(self):
        distance = randint(0, self.radius - 1)
        angle = 2 * pi * random()

        x = int(distance * cos(angle))
        y = int(distance * sin(angle))

        return x, y


def euclidean_distance(x1, y1, x2, y2):
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)
