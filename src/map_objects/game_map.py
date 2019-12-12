#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import map_objects.constants as constants
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from map_objects.circle import Circle
from rendering.render_functions import RenderOrder
from component.fighter import Fighter
from component.ai import BasicMonster
from component.item import Item
from component.drawable import Drawable
from item_functions import heal
from entity import Entity

from random import randint
from numpy.random import choice
from math import sqrt


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.monster_factories = self.initialize_monster_factories()
        self.item_factories = self.initialize_item_factories()
        self.tile_factories = self.initialize_tile_factories()

        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[build_tile(self.tile_factories['wall']) for y in range(self.height)] for x in range(self.width)]

        return tiles

    @staticmethod
    def initialize_tile_factories():
        wall_tiles_fact = WallFactory()
        slimy_wall_tiles_fact = SlimyWallFactory()
        ground_tiles_fact = GroundFactory()

        return {'wall': wall_tiles_fact, 'slimy': slimy_wall_tiles_fact, 'ground': ground_tiles_fact}

    @staticmethod
    def initialize_monster_factories():
        # TODO: refactor method so enemies can be added
        #       easily or read from file
        trooper_fact = TrooperFactory(10, 0, 3)
        trooper_weight = 0.9
        juggernaut_fact = JuggernautFactory(15, 1, 4)
        juggernaut_weight = 0.1

        return {trooper_fact: trooper_weight, juggernaut_fact: juggernaut_weight}

    @staticmethod
    def initialize_item_factories():
        # TODO: refactor method so items can be added
        #       easily or read from file
        healing_pills_fact = HealingPillsFactory(4)
        healing_pills_weight = 1

        return {healing_pills_fact: healing_pills_weight}

    def create_rect_room(self, rect):
        # go through the tiles in the rectangle and make them walkable
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                self.tiles[x][y] = build_tile(self.tile_factories['ground'])

    def create_circle_room(self, circle):
        left_limit = min(self.width, circle.center_x - circle.radius)
        right_limit = max(0, circle.center_x + circle.radius + 1)

        top_limit = min(self.height, circle.center_y - circle.radius)
        bottom_limit = max(0, circle.center_y + circle.radius + 1)

        for x in range(max(0, left_limit), min(self.width, right_limit)):
            for y in range(max(0, top_limit), min(self.height, bottom_limit)):
                if sqrt((x - circle.center_x) ** 2 + (y - circle.center_y) ** 2) < circle.radius:
                    self.tiles[x][y] = build_tile(self.tile_factories['ground'])

    def make_map(self, map_width, map_height, max_rooms, room_min_size,
                 room_max_size, player, entities,
                 max_monsters_per_room, max_items_per_room):
        """
        This method generates a new map.
        """
        # TODO: refactor to generate symmetric maps. Half work, better maps!

        rooms = []
        rooms_number = 0

        for r in range(max_rooms):
            shape_seed = randint(0, 99)
            if shape_seed in constants.RECT_ROOM_RANGE:
                # build rect room
                # size of the rectangle
                rect_width = randint(room_min_size, room_max_size)
                rect_height = randint(room_min_size, room_max_size)
                # position of the rectangle
                corner_x = randint(0, map_width - rect_width - 1)
                corner_y = randint(0, map_height - rect_height - 1)

                new_room = Rect(corner_x, corner_y, rect_width, rect_height)

                self.create_rect_room(new_room)

            elif shape_seed in constants.CIRCLE_ROOM_RANGE:
                # build circle room
                # size of the circle
                radius = randint(int(room_min_size / 2),
                                 int(room_max_size / 2))
                # position of the circle's center
                center_x = randint(0 + radius + 1, map_width - radius - 1)
                center_y = randint(0 + radius + 1, map_height - radius - 1)

                new_room = Circle(center_x, center_y, radius)

                self.create_circle_room(new_room)

            else:
                raise ValueError

            # TODO: Add room filler!

            is_connected = False

            for other_room in rooms:
                if new_room.intersect(other_room):
                    is_connected = True

            (new_room_x, new_room_y) = new_room.center()

            if rooms_number == 0:
                player.x = new_room_x
                player.y = new_room_y

            elif not is_connected:
                # TODO connect to the nearest room instead
                (prev_room_x, prev_room_y) = rooms[rooms_number - 1].center()

                if randint(0, 1) == 1:
                    self.create_h_tunnel(prev_room_x, new_room_x, prev_room_y)
                    self.create_v_tunnel(prev_room_y, new_room_y, new_room_x)
                else:
                    self.create_v_tunnel(prev_room_y, new_room_y, prev_room_x)
                    self.create_h_tunnel(prev_room_x, new_room_x, new_room_y)

            place_entities(new_room, entities, max_monsters_per_room, max_items_per_room, self.monster_factories,
                           self.item_factories)

            rooms.append(new_room)
            rooms_number += 1

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = build_tile(self.tile_factories['ground'])

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = build_tile(self.tile_factories['ground'])

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        else:
            return False


