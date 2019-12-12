#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcod as libtcod


class Tile:
    """
    A tile on a map. It may or may not be blocked, and may or
    may not block sight.
    """
    def __init__(self, blocked, block_sight=None, drawable=None):
        self.blocked = blocked

        # By default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight

        if drawable:
            self.drawable = drawable

        self.explored = False
