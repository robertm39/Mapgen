# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 13:16:51 2021

@author: rober
"""

import traceback

import maps

def tile_test():
    tile1 = maps.Tile(1, 2, 3, 4)
    
    #Test rotation
    assert tile1.rotated(0) == tile1
    assert tile1.rotated(1) == maps.Tile(4, 1, 2, 3)
    assert tile1.rotated(2) == maps.Tile(3, 4, 1, 2)
    assert tile1.rotated(3) == maps.Tile(2, 3, 4, 1)
    
    #Test matching
    tile2 = maps.Tile(5, 5, 1, 5)
    assert tile1.matches(tile2, maps.Direction.RIGHT)
    assert not tile1.matches(tile2, maps.Direction.LEFT)
    assert not tile1.matches(tile2, maps.Direction.UP)
    assert not tile1.matches(tile2, maps.Direction.DOWN)
    
    tile3 = maps.Tile(5, 5, 5, 2)
    assert not tile1.matches(tile3, maps.Direction.RIGHT)
    assert not tile1.matches(tile3, maps.Direction.LEFT)
    assert tile1.matches(tile3, maps.Direction.UP)
    assert not tile1.matches(tile3, maps.Direction.DOWN)

def run_test(test):
    try:
        test()
    except Exception:
        print('{} Failed'.format(test.__name__))
        traceback.print_exc()
        return
    print('{} Succeeded'.format(test.__name__))

def main():
    run_test(tile_test)

if __name__ == '__main__':
    main()