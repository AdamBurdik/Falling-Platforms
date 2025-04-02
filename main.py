import pygame
import sys
import random

from data.scripts.explanation import Explanation
from data.scripts.player import Player
from data.scripts.map import Map
from data.preferences import RESOLUTION, MAX_FPS, SCALE
import json

from data.scripts.tile import Tile


class Game:
    def __init__(self, resolution, max_fps, scale):

        pygame.init()
        info = pygame.display.Info()
        self.display = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)

        self.screen = pygame.Surface((info.current_w, info.current_h))
        self.max_fps = max_fps
        self.clock = pygame.Clock()
        self.scale = scale
        self.map = Map(self.scale, self)
        self.player = Player(pygame.Vector2(0, 0), self.scale, self)

        self.background_scale = 1

        self.background1_layer1 = pygame.transform.scale(
            pygame.image.load("data/assets/background1_layer1.png"),
            (1920 * self.background_scale, 1080 * self.background_scale)
        ).convert_alpha()
        self.background2_layer1 = pygame.transform.scale(
            pygame.image.load("data/assets/background2_layer1.png"),
            (1920 * self.background_scale, 1080 * self.background_scale)
        ).convert_alpha()

        self.background1_layer2 = pygame.transform.scale(
            pygame.image.load("data/assets/background1_layer2.png").convert_alpha(),
            (1920 * self.background_scale, 1080 * self.background_scale)
        ).convert_alpha()
        self.background2_layer2 = pygame.transform.scale(
            pygame.image.load("data/assets/background2_layer2.png").convert_alpha(),
            (1920 * self.background_scale, 1080 * self.background_scale)
        ).convert_alpha()

        self.background_width = 1920 * self.background_scale
        self.background_height = 1080 * self.background_scale

        self.background_speed = 2

        self.backgrounds = [
            [
                ([0, 0], self.background1_layer1),
                ([-self.background_width, 0], self.background2_layer1)
            ],
            [
                ([0, 0], self.background1_layer2),
                ([self.background_width, 0], self.background2_layer2)
            ],
        ]


        self.trap_spawn_length = 2500
        self.trap_count = 1
        self.trap_count_velocity = 1
        self.fase_trap_count = 0
        self.total_trap_count = 0
        self.trap_timer_event = pygame.USEREVENT + 1
        self.size_to_generate = 0

        self.time = 0
        self.time_timer_event = pygame.USEREVENT + 2
        self.mainscreen_ui_scale = 9

        pygame.font.init()
        self.font = pygame.font.Font("data/assets/fonts/ui_font.otf", 56)
        self.small_font = pygame.font.Font("data/assets/fonts/ui_font.otf", 16)
        self.ui_font = pygame.font.Font("data/assets/fonts/ui_font.otf", 10 * self.mainscreen_ui_scale)
        self.small_ui_font = pygame.font.Font("data/assets/fonts/ui_font.otf", 5 * self.mainscreen_ui_scale)

        self.title = pygame.transform.scale(
            pygame.image.load("data/assets/ui/title.png").convert_alpha(),
            (87 * self.mainscreen_ui_scale, 22 * self.mainscreen_ui_scale)
        )
        self.navbar = pygame.transform.scale(
            pygame.image.load("data/assets/ui/navbar_bars.png").convert_alpha(),
            (122 * (self.mainscreen_ui_scale / 1.5), 7 * (self.mainscreen_ui_scale / 1.5))
        )

        self.play_button = pygame.transform.scale(
            pygame.image.load("data/assets/ui/play_button.png").convert_alpha(),
            (21 * (self.mainscreen_ui_scale / 1.5), 9 * (self.mainscreen_ui_scale / 1.5))
        )
        self.play_button_rect = self.play_button.get_rect(topleft=(
            (self.resolution[0] - self.play_button.get_width()) // 2 - 145,
            (self.resolution[1] - self.play_button.get_height()) // 2
        ))

        self.exit_button = pygame.transform.scale(
            pygame.image.load("data/assets/ui/exit_button.png").convert_alpha(),
            (18 * (self.mainscreen_ui_scale / 1.5), 8 * (self.mainscreen_ui_scale / 1.5))
        )
        self.exit_button_rect = self.exit_button.get_rect(topleft=(
            (self.resolution[0] - self.exit_button.get_width()) // 2 + 160,
            (self.resolution[1] - self.exit_button.get_height()) // 2
        ))

        self.controls_button = pygame.transform.scale(
            pygame.image.load("data/assets/ui/controls_button.png").convert_alpha(),
            (43 * (self.mainscreen_ui_scale / 1.5), 8 * (self.mainscreen_ui_scale / 1.5))
        )

        self.record_button = pygame.transform.scale(
            pygame.image.load("data/assets/ui/record_button.png").convert_alpha(),
            (36 * (self.mainscreen_ui_scale / 1.5), 8 * (self.mainscreen_ui_scale / 1.5))
        )

        self.navbar2 = pygame.transform.scale(
            pygame.image.load("data/assets/ui/navbar_bars_2.png").convert_alpha(),
            (132 * (self.mainscreen_ui_scale / 1.5), 3 * (self.mainscreen_ui_scale / 1.5))
        )

        self.controls_button_rect = self.controls_button.get_rect(topleft=(
            (self.resolution[0] - self.controls_button.get_width()) // 2 - 175,
            (self.resolution[1] - self.controls_button.get_height()) // 2 + 150
        ))

        self.record_button_rect = self.record_button.get_rect(topleft=(
            (self.resolution[0] - self.record_button.get_width()) // 2 + 195,
            (self.resolution[1] - self.record_button.get_height()) // 2 + 150
        ))

        self.controls_screen = pygame.transform.scale(
            pygame.image.load("data/assets/ui/controls_screen.png").convert_alpha(),
            (192 * (self.mainscreen_ui_scale / 1.5), 116 * (self.mainscreen_ui_scale / 1.5))
        )


        # 0 = Disabled
        # 1 = To Right
        # -1 = To Left
        self.ui_transition = 0
        self.ui_transition_type = 1
        self.navbar_horizontal_offset = 0
        self.navbar_horizontal_velocity = -15
        self.title_horizontal_offset = 0
        self.title_horizontal_velocity = -15
        self.ui_acceleration = 2

        self.title_vertical_offset = 0
        self.title_offset_direction = 0

        # 0 = MainScreen
        # 1 = Game
        # 2 = DeathScreen
        self.menu = 0

        self.death_screen = pygame.transform.scale(
            pygame.image.load("data/assets/ui/death_screen.png").convert_alpha(),
            (126 * self.mainscreen_ui_scale, 67 * self.mainscreen_ui_scale)
        ).convert_alpha()
        self.death_screen_transition = False
        self.death_screen_vertical_offset = 0
        self.death_screen_velocity = 0

        self.record = 0

        self.music = False

        pygame.mixer.init()
        pygame.mixer.music.load("data/assets/music/background_music.mp3")

        self.playing_music = False

        self.active_buttons = True

        self.screen_shake = 0
        self.gameplay_transition = False
        self.gameplay_transition_text_horizontal_offset = -375

        self.gameplay_active = False

        self.survived_time = 0

        self.explanation = Explanation(self)

    @property
    def resolution(self) -> tuple[int, int]:
        return pygame.display.get_window_size()

    def toggle_music(self):
        if self.playing_music:
            self.stop_music()
            self.playing_music = False
        else:
            self.play_music()
            self.playing_music = True

    def play_music(self):
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)

    def stop_music(self):
        pygame.mixer.music.stop()

    def start_gameplay(self):
        if self.gameplay_active:
            return

        self.gameplay_transition = False

        pygame.time.set_timer(self.trap_timer_event, self.trap_spawn_length)
        pygame.time.set_timer(self.time_timer_event, 1000)
        self.gameplay_active = True

        self.player.can_move = True

        self.gameplay_transition = False

    def setup(self, generate_tiles=True):

        self.start_gameplay()
        #self.player.pos = pygame.Vector2(random.randint(0, 6), random.randint(0, 6))

        if generate_tiles:
            self.map.generate_tiles()

        self.trap_count_velocity = 1

        self.active_buttons = False

        self.ui_transition = 0
        self.navbar_horizontal_offset = 0
        self.navbar_horizontal_velocity = -15
        self.title_horizontal_offset = 0
        self.title_horizontal_velocity = -15

    def load_record(self):
        with open("data/record.json") as file:
            data = json.load(file)
            self.record = data.get("record")

    def render_background(self) -> None:
        for i, layer in enumerate(self.backgrounds):
            for background in layer:

                pos = background[0]
                surface = background[1]

                if i == 0:
                    pos[0] += self.background_speed
                    if pos[0] > self.background_width:
                        pos[0] = -self.background_width + self.background_speed
                else:
                    pos[0] -= self.background_speed
                    if pos[0] < -self.background_width:
                        pos[0] = self.background_width - 2

                self.screen.blit(surface, pos)

    def start_deathtransition(self):
        self.trap_count = 0
        self.map.stop_tile_render()
        self.death_screen_transition = True
        self.death_screen_vertical_offset = 750
        print("time:", self.time, "record:", self.record)
        if self.time > self.record:
            self.record = self.time
        self.save_record()
        self.menu = 2

    def switch_to_death_screen(self):

        self.gameplay_active = False

        self.survived_time = self.time
        self.map.start_death_transition()
        #self.menu = 2

    def tick(self):
        self.screen.fill((0, 0, 0))

        match self.menu:
            case 0:
                self.tick_mainscreen()
            case 1:
                self.tick_game()
            case 2:
                self.tick_deathscreen()
            case 3:
                self.tick_controls()
            case 4:
                self.tick_record()
            case 5:
                self.explanation.tick()


        screen_shake_offset = pygame.Vector2(0, 0)
        if self.screen_shake > 0:
            self.screen_shake -= 1

            screen_shake_offset.x = random.randint(-4, 4)
            screen_shake_offset.y = random.randint(-4, 4)

        self.display.blit(self.screen, screen_shake_offset)
        pygame.display.set_caption(f"Falling Platforms       FPS: {int(self.clock.get_fps())}")

    def transition_to_gameplay(self):
        self.map.generate_tiles()
        self.gameplay_transition = True
        self.menu = 1

    def tick_controls(self):
        self.render_background()

        self.screen.blit(self.controls_screen, (
            (self.resolution[0] - self.controls_screen.get_width()) // 2,
            (self.resolution[1] - self.controls_screen.get_height()) // 2
        ))

        click_to_continue = self.small_ui_font.render("click anywhere to continue", True, (249, 168, 117))
        self.screen.blit(click_to_continue, ((self.resolution[0] - 600) // 2, 1030))

    def tick_record(self):
        self.render_background()

        record_time = self.small_ui_font.render(f"Personal best: {self.record}", True, (255, 246, 211))
        self.screen.blit(record_time, (550, 455 - self.death_screen_vertical_offset))

        click_to_continue = self.small_ui_font.render("click anywhere to continue", True, (249, 168, 117))
        self.screen.blit(click_to_continue, ((self.resolution[0] - 600) // 2, self.resolution[1] - 50))

        # current_time = self.ui_font.render(f"{self.time}s", True, (255, 246, 211)) self.screen.blit( current_time,
        # ((self.resolution[0] - self.death_screen.get_width()) // 2, (self.resolution[1] -
        # self.death_screen.get_height()) // 2) )

    def tick_mainscreen(self):
        self.render_background()

        if self.title_offset_direction == 0:
            self.title_vertical_offset += 0.3
            if self.title_vertical_offset > 25:
                self.title_offset_direction = 1

        if self.title_offset_direction == 1:
            self.title_vertical_offset -= 0.3
            if self.title_vertical_offset < 0:
                self.title_offset_direction = 0

        if self.ui_transition:
            self.title_horizontal_offset += (self.title_horizontal_velocity + 0.1) * -self.ui_transition
            self.title_horizontal_velocity += self.ui_acceleration

            self.navbar_horizontal_offset += (self.navbar_horizontal_velocity + 1) * self.ui_transition
            self.navbar_horizontal_velocity += self.ui_acceleration

            if self.title_horizontal_offset < -1000:
                if self.ui_transition_type == 1:
                    self.transition_to_gameplay()
                elif self.ui_transition_type == 2:
                    self.menu = 3
            if self.title_horizontal_offset > 1000:
                if self.ui_transition_type == 1:
                    self.quit()
                elif self.ui_transition_type == 2:
                    self.load_record()
                    self.menu = 4

        self.screen.blit(self.title, (
            (self.resolution[0] - self.title.get_width()) // 2 + self.title_horizontal_offset,
            (self.resolution[1] - self.title.get_height()) // 2 - 200 + self.title_vertical_offset
        ))

        self.screen.blit(self.navbar, (
            (self.resolution[0] - self.navbar.get_width()) // 2 + self.navbar_horizontal_offset,
            (self.resolution[1] - self.navbar.get_height()) // 2,
        ))

        self.screen.blit(self.play_button, (
            (self.resolution[0] - self.play_button.get_width()) // 2 - 145 + self.navbar_horizontal_offset,
            (self.resolution[1] - self.play_button.get_height()) // 2
        ))

        self.screen.blit(self.exit_button, (
            (self.resolution[0] - self.play_button.get_width()) // 2 + 160 + self.navbar_horizontal_offset,
            (self.resolution[1] - self.play_button.get_height()) // 2
        ))

        self.screen.blit(self.navbar2, (
            (self.resolution[0] - self.navbar2.get_width()) // 2 + self.navbar_horizontal_offset,
            (self.resolution[1] - self.navbar2.get_height()) // 2 + 150
        ))

        self.screen.blit(self.controls_button, (
            (self.resolution[0] - self.controls_button.get_width()) // 2 + self.navbar_horizontal_offset - 175,
            (self.resolution[1] - self.controls_button.get_height()) // 2 + 150
        ))

        self.screen.blit(self.record_button, (
            (self.resolution[0] - self.record_button.get_width()) // 2 + self.navbar_horizontal_offset + 195,
            (self.resolution[1] - self.record_button.get_height()) // 2 + 150
        ))

    def tick_game(self):
        if not self.gameplay_transition:
            self.handle_key_input()

        self.render_background()

        self.map.update()
        self.player.update()
        self.map.render(self.screen)
        self.draw_text()

    def save_record(self):
        with open("data/record.json", "w") as file:
            json.dump({"record": self.record}, file, indent=4)

    def tick_deathscreen(self):
        self.render_background()

        if self.death_screen_transition:
            if self.death_screen_vertical_offset - self.death_screen_velocity < 0:
                self.death_screen_vertical_offset = 0
                self.death_screen_velocity = 0
                self.death_screen_transition = False
                self.screen_shake = 10
            else:
                self.death_screen_vertical_offset -= self.death_screen_velocity
                self.death_screen_velocity += 1

        self.screen.blit(
            self.death_screen,
            ((self.resolution[0] - self.death_screen.get_width()) // 2,
             (self.resolution[1] - self.death_screen.get_height()) // 2 - self.death_screen_vertical_offset)
        )

        survived_time = self.small_ui_font.render(f"Survived for {self.survived_time} seconds", True, (255, 246, 211))
        self.screen.blit(survived_time, (510, 520 - self.death_screen_vertical_offset))
        record_time = self.small_ui_font.render(f"Personal best: {self.record}s", True, (255, 246, 211))
        self.screen.blit(record_time, (550, 635 - self.death_screen_vertical_offset))

        click_to_continue = self.small_ui_font.render("click anywhere to continue", True, (249, 168, 117))
        self.screen.blit(click_to_continue, ((self.resolution[0] - 600) // 2, self.resolution[1] - 50))

    def quit(self) -> None:
        pygame.quit()
        sys.exit()

    def draw_text(self):
        lines = [
            self.font.render(f"Time: {self.time}s", True, (255, 255, 255)),
            self.font.render(f"Distance: {self.player.move_count}", True, (255, 255, 255)),
        ]

        if (self.gameplay_transition_text_horizontal_offset + 3) > 0:
            self.gameplay_transition_text_horizontal_offset = 0
        else:
            self.gameplay_transition_text_horizontal_offset += 3

        for i, line in enumerate(lines):
            self.screen.blit(line, (20 + self.gameplay_transition_text_horizontal_offset, 50 + 50 * i))

        fps_text = self.small_font.render(f"FPS: {int(self.clock.get_fps())}", True, (0, 255, 0))
        self.screen.blit(fps_text, (0, 1060))

        if self.player.god_mode:
            godmode_text = self.small_font.render(f"GodMode Enabled", True, (0, 255, 0))
            self.screen.blit(godmode_text, (0, 1035))

    def handle_trap_timer(self):
        for i in range(round(self.trap_count)):
            if random.randint(0, 5) == 0:
                continue
            self.map.activate_random_trap()
            self.fase_trap_count += 1
            self.total_trap_count += 1

        if self.fase_trap_count >= 5 + self.trap_count_velocity:
            # if (self.trap_count + 1) < 5:
            #     self.trap_count += 1
            self.trap_count += self.trap_count_velocity * self.trap_count_velocity / 2
            self.fase_trap_count = 0
            if (self.trap_spawn_length - 100) >= 1000:
                self.trap_spawn_length -= 100
                pygame.time.set_timer(self.trap_timer_event, max(self.trap_spawn_length, 100))

            if self.size_to_generate == 0:
                self.map.increase_width()
                self.size_to_generate = 1
            else:
                self.map.increase_height()
                self.size_to_generate = 0
            Tile.percentages[1] -= 0.05
            Tile.percentages[2] += 0.05

    def handle_time_timer(self):
        self.time += 1

    def button_click_detection(self):
        x, y = pygame.mouse.get_pos()

        if not self.active_buttons:
            return

        if self.play_button_rect.collidepoint(x, y):
            self.reset()
            self.ui_transition = 1
        if self.exit_button_rect.collidepoint(x, y):
            self.reset()
            self.ui_transition = -1
        if self.controls_button_rect.collidepoint(x, y):
            self.reset()
            self.ui_transition_type = 2
            self.ui_transition = 1
        if self.record_button_rect.collidepoint(x, y):
            self.reset()
            self.ui_transition_type = 2
            self.ui_transition = -1

    def reset(self):
        self.active_buttons = False
        self.gameplay_transition = False
        self.gameplay_active = False
        self.navbar_horizontal_offset = 0
        self.title_horizontal_offset = 0
        self.title_horizontal_velocity = -20
        self.navbar_horizontal_velocity = -20
        self.gameplay_transition_text_horizontal_offset = -375
        self.ui_transition = 0
        self.ui_transition_type = 1
        self.time = 0
        self.trap_count = 0
        self.menu = 0

        self.trap_spawn_length = 2500
        self.trap_count = 1
        self.fase_trap_count = 0
        self.total_trap_count = 0
        self.time = 0

        self.player.move_count = 0
        self.map.fallen_platforms = 0
        self.map.width = 3
        self.map.height = 3

        self.map.min_x = -1
        self.map.max_x = 1
        self.map.min_y = -1
        self.map.max_y = 1

    def handle_event(self, event: pygame.event):
        if event.type == pygame.QUIT:
            self.quit()
        if self.menu == 5:
            self.explanation.handle_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.menu != 0:
                    self.reset()
                    self.active_buttons = True
                else:
                    self.quit()
            elif event.key == pygame.K_w:
                self.player.move(0, -1)
            elif event.key == pygame.K_s:
                self.player.move(0, 1)
            elif event.key == pygame.K_a:
                self.player.move(-1, 0)
            elif event.key == pygame.K_d:
                self.player.move(1, 0)
            elif event.key == pygame.K_UP:
                self.player.move(0, -1)
            elif event.key == pygame.K_DOWN:
                self.player.move(0, 1)
            elif event.key == pygame.K_LEFT:
                self.player.move(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.player.move(1, 0)
            elif event.key == pygame.K_F6:
                self.player.god_mode = True if not self.player.god_mode else False
            # elif event.key == pygame.K_F1:
            #     self.toggle_music()
            elif event.key == pygame.K_F1:
                if self.menu != 5:
                    self.menu = 5
                else:
                    self.menu = 0
        if event.type == self.trap_timer_event:
            self.handle_trap_timer()
        if event.type == self.time_timer_event:
            self.handle_time_timer()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu == 2 or self.menu == 3 or self.menu == 4:
                self.reset()
                self.active_buttons = True
            elif self.menu == 0:
                self.button_click_detection()
        if event.type == pygame.VIDEORESIZE:
            self.display = pygame.display.set_mode((event.w, event.h),
                                              pygame.RESIZABLE)
            self.screen = pygame.Surface((event.w, event.h))

    def handle_key_input(self):
        pass

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.tick()

            pygame.display.update()
            self.clock.tick(self.max_fps)


if __name__ == "__main__":
    game = Game(RESOLUTION, MAX_FPS, SCALE)
    game.run()
