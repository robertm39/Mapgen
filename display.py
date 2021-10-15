# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 14:33:33 2021

@author: rober
"""

import maps

EMBEDDED_DISPS = {maps.Direction.RIGHT: (0, 0),
                  maps.Direction.UP: (-1, 0),
                  maps.Direction.LEFT: (-1, 1),
                  maps.Direction.DOWN: (0, 1)}

def get_embedded_coords(coords, direction):
    """
    Get the coordinates in the embedded grid
    for the given coordinates in the outer grid and the given direction.
    """
    x, y = coords.x, coords.y
    
    bx, by = x + y, -x + y
    
    dx, dy = EMBEDDED_DISPS[direction]
    
    return maps.CoordPair(bx + dx, by + dy)

class Map:
    """
    A map where each coordinate has a single terrain type.
    """
    def __init__(self, tile_map):
        squares = dict()
        
        #Get the embedded map out of the given tile map
        
        #For each tile, set the four embedded squares that are
        #partially in the tile
        #this also checks that all the tiles match
        for coords, tile in tile_map.tiles.items():
            for direction in maps.Direction:
                embedded_coords = get_embedded_coords(coords, direction)
                terrain = tile.sections[direction]
                
                if not embedded_coords in squares:
                    squares[embedded_coords] = terrain
                else:
                    if squares[embedded_coords] != terrain:
                        raise ValueError('mismatched terrains at {}: '
                                         '{}, {}'
                                         .format(embedded_coords,
                                                 squares[embedded_coords],
                                                 terrain))
        
        