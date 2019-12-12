#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcod as libtcod


class BasicMonster:
    def __init__(self):
        pass

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results