def place_entities(room, entities, max_monsters_per_room, max_items_per_room, monster_factories, item_factories):
    # TODO: * split this function
    #       * code duplication

    # get a random number of monsters
    number_of_monsters = randint(0, max_monsters_per_room)

    # get a random number of items
    number_of_items = randint(0, max_items_per_room)

    # spawn monsters
    for i in range(number_of_monsters):
        # choose a random location in the room
        x, y = room.get_random_location()

        # if the tile is free from entities...
        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            # ...create a new monster there
            monster_factory = choice(list(monster_factories.keys()), p=list(monster_factories.values()))
            monster = build_entity(monster_factory, x, y)

            # add the spawned monster to the entity list
            entities.append(monster)

    # spawn items
    for i in range(number_of_items):
        # choose a random location in the room
        x, y = room.get_random_location()

        # if the tile is free from entities...
        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            # ...add a healing pill there
            item_factory = choice(list(item_factories.keys()), p=list(item_factories.values()))
            item = build_entity(item_factory, x, y)

            entities.append(item)


def build_tile(tile_factory):
    return tile_factory.factory()


def build_entity(entity_factory, x, y):
    return entity_factory.factory(x, y)


# TODO: move factories somewhere else
class TrooperFactory:
    def __init__(self, hp, defense, power):
        self.name = 'Trooper'
        self.hp = hp
        self.defense = defense
        self.power = power

    def factory(self, x, y):
        fighter_comp = Fighter(self.hp, self.defense, self.power)
        ai_comp = BasicMonster()
        drawable_comp = Drawable('trooper_bg_dark',
                                 'trooper_fg_dark',
                                 'trooper_bg_light',
                                 'trooper_fg_light',
                                 ['T', 'r', 'o', 'o', 'p', 'e', 'r'],
                                 animated=True,
                                 animation_tick=5)

        return Entity(x, y, self.name, blocks=True,
                      render_order=RenderOrder.ACTOR, drawable=drawable_comp, ai=ai_comp, fighter=fighter_comp)


class JuggernautFactory:
    def __init__(self, hp, defense, power):
        self.name = 'Juggernaut'
        self.hp = hp
        self.defense = defense
        self.power = power

    def factory(self, x, y):
        fighter_comp = Fighter(self.hp, self.defense, self.power)
        ai_comp = BasicMonster()
        drawable_comp = Drawable('juggernaut_bg_dark',
                                 'juggernaut_fg_dark',
                                 'juggernaut_bg_light',
                                 'juggernaut_fg_light',
                                 ['J', 'u', 'g', 'g', 'e', 'r', 'n', 'a', 'u', 't'],
                                 animated=True,
                                 animation_tick=5)

        return Entity(x, y, self.name, blocks=True,
                      render_order=RenderOrder.ACTOR, drawable=drawable_comp, ai=ai_comp, fighter=fighter_comp)


class HealingPillsFactory:
    def __init__(self, healing_amount):
        self.name = 'Healing Pill'
        self.healing_amount = healing_amount

    def factory(self, x, y):
        item_comp = Item(use_function=heal, amount=self.healing_amount)
        drawable_comp = Drawable('heal_pills_bg_dark',
                                 'heal_pills_fg_dark',
                                 'heal_pills_bg_light',
                                 'heal_pills_fg_light',
                                 char='!')

        return Entity(x, y, self.name, blocks=False,
                      render_order=RenderOrder.ITEM, drawable=drawable_comp, item=item_comp)


class WallFactory:
    def __init__(self):
        pass

    @staticmethod
    def factory():
        drawable_comp = Drawable('wall_bg_dark', 'wall_fg_dark', 'wall_bg_light', 'wall_fg_light',
                                 char='#')

        return Tile(blocked=True, drawable=drawable_comp)


class SlimyWallFactory:
    def __init__(self):
        pass

    @staticmethod
    def factory():
        drawable_comp = Drawable('wall_bg_dark', 'wall_fg_dark', 'wall_bg_light', 'wall_fg_light',
                                 char=['#', '`'], animated=True, animation_tick=30)

        return Tile(blocked=True, drawable=drawable_comp)


class GroundFactory:
    def __init__(self):
        pass

    @staticmethod
    def factory():
        drawable_comp = Drawable('ground_bg_dark', 'ground_bg_dark', 'ground_bg_light', 'ground_fg_light',
                                 char='.')

        return Tile(blocked=False, drawable=drawable_comp)
