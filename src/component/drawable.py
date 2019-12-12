#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import randint


class Drawable:
    """
    Every entity with this component can be draw on the map.
    """
    def __init__(self, dark_bg, dark_fg, light_bg, light_fg, char,
                 animated=False, animation_tick=None):
        self.dark_bg = dark_bg
        self.dark_fg = dark_fg
        self.light_bg = light_bg
        self.light_fg = light_fg
        self._char = char

        self.animated = animated
        self.animation_tick = animation_tick
        self.animation_clock = self.randomized_initial_clock(animation_tick)
        self.animation_index = 0

    @property
    def char(self):
        if self.animated:
            return self._char[self.animation_index]
        else:
            return self._char

    @char.setter
    def char(self, value):
        self._char = value

    @char.deleter
    def char(self):
        del self._char

    def tick(self):
        """
        This method is used to animate the character of the entity.
        Every animation_tick ticks the character is replaced with the
        next one in the animation.
        """
        if self.animated:
            self.animation_clock += 1

            if self.animation_clock == self.animation_tick:
                self.animation_index += 1
                self.animation_clock = 0

                if self.animation_index >= len(self._char):
                    self.animation_index = 0

    @staticmethod
    def randomized_initial_clock(animation_tick):
        if animation_tick:
            return randint(0, animation_tick - 1)
        else:
            return 0
