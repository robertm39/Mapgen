# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 13:34:52 2021

@author: rober
"""

from random import randint
import math
import itertools

from numpy import sign

import maps

class Segment:
    """
    A segment of terrain on a tile.
    """
    def __init__(self, terrain, size):
        self.terrain = terrain
        self.size = size

def get_segments(tile):
    """
    Return a list of the segments in a tile.
    """
    segments = list()
    
    prev = None
    for direction in maps.Direction:
        #The terrain at the current section of the tile
        terrain = tile.sections[direction]
        
        #If the terrains don't match, we're in a new segment
        if terrain != prev:
            segments.append(Segment(terrain, 1))
        #If they do match, we're in the same segment
        else:
            segments[-1].size += 1
        prev = terrain
    
    #If there's only one segment, we're done
    if len(segments) == 1:
        return segments
    
    #If there's more than one segment,
    #we need to check if the first and last segment are really the same
    if segments[0].terrain == segments[-1].terrain:
        #Add the size of the last segment to the first,
        #and get rid of the last
        segments[0].size += segments[-1].size
        segments.pop()
    
    return segments

class TerrainWeight:
    """
    The weights for one terrain type.
    """
    def __init__(self, terrain, weight, segment_weights=None):
        self.terrain = terrain
        self.weight = weight
        self.segment_weights = segment_weights
    
    def get_weight(self, tile):
        """
        Return the weight this terrainweight assigns to the given tile.
        """
        weight = 1
        
        #Handle the terrain weight
        for direction in maps.Direction:
            if tile.sections[direction] == self.terrain:
                weight *= self.weight
        
        #Handle the segment weights, if any
        if self.segment_weights is not None:
            for segment in get_segments(tile):
                if segment.terrain == self.terrain:
                    weight *= self.segment_weights[segment.size - 1]
        
        return weight

class SegmentWeights:
    """
    The weights for different types of segments.
    """
    def __init__(self, segment_weights):
        self.segment_weights = segment_weights
    
    def get_weight(self, tile):
        """
        Return the weight this segmentweights assigns to the given tile.
        """
        weight = 1
        
        for segment in get_segments(tile):
            weight *= self.segment_weights[segment.size - 1]
        
        return weight

def get_all_tiles(terrains):
    """
    Return all possible tiles with the given terrain types.
    """
    result = set()
    
    #For each 4-tuple of terrain types drawn from terrains,
    #make a tile with those terrain types in its four sections
    for comb in itertools.product(terrains, repeat=4):
        result.add(maps.Tile(*comb))
    
    return result

def get_weights(tiles, terrains, segment_weights, terrain_weights):
    """
    Return the weights for each tile.
    
    Parameters:
        tiles: 
            The tiles to get the weights for.
            
        segment_weights SegmentWeights: 
            The weights for each segment size.
            
        terrain_weights {terrain->TerrainWeight}: 
            The weights for each terrain type.
    
    Return:
        
    """
    weights = dict()
    
    for tile in tiles:
        #Start with the segment-based weight
        weight = segment_weights.get_weight(tile)
        
        #Multiply in the terrain-based weights
        for _, terrain_weight in terrain_weights.items():
            weight *= terrain_weight.get_weight(tile)
    
        #Store this as the weight for the tile
        weights[tile] = weight
    
    return weights

def wrap_dict(d):
    """
    Return a wrapper function for the given dictionary.
    """
    return lambda x: d.get(x, 0)

def get_target_total_counts(weights, target_low_count):
    """
    Return the recommended target total count,
    given a target approximate minimum count.
    """
    
    min_weight = min(weight for _, weight in weights.items())
    
    return math.ceil(target_low_count / min_weight)

def get_counts_from_weights(weights, target_total_count):
    """
    Return the discrete counts corresponding to the given weights.
    """
    if target_total_count < len(weights):
        raise ValueError('{} tiles, target_total_count: {}'
                         .format(len(weights), target_total_count))
    
    total_weights = sum([weight for _, weight in weights.items()])
    
    total_count = 0
    
    counts = dict()
    
    for tile, weight in weights.items():
        normalized = (weight / total_weights) * target_total_count
        
        #Round each weight to a whole number,
        #then make sure each weight is above zero
        count = round(normalized)
        count = max(1, count)
        total_count += count
        
        counts[tile] = count
    
    #Trim the excess
    excess = total_count - target_total_count
    
    #Sort the tiles by count in descending order
    most_common_first = sorted(list(counts),
                               key=lambda x: counts[x],
                               reverse=True)
    
    #How much to subtract from tiles to correct the deviation
    change = sign(excess)
    
    #Add or subtract one from the most common tiles
    #to fix the deviation from the target total count
    for i in range(abs(excess)):
        counts[most_common_first[i]] -= change
        if counts[most_common_first[i]] == 0:
            raise ValueError('count of zero: {}'.format(most_common_first[i]))
    
    return counts

class TileSampler:
    """
    A class to sample tiles randomly from a given distribution
    """
    def __init__(self, tiles, count_func):
        self.total_count = 0
        self.tiles_from_nums = dict()
        
        #Set which numbers go to which tiles
        for tile in tiles:
            count = count_func(tile)
            
            for num in range(self.total_count, self.total_count + count):
                self.tiles_from_nums[num] = tile
                
            self.total_count += count
    
    def random_tile(self):
        """
        Select a random tile.
        """
        return self.tiles_from_nums[randint(0, self.total_count-1)]

def get_uniform_sampler(tiles):
    count_func = lambda x: 1 if x in tiles else 0
    
    return TileSampler(tiles, count_func)

def get_weighted_sampler(segment_weights, terrain_weights):
    #Get the terrain types and all the tiles
    terrain_types = set(terrain_weights)
    tiles = get_all_tiles(terrain_types)
    
    #Get the tile weights
    weights = get_weights(tiles,
                          terrain_types,
                          segment_weights,
                          terrain_weights)
    
    total_count = get_target_total_counts(weights, 1000)
    counts = get_counts_from_weights(weights, total_count)
    
    # for tile, count in counts.items():
    #     print('{}: {} times'.format(tile, count))
    
    count_func = wrap_dict(counts)
    
    return TileSampler(tiles, count_func)