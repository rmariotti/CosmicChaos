#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from map_objects.shape import Shape
from random import randint


class Rect(Shape):
    def __init__(self, corner_x, corner_y, width, height):
        self.x1 = corner_x
        self.y1 = corner_y
        self.x2 = corner_x + width
        self.y2 = corner_y + height

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y

    def intersect(self, shape):
        for x in range(self.x1, self.x2 + 1):
            for y in range(self.y1, self.y2 + 1):
                if shape.has_tile(x, y):
                    return True

        return False

    def has_tile(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def get_random_location(self):
        x = randint(self.x1 + 1, self.x2 - 1)
        y = randint(self.y1 + 1, self.y2 - 1)

        return x, y
