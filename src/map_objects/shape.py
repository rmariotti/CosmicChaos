#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def center(self):
        raise NotImplementedError()

    @abstractmethod
    def intersect(self, shape):
        raise NotImplementedError()

    @abstractmethod
    def has_tile(self, x, y):
        raise NotImplementedError()

    @abstractmethod
    def get_random_location(self):
        raise NotImplementedError()
