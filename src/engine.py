#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcod as libtcod

from time import sleep

from game_states import GameStates
from loader_functions.initialize_new_game import (get_constants,
                                                  get_game_variables)
from input_handlers import handle_keys
from entity import get_blocking_entities_at_location, get_item_at_location
from rendering.render_functions import render_all
from rendering.map_renderers import DoubleCharacterMapRenderer
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from death_functions import kill_monster, kill_player


def main():
    constants = get_constants()

    # load font from file (tcod)
    libtcod.console_set_custom_font('../assets/terminus8x16_ext.png', libtcod.FONT_LAYOUT_TCOD, 32, 14)

    extended_characters_start = 256

    for y in range(5, 11):
        libtcod.console_map_ascii_codes_to_font(extended_characters_start, 32, 0, y)
        extended_characters_start += 32

    # create game map and game UI
    libtcod.console_init_root(constants['screen_width'],
                              constants['screen_height'],
                              constants['window_title'],
                              constants['start_fullscreen'],
                              libtcod.RENDERER_SDL2,
                              vsync=False)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])

    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])

    map_renderer = DoubleCharacterMapRenderer(con, constants['colors'])

    player, entities, game_map, message_log, game_state = get_game_variables(constants)

    # used to force tcod to recompute fov only when needed
    fov_recompute = True

    # contains a map of the tiles in player's fov
    fov_map = initialize_fov(game_map)

    # initialize mouse/keyboard input
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # set initial game state
    previous_game_state = game_state

    # game loop
    while not libtcod.console_is_window_closed():
        # reduce CPU usage
        # TODO: Use Events
        sleep(0.05)

        # check for inputs
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        # recompute fov if needed
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          constants['fov_radius'],
                          constants['fov_light_walls'],
                          constants['fov_algorithm'])

        # render map
        render_all(con, map_renderer, panel, entities,
                   player, game_map, fov_map,
                   fov_recompute, message_log,
                   constants['screen_width'],
                   constants['screen_height'],
                   constants['bar_width'],
                   constants['panel_height'],
                   constants['panel_y'],
                   mouse,
                   constants['colors'],
                   game_state)

        fov_recompute = False

        # draw map
        libtcod.console_flush()

        # remove entities from the map, they will be put back on the map
        # by render_all() on their new positions
        map_renderer.clear_all(entities)

        # parse user's input
        action = handle_keys(key, game_state)

        # the action variable contains a dictionary containing a command (key)
        # and some params (value), the lines below unpack the commands
        # TODO: use constants instead of strings for commands
        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        # list of dictionary containing the results of player's actions
        player_turn_results = []

        # parse move action
        if move and game_state == GameStates.PLAYERS_TURN:
            delta_x, delta_y = move
            destination_x = player.x + delta_x
            destination_y = player.y + delta_y

            # check if the destination tile is blocked (wall or other entities)
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(delta_x, delta_y)
                    fov_recompute = True

                # the player acted, now it's enemies turn
                game_state = GameStates.ENEMY_TURN

                # end of player's turn events
                for entity in entities:
                    entity.drawable.tick()

                for tile_row in game_map.tiles:
                    for tile in tile_row:
                        tile.drawable.tick()

        # parse item pickup
        if pickup and game_state == GameStates.PLAYERS_TURN:
            item = get_item_at_location(entities, player.x, player.y)

            if item:
                pickup_results = player.inventory.add_item(item)
                player_turn_results.extend(pickup_results)
            else:
                message_log.add_message(Message('There is nothing to pickup here.', libtcod.yellow))

        # open the inventory menu
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if (inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and
                inventory_index < len(player.inventory.items)):
            item = player.inventory.items[inventory_index]
            player_turn_results.extend(player.inventory.use(item))

        # Close program
        if exit:
            if game_state == GameStates.SHOW_INVENTORY:
                game_state = previous_game_state
            else:
                return True

        # Toggle/Set fullscreen
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_results in enemy_turn_results:
                        message = enemy_turn_results.get('message')
                        dead_entity = enemy_turn_results.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
