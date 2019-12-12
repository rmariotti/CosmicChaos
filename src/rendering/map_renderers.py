from abc import ABC, abstractmethod
import tcod as libtcod


class MapRenderer(ABC):
    """
    A MapRenderer object gives access to methods used by the render_functions to print the map
    on a libtcod console.
    Using MapRenderer allows the user to print the map in different ways without changing the code.
    """

    def __init__(self, con, colors):
        self.con = con
        self.colors = colors

    @abstractmethod
    def draw(self, x, y, drawable, light):
        raise NotImplementedError()

    @abstractmethod
    def draw_entity(self, entity, fov_map):
        raise NotImplementedError()

    @abstractmethod
    def clear_entity(self, entity):
        raise NotImplementedError()

    @abstractmethod
    def clear_all(self, entities):
        raise NotImplementedError()


class SingleCharacterMapRenderer(MapRenderer):
    def __init__(self, con, colors):
        MapRenderer.__init__(self, con, colors)

    def draw(self, x, y, drawable, light):
        if light:
            self._draw_fg(x, y, drawable.drawable.char, self.colors[drawable.drawable.light_fg])
            self._draw_bg(x, y, self.colors[drawable.drawable.light_bg])
        else:
            self._draw_fg(x, y, drawable.drawable.char, self.colors[drawable.drawable.dark_fg])
            self._draw_bg(x, y, self.colors[drawable.drawable.dark_bg])

    def _draw_fg(self, x, y, char, fg_color=libtcod.white):
        libtcod.console_set_default_foreground(self.con, fg_color)
        libtcod.console_put_char(self.con, x, y, char, libtcod.BKGND_NONE)

    def _draw_bg(self, x, y, bg_color):
        libtcod.console_set_char_background(self.con, x, y, bg_color, libtcod.BKGND_SET)

    def draw_entity(self, entity, fov_map):
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            self.draw(entity.x, entity.y, entity, light=True)

    def clear_entity(self, entity):
        space = ' '
        self._draw_fg(entity.x, entity.y, space)

    def clear_all(self, entities):
        for entity in entities:
            self.clear_entity(entity)


class DoubleCharacterMapRenderer(MapRenderer):
    def __init__(self, con, colors):
        MapRenderer.__init__(self, con, colors)

    def draw(self, x, y, drawable, light):
        if light:
            self._draw_double(x, y, drawable.drawable.char, self.colors[drawable.drawable.light_fg],
                              self.colors[drawable.drawable.light_bg])
        else:
            self._draw_double(x, y, drawable.drawable.char, self.colors[drawable.drawable.dark_fg],
                              self.colors[drawable.drawable.dark_bg])

    def _draw_double(self, x, y, char, fg_color, bg_color):
        """
        This method is used to print characters on the map using a 8x16
        font while emulating the behaviour of a 16x16 font.
        This function will work as expected only if a compatible font is set in libtcod and
        SDL2 is used as renderer for the console.

        :param x: x-coordinate of the character to print.
        :param y: y-coordinate of the character to print.
        :param char: character what will be printed using two 8x16 characters.
        :param fg_color: character color.
        :param bg_color: character background color.
        :return: None
        """
        x = x * 2

        char_offset = 256 + (ord(char) - ord(' ')) * 2

        half_char_1 = char_offset
        half_char_2 = char_offset + 1

        self._draw_double_fg(x, y, half_char_1, half_char_2, fg_color)
        self._draw_double_bg(x, y, bg_color)

    def _draw_double_fg(self, x, y, char_1, char_2, fg_color=libtcod.white):
        """
        Uses libtcod to draw two characters (char_1, char_2) in two adjacent squares.

        :param x: x-coordinate where the first character will be put, the second one will be put in x+1.
        :param y: y-coordinate where the characters will be put.
        :param char_1: character to print in the first square.
        :param char_2: character to print in the second square.
        :param fg_color: color of the characters.
        :return: None
        """
        libtcod.console_set_default_foreground(self.con, fg_color)
        libtcod.console_put_char(self.con, x, y, char_1, libtcod.BKGND_NONE)
        libtcod.console_put_char(self.con, x + 1, y, char_2, libtcod.BKGND_NONE)

    def _draw_double_bg(self, x, y, bg_color):
        """
        Uses libtcod to set the background of two adjacent squares.

        :param x: x-coordinate of the first square, the second one will have x+1 x-coordinate.
        :param y: y-coordinate of both squares.
        :param bg_color: bg color of the squares.
        :return: None
        """
        libtcod.console_set_char_background(self.con, x, y, bg_color, libtcod.BKGND_SET)
        libtcod.console_set_char_background(self.con, x + 1, y, bg_color, libtcod.BKGND_SET)

    def draw_entity(self, entity, fov_map):
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            self.draw(entity.x, entity.y, entity, light=True)

    def clear_entity(self, entity):
        space = ' '
        self._draw_double_fg(entity.x * 2, entity.y, space, space)

    def clear_all(self, entities):
        for entity in entities:
            self.clear_entity(entity)
