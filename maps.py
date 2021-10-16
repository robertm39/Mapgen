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
        return '({}, {})'.format(self.x, self.y)
    
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
        
        # self._hash = 17
        # self._hash = (self._hash + hash(right)) * 31
        # self._hash = (self._hash + hash(up)) * 31
        # self._hash = (self._hash + hash(left)) * 31
        # self._hash = (self._hash + hash(down)) * 31
    
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        
        for direction in Direction:
            if self.sections[direction] != other.sections[direction]:
                return False
        
        return True
    
    def __neq__(self, other):
        return not(self == other)
    
    def __hash__(self):
        _hash = 17
        _hash = (_hash + hash(self.sections[Direction.RIGHT])) * 31
        _hash = (_hash + hash(self.sections[Direction.UP])) * 31
        _hash = (_hash + hash(self.sections[Direction.LEFT])) * 31
        _hash = (_hash + hash(self.sections[Direction.DOWN])) * 31
        
        return _hash
    
    def __str__(self):
        return '{} {} {} {}'\
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
    
    def copy(self):
        return Tile(self.sections[Direction.RIGHT],
                    self.sections[Direction.UP],
                    self.sections[Direction.LEFT],
                    self.sections[Direction.DOWN])

ADJ_DISPS = {Direction.RIGHT: CoordPair( 1,  0),
             Direction.UP: CoordPair( 0, -1),
             Direction.LEFT: CoordPair(-1,  0),
             Direction.DOWN: CoordPair( 0,  1)}

#Displacement functions
def boundless_disp(coords, disp):
    """
    The displacement for a bound unbounded in both directions.
    """
    return CoordPair(coords.x + disp.x, coords.y + disp.y)

def torus_disp(coords, disp, width, height):
    """
    The displacement for a toroidal board.
    """
    unwrapped = boundless_disp(coords, disp)
    
    return CoordPair(unwrapped.x % width, unwrapped.y % height)

def get_torus_disp(width, height):
    #You can't have a width or a height of one
    #tiles being adjacent to themselves isn't supported
    if width <= 1:
        raise ValueError('width: {}'.format(width))
        
    if height <= 1:
        raise ValueError('width: {}'.format(height))
    
    return lambda coords, disp: torus_disp(coords, disp, width, height)

class TileMap:
    """
    A map of tiles.
    """
    def __init__(self, disp_function):
        
        self.tiles = dict()
        
        self.disp_function = disp_function
    
    def in_direction(self, coords, direction):
        c_disp = ADJ_DISPS[direction]
        return self.disp_function(coords, c_disp)
    
    def fits(self, coords, tile):
        #For all the adjacent tiles, check whether this tile matches
        for direction in ADJ_DISPS:
            
            #Get the coordinates in this direction
            other_coords = self.in_direction(coords, direction)
            
            #If there are no coords in that direction, continue
            if other_coords is None:
                continue
            
            if not other_coords in self.tiles:
                continue
            
            other_tile = self.tiles[other_coords]
            
            #It doesn't match
            if not tile.matches(other_tile, direction):
                return False
        
        return True
    
    def add_tile(self, coords, tile):
        if coords in self.tiles:
            raise ValueError('coords in self.tiles: {}'.format(coords))
        
        if not self.fits(coords, tile):
            raise ValueError('tile doesn\'t fit: {}, {}'.format(coords, tile))
        
        self.tiles[coords] = tile
    
    def at(self, coords):
        return self.tiles[coords]