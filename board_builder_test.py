# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 11:13:47 2021

@author: rober
"""

from IPython.display import display

import maps
import tile_sampler
import board_builder
import display_map

def adjacency_test():
    #Get a boundless map
    tile_map = maps.TileMap(maps.boundless_disp)
    
    #Set the terrain types: plains, forest, and water
    terrains = ('P', 'F', 'W')
    
    #Get all the tiles
    tiles = tile_sampler.get_all_tiles(terrains)
    
    #Get the adjacency info manager
    coords_from_adjacencies = board_builder.CoordsFromAdjacencies(tile_map)
    
    tile_1 = maps.Tile(*'FFFF')
    coords_1 = maps.CoordPair(0, 0)
    
    coords_from_adjacencies.add_tile(coords_1, tile_1)
    
    #Check that all the data members are right
    assert coords_from_adjacencies.taken_coords == {coords_1}
    
    #Check the info of the coords above
    target_desc_above_1 = maps.Tile(None, None, None, 'F')
    coords_above = maps.CoordPair(0, -1)
    desc_above = coords_from_adjacencies.adjacencies_from_coords[coords_above]
    assert desc_above == target_desc_above_1
    
    fit_coords = coords_from_adjacencies.coords_from_adjacencies[desc_above]
    assert fit_coords == {coords_above}
    
    #Now add another tile and see if updating existing descriptions works
    tile_2 = maps.Tile(*'PPPP')
    
    #Up and to the left of the first tile
    coords_2 = maps.CoordPair(-1, -1)
    
    coords_from_adjacencies.add_tile(coords_2, tile_2)
    
    #Check that data members are right
    assert coords_from_adjacencies.taken_coords == {coords_1, coords_2}
    
    #Check that the description of (0, -1) is right
    target_desc_above_2 = maps.Tile(None, None, 'P', 'F')
    desc_above = coords_from_adjacencies.adjacencies_from_coords[coords_above]
    assert desc_above == target_desc_above_2
    
    fit_coords = coords_from_adjacencies.coords_from_adjacencies[desc_above]
    assert fit_coords == {coords_above}
    
    prev_fit = coords_from_adjacencies\
               .coords_from_adjacencies.get(target_desc_above_1, set())
    
    assert prev_fit == set()

def builder_test():
    # Get a boundless map
    tile_map = maps.TileMap(maps.boundless_disp)
    
    # Set the terrain types: plains, forest, and water
    # terrains = ('P', 'F', 'W')
    terrains = ('P', 'F')
    
    # Get all the tiles
    tiles = tile_sampler.get_all_tiles(terrains)
    
    # Get a tile sampler
    sampler = tile_sampler.get_uniform_sampler(tiles)
    
    # Get a board builder
    builder = board_builder.MapBuilder(tile_map, sampler)
    
    num_tiles = 10000
    
    for _ in range(num_tiles):
        builder.add_tile()
    
    #Display the map
    colors_from_terrains = {'P': (239, 222, 103),
                            'F': (16, 155, 0),
                            'W': (0, 0, 191)}
    
    plain_map = display_map.Map(tile_map)
    
    square_size = 3
    map_image = plain_map.get_image(colors_from_terrains, square_size)
    
    display(map_image)

def weighted_builder():
    # Get a boundless map
    tile_map = maps.TileMap(maps.boundless_disp)
    
    # Set the terrain types: plains, forest, and water
    terrains = ('P', 'F', 'W')
    # terrains = ('P', 'F')
    
    # Get all the tiles
    tiles = tile_sampler.get_all_tiles(terrains)
    
    # Get the weights
    
    # Get the segment weights
    # make full tiles more common, everything else equal
    segment_weights = tile_sampler.SegmentWeights([1, 1, 1, 4])
    
    # Get the terrain weights
    terrain_weights = dict()
    
    # make plains more common
    plains_weights = tile_sampler.TerrainWeight('P', 1.2)
    terrain_weights['P'] = plains_weights
    
    # make forests less common
    forest_weights = tile_sampler.TerrainWeight('F', 1)
    terrain_weights['F'] = forest_weights
    
    # make water more common
    water_weights = tile_sampler.TerrainWeight('W', 1.5, [0.1, 0.1, 0.1, 2])
    terrain_weights['W'] = water_weights
    
    # Get the sampler
    sampler = tile_sampler.get_weighted_sampler(segment_weights,
                                                terrain_weights)
    
    # Get a board builder
    builder = board_builder.MapBuilder(tile_map, sampler)
    
    num_tiles = 1000000
    
    for _ in range(num_tiles):
        builder.add_tile()
    
    #Display the map
    colors_from_terrains = {'P': (239, 222, 103),
                            'F': (16, 155, 0),
                            'W': (0, 0, 191)}
    
    plain_map = display_map.Map(tile_map)
    
    square_size = 1
    map_image = plain_map.get_image(colors_from_terrains, square_size)
    
    display(map_image)
    map_image.save('gen_map3.png')
    
def main():
    # adjacency_test()
    # builder_test()
    weighted_builder()

if __name__ == '__main__':
    main()