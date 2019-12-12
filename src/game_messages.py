#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tcod as libtcod

import textwrap


class Message:
    """
    This class is used to store a message (String) and it's color
    """
    def __init__(self, text, color=libtcod.white):
        self.text = text
        self.color = color

class MessageLog:
    """
    This class is used to store a list of Message objects and display them
    in a box of limited height/width
    """
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # if the buffer is full, remove the first 
            # line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # add the new line as Message object, with the text and the color
            self.messages.append(Message(line, message.color))
