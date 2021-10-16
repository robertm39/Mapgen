# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 18:42:40 2021

@author: rober
"""

import random

import maps

def num_differences(tile_1, tile_2):
    """
    Return the number of differences between the two tiles.
    """
    num = 0
    
    for direction in maps.Direction:
        #None matches everything
        if tile_1.sections[direction] == None:
            continue
        if tile_2.sections[direction] == None:
            continue
        
        if tile_1.sections[direction] != tile_2.sections[direction]:
            num += 1
    
    return num

class StochSwapMapBuilder:
    def __init__(self, half_diag, tile_map, sampler, num_swaps):
        self.half_diag = half_diag
        self.tile_map = tile_map
        self.sampler = sampler
        self.num_swaps = num_swaps
        
        self.all_coords = set()
        self.tiles_from_coords = dict()
        
        # Initialize all_coords
        for x in range(self.half_diag * 2 + 1):
            half_y = self.half_diag - abs(x - self.half_diag)
            
            for y in range(-half_y, half_y + 1):
                coords = maps.CoordPair(x, y)
                
                self.all_coords.add(coords)
        
        # For random sampling
        self.all_coords_list = list(self.all_coords)
        
        # Sample the initial tiles
        for coords in self.all_coords:
            tile = self.sampler.random_tile()
            self.tiles_from_coords[coords] = tile
    
    def get_needed_tile(self, coords):
        # Figure out what tile we need
        terrains = list()
        for direction in maps.Direction:
            adj_coords = self.tile_map.in_direction(coords, direction)
            
            if not adj_coords in self.all_coords:
                terrain = None
            else:
                adj_tile = self.tiles_from_coords[adj_coords]
                terrain = adj_tile.sections[maps.OPPOSITES[direction]]
            
            terrains.append(terrain)
        
        needed_tile = maps.Tile(*terrains)
        
        return needed_tile
    
    def error_at(self, coords):
        tile = self.tiles_from_coords[coords]
        needed = self.get_needed_tile(coords)
        return num_differences(tile, needed)
    
    def swap(self, coords_1, coords_2):
        tile_1 = self.tiles_from_coords[coords_1]
        tile_2 = self.tiles_from_coords[coords_2]
        
        self.tiles_from_coords[coords_1] = tile_2
        self.tiles_from_coords[coords_2] = tile_1
    
    def do_random_swap(self):
        """
        Swap two randomly chosen coords if doing so improves the map.
        """
        coords_1 = random.choice(self.all_coords_list)
        coords_2 = random.choice(self.all_coords_list)
        
        tile_1 = self.tiles_from_coords[coords_1]
        tile_2 = self.tiles_from_coords[coords_2]
        
        needed_1 = self.get_needed_tile(coords_1)
        needed_2 = self.get_needed_tile(coords_2)
        
        current_cost = num_differences(tile_1, needed_1) +\
                       num_differences(tile_2, needed_2)
        
        swapped_cost = num_differences(tile_1, needed_2) +\
                       num_differences(tile_2, needed_1)
        
        if swapped_cost < current_cost:
            self.swap(coords_1, coords_2)
    
    def fill_in_needed(self):
        filled_in = 0
        for coords in self.all_coords:
            needed = self.get_needed_tile(coords)
            
            skip = False
            for direction in maps.Direction:
                if needed.sections[direction] == None:
                    skip = True
                    break
            if skip:
                continue
            
            if needed != self.tiles_from_coords[coords]:
                filled_in += 1
                self.tiles_from_coords[coords] = needed
        print('Filled in {} tiles'.format(filled_in))
    
    def make_map(self, num_swaps):
        for _ in range(num_swaps):
            self.do_random_swap()
        
        self.fill_in_needed()
        
        for coords, tile in self.tiles_from_coords.items():
            self.tile_map.add_tile(coords, tile)