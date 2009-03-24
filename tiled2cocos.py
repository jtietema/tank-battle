#!/usr/bin/env python

# TODO: multiple layers
# TODO: properties on layers and the map itself
# TODO: includes inside maps file should be relative to the maps file, not relative
#       to the CWD.

import pyglet.image
import cocos.tiles
import xml.dom.minidom
import os


def get_text_contents(node, preserve_whitespace=False):
    """Returns the text contents for a particular node. By default discards
    leading and trailing whitespace."""
    result = ''.join([node.data for node in node.childNodes if node.nodeType == node.TEXT_NODE])
    
    if not preserve_whitespace:
        result = result.strip()
    
    return result


def get_first(parent, tag_name):
    """Returns the parent's first child tag matching the tag name."""
    return parent.getElementsByTagName(tag_name)[0]


def try_attribute(node, attribute_name, default=None):
    """Tries to get an attribute from the supplied node. Returns the default
    value if the attribute is unavailable."""
    if node.hasAttribute(attribute_name):
        return node.getAttribute(attribute_name)
    
    return default


def has_child(node, child_tag_name):
    """Determines if the node has at least one child with the specified tag name."""
    return len(node.getElementsByTagName(child_tag_name)) > 0


def load_tilesets(map_node):
    """Creates the cocos2d TileSet objects from .tmx tileset nodes."""
    tileset_nodes = map_node.getElementsByTagName('tileset')
    tiles = {}
    for tileset_node in tileset_nodes:
        tiles.update(load_tiles(tileset_node))
    return tiles


def load_tiles(tileset_node):
    """Loads the tiles from one tileset."""
    tiles = {}
    
    tile_width = int(tileset_node.getAttribute('tilewidth'))
    tile_height = int(tileset_node.getAttribute('tileheight'))
    spacing = int(try_attribute(tileset_node, 'spacing', 0))
    margin = int(try_attribute(tileset_node, 'margin', 0))
    
    image_map_file = get_first(tileset_node, 'image').getAttribute('source')
    image_map = pyglet.image.load(image_map_file)
    
    image_map_height = image_map.height
    image_map_width = image_map.width
    
    num_rows = (image_map_height - margin) // (tile_height + spacing)
    num_columns = (image_map_width - margin) // (tile_width + spacing)
    
    tile_properties = load_tile_properties(tileset_node)
    
    gid = int(tileset_node.getAttribute('firstgid'))
    for row_index in range(num_rows + 1):
        for col_index in range(num_columns + 1):
            x = margin + col_index * (tile_width + spacing)
            y = image_map_height - (margin + row_index * (tile_height + spacing)) - tile_height
            tile_image = image_map.get_region(x, y, tile_width, tile_height)
            
            if gid in tile_properties:
                properties = tile_properties[gid]
            else:
                properties = {}
            
            tiles[gid] = cocos.tiles.Tile(gid, properties, tile_image)
            gid += 1
    
    return tiles


def load_tile_properties(tileset_node):
    """Fetches properties for tiles from a tileset. Returns a dictionary, where the keys are
    the tile IDs."""
    first_gid = int(tileset_node.getAttribute('firstgid'))
    tile_nodes = tileset_node.getElementsByTagName('tile')
    
    properties = {}
    
    for tile_node in tile_nodes:
        gid = int(tile_node.getAttribute('id')) + first_gid
        
        if has_child(tile_node, 'properties'):
            tile_properties = {}
            property_nodes = get_first(tile_node, 'properties').getElementsByTagName('property')
            
            for property_node in property_nodes:
                name = property_node.getAttribute('name')
                value = property_node.getAttribute('value')
                tile_properties[name] = value
                
            properties[gid] = tile_properties
    
    return properties
    

def load_map(filename):
    """Loads the actual map_node using the tilesets passed in."""
    doc = xml.dom.minidom.parse(filename)

    map_node = doc.documentElement

    NUM_COLUMNS = int(map_node.getAttribute('width'))
    NUM_ROWS = int(map_node.getAttribute('height'))

    TILE_WIDTH = int(map_node.getAttribute('tilewidth'))
    TILE_HEIGHT = int(map_node.getAttribute('tileheight'))
    
    tiles = load_tilesets(map_node)
    
    layer_node = get_first(map_node, 'layer')
    
    tile_nodes = get_first(layer_node, 'data').getElementsByTagName('tile')
    tile_index = 0
    gid_matrix = []
    for row_index in range(NUM_ROWS):
        row = []
        gid_matrix.append(row)
        for col_index in range(NUM_COLUMNS):
            tile_node = tile_nodes[tile_index]
            row.append(int(tile_node.getAttribute('gid')))
            tile_index += 1
    
    gid_matrix = prepare_matrix(gid_matrix)
    
    cells = []
    for i, column in enumerate(gid_matrix):
        col = []
        cells.append(col)
        for j, gid in enumerate(column):
            col.append(cocos.tiles.RectCell(i, j, TILE_WIDTH, TILE_HEIGHT, {}, tiles[gid]))
    
    return cocos.tiles.RectMapLayer('map', TILE_WIDTH, TILE_HEIGHT, cells)


def prepare_matrix(matrix):
    """Converts a row oriented tile matrix into one that cocos2d
    understands. Visualize a matrix being rotated 90 degrees counter-clockwise,
    and you understand exactly what this method does."""
    result = []
    for row in zip(*matrix):
        row = list(row)
        row.reverse()
        result.append(row)
    return result


__all__ = ['load_map']
