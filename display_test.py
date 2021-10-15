# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 15:42:09 2021

@author: rober
"""

from IPython.display import display

import maps
import display_map

def test_display():
    
    #Only have plains and forests for now
    colors_from_terrains = {'P': (239, 222, 103),
                            'F': (16, 155, 0)}
    
    # terrains = set('PF')
    
    tile_1 = maps.Tile('F', 'P', 'P', 'F')
    tile_2 = tile_1.rotated(1)
    tile_3 = tile_1.rotated(2)
    tile_4 = tile_1.rotated(3)
    
    tile_map = maps.TileMap()
    tile_map.add_tile(maps.CoordPair(0, 0), tile_1)
    tile_map.add_tile(maps.CoordPair(0, 1), tile_2)
    tile_map.add_tile(maps.CoordPair(1, 1), tile_3)
    tile_map.add_tile(maps.CoordPair(1, 0), tile_4)
    
    plain_map = display_map.Map(tile_map)
    
    square_size = 10
    map_image = plain_map.get_image(colors_from_terrains, square_size)
    
    display(map_image)

def main():
    test_display()

if __name__ == '__main__':
    main()