#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Item:
    def __init__(self, use_function=None, **kwargs):
        self.use_function = use_function
        self.function_kwargs = kwargs
