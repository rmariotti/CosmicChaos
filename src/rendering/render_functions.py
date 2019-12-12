#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcod as libtcod
from math import floor

from enum import Enum
from game_states import GameStates
from menu import inventory_menu


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map):
    # floor(x/2) is needed since the map is made of 2 8x16 characters per tiles
    (x, y) = (floor(mouse.cx / 2), mouse.cy)

    names = [entity.name for entity in entities if entity.x == x and entity.y == y and
             libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]

    names = ', '.join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value,
               maximum, bar_color, back_color, foreground_color):
    """
    This function is used to render bars, for example the HP bar of the player.
    """
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1,
                         False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1,
                             False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, foreground_color)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y,
                             libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, map_renderer, panel, entities, player, game_map, fov_map,
               fov_recompute, message_log, screen_width, screen_height, bar_width,
               panel_height, panel_y, mouse, colors, game_state):
    """
    This function renders tiles, entities and panels.
    The tiles are rendered first then all the entities by render_order.

    TODO: code cleanup needed!
          move part of this stuff inside map_renderers
    """
    if fov_recompute:
        # Draw all the tiles in the game map
        for y in range(game_map.height):
            for x in range(game_map.width):
                tile = game_map.tiles[x][y]

                visible = libtcod.map_is_in_fov(fov_map, x, y)
                explored = tile.explored

                if visible:
                    # print tile
                    map_renderer.draw(x, y, tile, light=True)

                    game_map.tiles[x][y].explored = True

                elif explored:
                    map_renderer.draw(x, y, tile, light=False)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        map_renderer.draw_entity(entity, fov_map)

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    if game_state == GameStates.SHOW_INVENTORY:
        inventory_menu(con, 'Press the key next to an item to use it, '
                            'or Esc to cancel.\n',
                       player.inventory, 50, screen_width, screen_height)

    # clear panel
    libtcod.console_set_default_background(panel, colors['panel_back'])
    libtcod.console_clear(panel)

    # print the game_messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    # print the hp bar
    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp,
               player.fighter.max_hp,
               colors['hp_bar_front'],
               colors['hp_bar_back'],
               colors['hp_bar_foreground'])

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
                             get_names_under_mouse(mouse, entities, fov_map))

    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)