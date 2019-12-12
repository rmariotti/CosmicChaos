#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcod as libtcod

from component.drawable import Drawable
from entity import Entity
from component.fighter import Fighter
from component.inventory import Inventory
from game_states import GameStates
from game_messages import MessageLog

from map_objects.game_map import GameMap
from rendering.render_functions import RenderOrder


def get_constants():
    # SETTING
    # TODO: * read settings from file
    #       * use percentages for most settings

    window_title = 'Cosmic Chaos'

    # screen size settings
    screen_width = 120
    screen_height = 35

    start_fullscreen = False

    # UI settings
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    # message bar settings
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    # map size settings
    map_width = 60
    map_height = 29

    # level generator options
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 3
    max_items_per_room = 10

    # fov settings (tcod)
    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 20

    player_char = '@'

    # color palette (map only)
    # TODO: * create a cool color palette!
    #       * order entries
    colors = {
        'wall_bg_dark': libtcod.Color(0, 0, 0),
        'wall_fg_dark': libtcod.Color(39, 131, 0),
        'wall_bg_light': libtcod.Color(0, 0, 0),
        'wall_fg_light': libtcod.Color(50, 167, 0),

        'ground_bg_dark': libtcod.Color(0, 0, 0),
        'ground_fg_dark': libtcod.Color(0, 0, 0),
        'ground_bg_light': libtcod.Color(0, 0, 0),
        'ground_fg_light': libtcod.Color(100, 100, 100),

        'panel_back': libtcod.Color(0, 0, 0),
        'hp_bar_back': libtcod.Color(0, 0, 0),
        'hp_bar_front': libtcod.Color(39, 131, 0),
        'hp_bar_foreground': libtcod.Color(0, 0, 0),

        'player_fg_light': libtcod.Color(0, 0, 0),
        'player_fg_dark': libtcod.Color(0, 0, 0),
        'player_bg_light': libtcod.Color(66, 221, 0),
        'player_bg_dark': libtcod.Color(0, 0, 0),

        'heal_pills_bg_dark': libtcod.Color(0, 0, 0),
        'heal_pills_fg_dark': libtcod.Color(0, 0, 0),
        'heal_pills_bg_light': libtcod.Color(0, 0, 0),
        'heal_pills_fg_light': libtcod.violet,

        'trooper_bg_dark': libtcod.Color(0, 0, 0),
        'trooper_fg_dark': libtcod.Color(0, 0, 0),
        'trooper_bg_light': libtcod.Color(0, 0, 0),
        'trooper_fg_light': libtcod.yellow,

        'juggernaut_bg_dark': libtcod.Color(0, 0, 0),
        'juggernaut_fg_dark': libtcod.Color(0, 0, 0),
        'juggernaut_bg_light': libtcod.Color(0, 0, 0),
        'juggernaut_fg_light': libtcod.red
    }

    constants = {
        # window constants
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'start_fullscreen': start_fullscreen,

        # UI constants
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,

        # level generator constants
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,

        # game constants
        'player_char': player_char,

        # colors
        'colors': colors
    }

    return constants


def get_game_variables(constants):
    # create player's character
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(capacity=25)
    drawable_component = Drawable('player_bg_dark', 'player_fg_dark',
                                  'player_bg_light', 'player_fg_light',
                                  constants['player_char'])

    player = Entity(0, 0, 'Player', blocks=True,
                    render_order=RenderOrder.ACTOR, drawable=drawable_component,
                    fighter=fighter_component, inventory=inventory_component)

    entities = [player]

    # create level map
    game_map = GameMap(constants['map_width'],
                       constants['map_height'])

    game_map.make_map(constants['map_width'],
                      constants['map_height'],
                      constants['max_rooms'],
                      constants['room_min_size'],
                      constants['room_max_size'],
                      player, entities,
                      constants['max_monsters_per_room'],
                      constants['max_items_per_room'])

    message_log = MessageLog(constants['message_x'],
                             constants['message_width'],
                             constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state
