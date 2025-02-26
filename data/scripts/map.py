import random
from data.scripts.tile import Tile
import pygame


class Map:
    def __init__(self, scale, game):
        self.game = game
        self.tiles = {}
        self.scale = scale
        self.tile_res = pygame.Vector2(32 * self.scale, 64 * self.scale)
        self.tile_textures = {
            "default": pygame.image.load("data/assets/tiles/default.png").convert_alpha(),
            "spikes": pygame.image.load("data/assets/tiles/spikes.png").convert_alpha(),
            "fase1": pygame.image.load("data/assets/tiles/fase1.png").convert_alpha(),
            "fase2": pygame.image.load("data/assets/tiles/fase2.png").convert_alpha(),
            "fase3": pygame.image.load("data/assets/tiles/fase3.png").convert_alpha(),
            "crush": pygame.image.load("data/assets/tiles/crush.png").convert_alpha(),
            "crush_top": pygame.image.load("data/assets/tiles/crush_top.png").convert_alpha()
        }
        self.resize_textures()
        self.fallen_platforms = 0
        self.width = 3
        self.max_width = 7
        self.height = 3
        self.max_height = 5

        self.min_x = -1
        self.max_x = 1
        self.min_y = -1
        self.max_y = 1

        window_size = pygame.display.get_window_size()
        map_size = self.get_map_size()
        self.offset = (
            (window_size[0] - map_size[0]) / 2 + 150,
            (window_size[1] - map_size[1]) / 2 + 150,
        )

    def resize_textures(self):
        for key, value in self.tile_textures.items():
            width, height = value.get_size()
            self.tile_textures[key] = pygame.transform.scale(
                value,
                (width * self.scale, height * self.scale)
            ).convert_alpha()

    def generate_tiles(self):
        self.tiles = {}
        for y in range(-1, self.width - 1):
            for x in range(-1, self.height - 1):
                new_tile = Tile((x, y), self.scale, self.tile_textures, self.game, -y)
                self.tiles[(x, y)] = new_tile

    def increase_width(self):
        if self.width < self.max_width:
            self.width += 2

            # Generate new row at left
            for y in range(self.min_y, self.max_y + 1):
                tile_pos = (self.min_x - 1, y)
                self.tiles[tile_pos] = Tile(tile_pos, self.scale, self.tile_textures, self.game, -self.min_y - 1)
            self.min_x -= 1

            # Generate new row at right
            for y in range(self.min_y, self.max_y + 1):
                tile_pos = (self.max_x + 1, y)
                self.tiles[tile_pos] = Tile(tile_pos, self.scale, self.tile_textures, self.game, -self.max_y + 1)
            self.max_x += 1

    def increase_height(self):
        if self.height < self.max_height:
            self.height += 2

            # Generate new row at top
            for x in range(self.min_x, self.max_x + 1):
                tile_pos = (x, self.min_y - 1)
                self.tiles[tile_pos] = Tile(tile_pos, self.scale, self.tile_textures, self.game, -self.min_y)
            self.min_y -= 1

            # Generate new row at bottom
            for x in range(self.min_x, self.max_x + 1):
                tile_pos = (x, self.max_y + 1)
                self.tiles[tile_pos] = Tile(tile_pos, self.scale, self.tile_textures, self.game, -self.max_y)
            self.max_y += 1

    
    def update(self):
        for pos, tile in self.tiles.items():
            if tile.is_rendered:
                tile.update()

    def render(self, display):
        for y in range(self.min_y, self.max_y + 1):
            for x in range(self.min_x, self.max_x + 1):
                pos = (x, y)
                tile = self.tiles.get(pos)
                if not tile:
                    continue

                if tile.is_rendered:
                    tile.render(display, self.scale, self.offset)
                if pos == (int(self.game.player.pos.x), int(self.game.player.pos.y)):
                    if self.game.gameplay_active:
                        self.game.player.render(display, self.tile_res, self.offset)
                if tile.is_rendered:
                    tile.rendercrush(display, self.scale, self.offset)

    def start_death_transition(self):
        for pos, tile in self.tiles.items():
            tile.death_transition_fall = True

    def stop_tile_render(self):
        for pos, tile in self.tiles.items():
            tile.is_rendered = False

    def change_vertical_offset(self, pos: tuple[int, int], value: int):
        tile = self.tiles.get(pos)
        if not tile:
            return
        tile.change_vertical_offset(value)
        
    def get_random_tile(self):
        return random.choice(list(self.tiles.values()))

    def activate_random_trap(self):
        found_tile = None
        for i in range(0, 36):
            tile = self.get_random_tile()
            if not tile.counting and tile.exists:
                found_tile = tile
        if found_tile:
            found_tile.start_trap_counter()
    
    def get_tile(self, pos):
        return self.tiles.get(pos)

    def get_map_size(self) -> tuple[int, int]:
        return (
            self.width * 32 * self.scale + self.width * (1 * self.scale),
            self.height * 32 * self.scale + self.height * (1 * self.scale)
        )