# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 10:38:22 2021

@author: rober
"""

import itertools
import random

import maps

class CoordsFromAdjacencies:
    """
    For a description of the terrains adjacent to a tile,
    return all coordinates matching that description.
    """
    
    def __init__(self, tile_map):
        self.tile_map = tile_map
        self.taken_coords = set()
        self.coords_from_adjacencies = dict()
        self.adjacencies_from_coords = dict()
    
    def add_coords_to_description(self, coords, desc):
        if not desc in self.coords_from_adjacencies:
            self.coords_from_adjacencies[desc] = {coords}
        else:
            self.coords_from_adjacencies[desc].add(coords)
    
    def set_description(self, coords, desc):
        """
        Set the adjacency description of the given coords.
        """
        
        #These coordinates are already described
        #so I need to 
        if coords in self.adjacencies_from_coords:
            prev_desc = self.adjacencies_from_coords[coords]
            self.coords_from_adjacencies[prev_desc].remove(coords)
        
        self.adjacencies_from_coords[coords] = desc
        self.add_coords_to_description(coords, desc)
    
    def add_tile(self, coords, tile):
        """
        Add a tile and update the adjacency descriptions.
        """
        if coords in self.taken_coords:
            raise ValueError('coords already filled: {}'.format(coords))
        
        #Remove these coords from the adjacency maps
        self.taken_coords.add(coords)
        if coords in self.adjacencies_from_coords:
            curr_desc = self.adjacencies_from_coords[coords]
            self.coords_from_adjacencies[curr_desc].remove(coords)
            del self.adjacencies_from_coords[coords]
        
        #Update adjacencies for adjacent coords
        for direction in maps.Direction:
            adj_coords = self.tile_map.in_direction(coords, direction)
            
            #These coords already have a tile, so they aren't available
            if adj_coords in self.taken_coords:
                continue
            
            #Get the previous description of these coords
            none_desc = maps.Tile(None, None, None, None)
            prev_desc = self.adjacencies_from_coords.get(adj_coords, none_desc)
            
            #Add the new information to the description
            desc = prev_desc.copy()
            terrain = tile.sections[direction]
            desc.sections[maps.OPPOSITES[direction]] = terrain
            
            self.set_description(adj_coords, desc)
    
    def get_coords(self, desc):
        return self.coords_from_adjacencies.get(desc, set())

# Initialize the list of all descriptions to get from a tile
# each description mentions a certain subset of the sections of a tile
# each description must mention at least one section, and may mention all
# descriptions stored in a map from number of sections to lists of descriptions

# get the initial descriptions
DESCRIPTIONS = list(itertools.product([True, False], repeat=4))

# get rid of the description with no segments
DESCRIPTIONS.pop()

# store the descriptions in a map
DESC_FROM_NUM = {1: list(), 2: list(), 3: list(), 4: list()}

for desc in DESCRIPTIONS:
    num = sum(desc)
    DESC_FROM_NUM[num].append(desc)

def desc_from_tile(tile, desc_sections):
    desc = tile.copy()
    
    if not desc_sections[0]:
        desc.sections[maps.Direction.RIGHT] = None
        
    if not desc_sections[1]:
        desc.sections[maps.Direction.UP] = None
        
    if not desc_sections[2]:
        desc.sections[maps.Direction.LEFT] = None
        
    if not desc_sections[3]:
        desc.sections[maps.Direction.DOWN] = None
    
    return desc

class MapBuilder:
    def __init__(self, tile_map, tile_sampler):
        self.tile_map = tile_map
        self.tile_sampler = tile_sampler
        self.coords_from_adjacencies = CoordsFromAdjacencies(self.tile_map)
        
        self.empty = True
        
    def add_tile(self):
        """
        Add a randomly selected tile in a suitable location.
        Favors locations that have more tiles adjacent.
        """
        # get a tile
        tile = self.tile_sampler.random_tile()
        
        #If the map is empty, put a tile in the center
        if self.empty:
            self.empty = False
            
            coords = maps.CoordPair(0, 0)
            
            self.tile_map.add_tile(coords, tile)
            self.coords_from_adjacencies.add_tile(coords, tile)
            
            return coords
        #otherwise, put it adjacent to another tile
        
        # look for places to put the tile, starting with places
        # that have more tiles adjacent
        for adj_num in (4, 3, 2, 1):
            possible_coords = set()
            for adj_desc_template in DESC_FROM_NUM[adj_num]:
                adj_desc = desc_from_tile(tile, adj_desc_template)
                
                matching = self.coords_from_adjacencies.get_coords(adj_desc)
                
                for coords in matching:
                    possible_coords.add(coords)
            
            #If there aren't any possibilities, continue
            if not possible_coords:
                continue
            
            possible_coords = list(possible_coords)
            coords = random.choice(possible_coords)
            
            self.tile_map.add_tile(coords, tile)
            self.coords_from_adjacencies.add_tile(coords, tile)
            
            return coords
        
        return False