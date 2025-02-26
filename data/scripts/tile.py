
import pygame
import random

class Tile:
    # Define the percentages for each number
    percentages = {
        1: 0.7,   # 60%
        2: 0.1,   # 30%
        3: 0.2   # 10%
    }

    def __init__(self, pos, scale, textures, game, row=0):
        self.pos: tuple[int, int] = pos
        self.scale = scale
        self.game = game
        self.vertical_offset = 3600 + -pos[1] * 500 - random.randint(-100, 500)
        self.textures = textures
        self.texture = self.textures.get("default")
        self.texture_id = 0
        self.width = 32 * self.scale
        self.height = 64 * self.scale
        self.counting = False
        self.fase1_start = 60
        self.fase2_start = 60
        self.fase3_start = 60
        self.fase = 0
        self.counter = 0
        self.killable = False
        self.trap_activated = False
        self.falling = False
        self.exists = True
        self.is_rendered = True

        self.reset_counter = 120

        self.velocity = 0
        self.acceleration = 1

        self.render_crush = False
        self.crush_vertical_offset = -100
        self.crush_velocity = 0
        self.crush_shake = False

        self.transition_fall = True

        self.death_transition_fall = False

    def update(self):
        if self.death_transition_fall:
            if (self.vertical_offset + self.velocity) < -1200:
                if not self.falling:
                    self.vertical_offset = 0
                    self.velocity = 0
                    self.death_transition_fall = False
                    self.game.start_deathtransition()
            else:
                self.vertical_offset -= self.velocity
                self.velocity += self.acceleration / 2
            return

        if self.counting:
            self.counter -= 1
            if self.counter <= 0:
                self.fase += 1
                if self.fase == 0:
                    self.counter = 60
                elif self.fase == 1:
                    self.counter = self.fase1_start
                elif self.fase == 2:
                    self.counter = self.fase2_start
                elif self.fase == 3:
                    self.counter = self.fase3_start
                elif self.fase == 4:
                    self.counter = self.reset_counter

        self.handle_fase_change()

        if self.render_crush:
            if not self.game.death_screen_transition:
                if (self.crush_vertical_offset + self.crush_velocity) > -16 * self.scale:
                    self.crush_vertical_offset = -16 * self.scale
                    self.killable = True
                    self.exists = False
                    self.game.player.check_death()
                    if not self.crush_shake:
                        self.crush_shake = True
                        self.game.screen_shake = 10
                else:
                    self.crush_vertical_offset += self.crush_velocity
                    self.crush_velocity += self.acceleration / 2

        if self.transition_fall:
            if (self.vertical_offset - self.velocity) < 0:
                self.vertical_offset = 0
                self.velocity = 0
                self.transition_fall = False
                self.game.start_gameplay()
                #if not self.game.player_spawned:
                #    self.game.setup(generate_tiles=False)
                #    self.game.player.is_rendered = True
            else:
                self.vertical_offset -= self.velocity
                self.velocity += self.acceleration / 2

        if self.falling:
            self.vertical_offset -= self.velocity
            self.velocity += self.acceleration
            if self.vertical_offset > 1500:
                self.render = False



    def handle_fase_change(self):
        if self.fase == 0:
            self.texture = self.textures.get("default")
            self.texture_id = 0
        if self.fase == 1:
            self.texture = self.textures.get("fase1")
            self.texture_id = 1
        if self.fase == 2:
            self.texture = self.textures.get("fase2")
            self.texture_id = 2
        if self.fase == 3:
            self.texture = self.textures.get("fase3")
            self.texture_id = 3
            self.game.player.check_warning(self.pos)
        if self.fase == 4:
            if not self.trap_activated:
                self.activate_trap()
        if self.fase == 5:
            self.deactivate_trap()

    def render(self, display: pygame.Surface, scale: int, map_offset: tuple[int, int]):
        
        x = self.pos[0] * self.width + self.pos[0] * (1 * scale) + map_offset[0]
        y = self.pos[1] * (27 * scale) + self.pos[1] * (1 * scale) - self.vertical_offset + map_offset[1]
        
        display.blit(self.texture, (x, y))

    def rendercrush(self, display: pygame.Surface, scale, map_offset: tuple[int, int]):
        if self.render_crush and not self.death_transition_fall:
            x = self.pos[0] * self.width + self.pos[0] * (1 * scale) + map_offset[0]
            y = self.pos[1] * (27 * scale) + self.pos[1] * (1 * scale) - self.vertical_offset + map_offset[1]

            display.blit(self.textures.get("crush_top"), (x, y + self.crush_vertical_offset))

    def change_vertical_offset(self, value):
        self.vertical_offset += value

    def start_trap_counter(self):
        self.counting = True

    def deactivate_trap(self):
        if self.game.death_screen_transition:
            self.is_rendered = False
            return
        self.texture = self.textures.get("default")
        self.counting = False
        self.counter = 0
        self.fase = 0
        self.killable = False
        self.trap_activated = False
        self.vertical_offset = 0
        self.velocity = 0
        if self.falling:
            self.game.map.fallen_platforms -= 1
            self.falling = False
        if self.render_crush:
            self.render_crush = False
            self.crush_velocity = 0
            self.crush_shake = False
        self.is_rendered = True
        self.exists = True

    def get_random_trap(self):
        # Generate a random number between 0 and 1
        rand_num = random.random()
        
        # Determine which number to generate based on the random number
        cumulative_prob = 0
        for num, prob in Tile.percentages.items():
            cumulative_prob += prob
            if rand_num <= cumulative_prob:
                return num

    def activate_trap(self, trap: int=None):
        # 1 = Spikes, 2 = Fall, 3 = Crush

        self.trap_activated = True

        if not trap:
            trap = self.get_random_trap()

        if trap == 1:
            self.activate_spikes()
        elif trap == 2:
            if self.game.map.fallen_platforms <= 5:
                self.activate_fall()
            else:
                self.trap_activated = False
                self.killable = False
                return
                # self.activate_trap(1)
        elif trap == 3:
            self.activate_crush()
        else:
            print(f"[ERROR] Unknown trap! {trap}")
        
    def activate_spikes(self):
        self.reset_counter = 120
        self.counter = self.reset_counter
        self.texture = self.textures.get("spikes")
        self.texture_id = 1
        self.killable = True
        self.game.player.check_death()
    
    def activate_fall(self):
        self.reset_counter = 1000
        self.counter = self.reset_counter
        self.falling = True
        self.exists = False
        self.game.map.fallen_platforms += 1
        self.game.screen_shake = 2


    def activate_crush(self):
        self.reset_counter = 240
        self.counter = self.reset_counter
        self.crush_vertical_offset = -1000
        self.texture = self.textures.get("crush")
        self.render_crush = True
        self.game.player.check_warning(self.pos)