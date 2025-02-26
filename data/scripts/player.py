import pygame


class Player:
    def __init__(self, pos, scale, game):
        self.pos: pygame.Vector2 = pos
        self.scale = scale
        self.texture = pygame.transform.scale(
            pygame.image.load("data/assets/player/idle.png"), (15 * scale, 15 * scale)
        ).convert_alpha()
        self.warning = pygame.transform.scale(
            pygame.image.load("data/assets/player/warning.png"), (9 * (scale / 1.1), 17 * (scale / 1.1))
        ).convert_alpha()
        self.game = game
        self.game.map.change_vertical_offset((self.pos.x, self.pos.y), -5)
        self.move_count = 0
        self.can_move = True
        self.fall_with_tile = False
        self.vertical_offset = 0
        self.render_warning = False
        self.god_mode = False


    def move(self, x, y):

        if self.game.gameplay_transition:
            return

        if not self.can_move:
            return

        tile = self.game.map.get_tile((self.pos.x + x, self.pos.y + y))
        if not tile:
            return
    
        if not tile.exists:
            return
        
        self.game.map.change_vertical_offset((self.pos.x, self.pos.y), 5)
        self.pos.x += x
        self.pos.y += y
        self.game.map.change_vertical_offset((self.pos.x, self.pos.y), -5)

        self.move_count += 1

        if tile.fase == 3 or tile.render_crush:
            self.check_warning(tile.pos)
        else:
            self.render_warning = False

        self.check_death()

    def check_warning(self, pos):
        if self.pos.x == pos[0] and self.pos.y == pos[1]:
            self.render_warning = True
        else:
            self.render_warning = False

    def update(self):
        tile = self.game.map.get_tile((self.pos.x, self.pos.y))
        if not tile:
            return

        self.vertical_offset = tile.vertical_offset
        if self.vertical_offset < -1000:
            self.game.switch_to_death_screen()

    def check_death(self):
        if self.god_mode:
            return
        tile = self.game.map.get_tile((int(self.pos.x), int(self.pos.y)))

        if tile.killable:
            self.game.switch_to_death_screen()

    def render(self, display: pygame.Surface, tile_size: tuple[int, int], map_offset: tuple[int, int]):

        grid_x = self.pos.x * tile_size[0] + (1 * self.scale) * self.pos.x
        grid_y = self.pos.y * (27 * self.scale) + (1 * self.scale) * self.pos.y

        x = (tile_size[0] - self.texture.get_width()) // 2 + grid_x + map_offset[0]
        y = (27 * self.scale - self.texture.get_height()) // 2 - 10 + grid_y - self.vertical_offset + map_offset[1]

        display.blit(self.texture, (x, y))

        if self.render_warning:
            display.blit(self.warning, (x + 11, y - 75))