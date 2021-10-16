# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 16:01:50 2021

@author: rober
"""

import random

import maps

class SwapMapBuilder:
    """
    Makes a map by first filling it with tiles, then rearranging.
    """
    def __init__(self,
                 half_diag,
                 tile_map,
                 border_sampler,
                 interior_sampler):
        
        self.half_diag = half_diag
        self.tile_map = tile_map
        self.border_sampler = border_sampler
        self.interior_sampler = interior_sampler
    
        self.tiles_from_coords = dict()
        self.coords_from_tiles = dict()
        self.frozen_coords = set()
    
    def make_border(self):
        """
        Add tiles around the border.
        """
        
        # Get the border and inner coords
        self.border_coords = set()
        
        # from 0 to half_diag * 2
        for x in range(self.half_diag * 2 + 1):
            half_y = self.half_diag - abs(x - self.half_diag)
            
            self.border_coords.add(maps.CoordPair(x, -half_y))
            self.border_coords.add(maps.CoordPair(x, half_y))
        
        #This work is being done multiple times now
        self.inner_coords = set()
        for x in range(1, self.half_diag * 2):
            half_y = self.half_diag - abs(x - self.half_diag)
            
            for y in range(-half_y + 1, half_y):
                coords = maps.CoordPair(x, y)
                if coords in self.border_coords:
                    raise ValueError('coords: {}'.format(coords))
                
                self.inner_coords.add(coords)
        
        self.eligible_coords = self.inner_coords.copy()
        
        # Sample the border
        for coords in self.border_coords:
            tile = self.border_sampler.random_tile()
            self.tile_map.add_tile(coords, tile)
    
    def add_to_coords_from_tiles(self, coords, tile):
        if not tile in self.coords_from_tiles:
            self.coords_from_tiles[tile] = set()
        
        self.coords_from_tiles[tile].add(coords)
    
    def sample_inner_tiles(self):
        """
        Fill the interior with random tiles, without regard for edges matching.
        """
        
        self.eligible_coords = self.inner_coords.copy()
        self.tiles_from_coords.clear()
        self.coords_from_tiles.clear()
        self.frozen_coords.clear()
        
        # Sample the inner tiles
        for coords in self.inner_coords:
            tile = self.interior_sampler.random_tile()
            
            self.tiles_from_coords[coords] = tile
            self.add_to_coords_from_tiles(coords, tile)
        
        # Put the outer tiles in
        for coords in self.border_coords:
            self.tiles_from_coords[coords] = self.tile_map.at(coords)
    
    def swap(self, coords_1, coords_2):
        # Get the tiles
        tile_1 = self.tiles_from_coords[coords_1]
        tile_2 = self.tiles_from_coords[coords_2]
        
        # Swap in tiles_from_coords
        self.tiles_from_coords[coords_1] = tile_2
        self.tiles_from_coords[coords_2] = tile_1
        
        # Swap in coords_from_tiles
        self.coords_from_tiles[tile_1].remove(coords_1)
        self.coords_from_tiles[tile_1].add(coords_2)
        
        self.coords_from_tiles[tile_2].remove(coords_2)
        self.coords_from_tiles[tile_2].add(coords_1)
    
    def do_swapping_iteration(self):
        # Get the interior coords in a random order
        shuffled_coords = list(self.eligible_coords)
        random.shuffle(shuffled_coords)
        
        for coords in shuffled_coords:
            # Figure out what tile we need
            terrains = list()
            for direction in maps.Direction:
                adj_coords = self.tile_map.in_direction(coords, direction)
                adj_tile = self.tiles_from_coords[adj_coords]
                terrain = adj_tile.sections[maps.OPPOSITES[direction]]
                terrains.append(terrain)
            
            needed_tile = maps.Tile(*terrains)
            coords_at = self.coords_from_tiles(needed_tile)
            
            #If none of the tiles work, continue
            if not coords_at:
                continue
            
            #Randomly select a tile
            coords_at = list(coords_at)
            other_coords = random.choice(coords_at)
            
            self.swap(coords, other_coords)
            
            # Make this spot ineligible for moving
            self.frozen_coords.add(coords)
            self.coords_from_tiles[needed_tile].remove(coords)
            self.eligible_coords.remove(coords)
    
    def do_swapping_iterations(self):
        while self.eligible_coords:
            self.do_swapping_iteration()
    
    def make_map(self):
        #Get the initial board
        self.make_border()
        self.sample_inner_tiles()
        
        # Put tiles into possible positions until you can't
        self.do_swapping_iterations()
        print('1 Iteration')
        
        done = False
        i = 2
        while not done:
            #See if the map works as is
            done = True
            try:
                test_map = maps.TileMap(self.tile_map.disp_function)
                for coords, tile in self.tiles_from_coords:
                    test_map.add_tile(coords, tile)
            except ValueError:
                done = False
            
            if done:
                break
            
            self.do_swapping_iterations()
            print('{} Iterations'.format(i))
            i += 1
            