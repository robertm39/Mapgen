# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 14:33:33 2021

@author: rober
"""

import numpy as np

from PIL import Image, ImageDraw

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

def get_white_image_array(width, height):
    array = np.ones((width, height, 3), dtype=np.uint8)
    return array * 255

class Map:
    """
    A map where each coordinate has a single terrain type.
    """
    def __init__(self, tile_map):
        self.squares = dict()
        
        self.min_x = float('inf')
        self.max_x = float('-inf')
        
        self.min_y = float('inf')
        self.max_y = float('-inf')
        
        #Get the embedded map out of the given tile map
        
        #For each tile, set the four embedded squares that are
        #partially in the tile
        #this also checks that all the tiles match
        for coords, tile in tile_map.tiles.items():
            for direction in maps.Direction:
                embedded_coords = get_embedded_coords(coords, direction)
                
                #Update mininum and maximum values
                ex, ey = embedded_coords.x, embedded_coords.y
                
                self.min_x = min(self.min_x, ex)
                self.max_x = max(self.max_x, ex)
                
                self.min_y = min(self.min_y, ey)
                self.max_y = max(self.max_y, ey)
                
                terrain = tile.sections[direction]
                
                if not embedded_coords in self.squares:
                    self.squares[embedded_coords] = terrain
                else:
                    if self.squares[embedded_coords] != terrain:
                        raise ValueError('mismatched terrains at {}: '
                                         '{}, {}'
                                         .format(embedded_coords,
                                                 self.squares[embedded_coords],
                                                 terrain))
    
        self.width = self.max_x - self.min_x + 1
        self.height = self.max_y - self.min_y + 1
                        
    def get_image(self, colors_from_terrains, square_size):
        im_width = self.width * square_size
        im_height = self.height * square_size
        
        # im_arr = get_white_image_array(im_width, im_height)
        image = Image.new('RGB', (im_width, im_height), 'white')
        draw = ImageDraw.Draw(image)
        
        for coords, terrain in self.squares.items():
            x = (coords.x - self.min_x) * square_size
            y = (coords.y - self.min_y) * square_size
            
            color = colors_from_terrains[terrain]
            
            draw.rectangle([x, y, x+square_size-1, y+square_size-1],
                           fill=color,
                           outline=None,
                           width=0)
        
        return image
