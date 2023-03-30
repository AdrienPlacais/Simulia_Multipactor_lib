#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 11:29:06 2023

@author: A. Plaçais
"""
import numpy as np


def printc(*args, color='cyan'):
    """Print colored messages."""
    dict_c = {
        'red': '\x1B[31m',
        'blue': '\x1b[34m',
        'green': '\x1b[32m',
        'magenta': '\x1b[35m',
        'cyan': '\x1b[36m',
        'normal': '\x1b[0m',
    }
    print(dict_c[color] + args[0] + dict_c['normal'], end=' ')
    for arg in args[1:]:
        print(arg, end=' ')
    print('')

