# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 12:59:50 2021

@author: Robert Morton
"""

from enum import Enum

class CoordPair:
    """
    A single coordinate pair.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self._hash = x<<16 ^ y
    
    def __eq__(self, other):
        if not isinstance(other, CoordPair):
            return False
        
        return self.x == other.x and self.y == other.y
    
    def __neq__(self, other):
        return not(self == other)
    
    def __hash__(self):
        return self._hash
    
    def __str__(self):
        return '{}, {}'.format(self.x, self.y)
    
    __repr__ = __str__

class Direction(Enum):
    RIGHT='RIGHT',
    UP='UP',
    LEFT='LEFT',
    DOWN='DOWN'

OPPOSITES = {Direction.RIGHT: Direction.LEFT,
             Direction.LEFT: Direction.RIGHT,
             Direction.UP: Direction.DOWN,
             Direction.DOWN: Direction.UP}

class Tile:
    """
    A tile.
    """
    def __init__(self, right, up, left, down):
        self.sections = {Direction.RIGHT: right,
                         Direction.UP: up,
                         Direction.LEFT: left,
                         Direction.DOWN: down}
        
        self._hash = 17
        self._hash = (self._hash + hash(right)) * 31
        self._hash = (self._hash + hash(up)) * 31
        self._hash = (self._hash + hash(left)) * 31
        self._hash = (self._hash + hash(down)) * 31
    
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        
        return self.sections == other.sections
    
    def __neq__(self, other):
        return not(self == other)
    
    def __hash__(self):
        return self._hash
    
    def __str__(self):
        return 'R: {}, T: {}, L: {}, B: {}'\
               .format(self.sections[Direction.RIGHT],
                       self.sections[Direction.UP],
                       self.sections[Direction.LEFT],
                       self.sections[Direction.DOWN])
    
    __repr__ = __str__
    
    def rotated(self, rotation):
        """
        Return this tile, rotated 90 degrees counterclockwise rotation times.
        """
        rotation = rotation % 4
        sections = [self.sections[Direction.RIGHT],
                    self.sections[Direction.UP],
                    self.sections[Direction.LEFT],
                    self.sections[Direction.DOWN]]
        
        sections = sections[-rotation:] + sections[:-rotation]
        
        return Tile(*sections)
    
    def matches(self, other, side):
        """
        Return whether the side of this tile indicate by side matches
        the opposite side of the other tile.
        """
        return self.sections[side] == other.sections[OPPOSITES[side]]

class TileMap:
    def __init__(self, disp_function):
        
        self.tiles = dict()
        
        self.disp_function = disp_function