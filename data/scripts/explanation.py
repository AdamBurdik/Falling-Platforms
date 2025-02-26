import pygame


class Explanation:
    def __init__(self, game):
        self.game = game

        self.scale = 6
        self.slide_index = 0

        self.slides = self.load_slides()
        self.crush_top = pygame.transform.scale(
            pygame.image.load("data/assets/tiles/crush_top.png").convert_alpha(),
            (32 * self.scale, 42 * self.scale)
        )
        self.crush_offset = -800

        self.default = pygame.transform.scale(
            pygame.image.load("data/assets/tiles/default.png").convert_alpha(),
            (32 * self.scale, 64 * self.scale)
        )
        self.default_offset = 50

        self.handle_new_slide()

    def load_slides(self) -> list:
        slides = []

        print(self.game.mainscreen_ui_scale)
        for i in range(1, 6 + 1):
            slides.append(
                pygame.transform.scale(
                        pygame.image.load(f"data/assets/explanation/slide_{i}.png").convert_alpha(),
                        (240 * self.scale, 135 * self.scale)
                )
            )

        return slides

    def tick(self):
        pos = (
            (pygame.display.get_window_size()[0] - 240 * self.scale) / 2,
            (pygame.display.get_window_size()[1] - 135 * self.scale) / 2
        )

        self.game.render_background()
        self.game.screen.blit(self.slides[self.slide_index], pos)

        if self.slide_index == 3:
            self.game.screen.blit(self.crush_top, (636, 150 + 177 + self.crush_offset))
            if self.crush_offset < 0:
                self.crush_offset += 20
            else:
                self.crush_offset = 0
        if self.slide_index == 4:
            self.game.screen.blit(self.default, (1035, 240 + 177 + self.default_offset))
            self.default_offset += 15


    def handle_new_slide(self):
        self.crush_offset = -800
        self.default_offset = 50

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.menu = 0
            if event.key == pygame.K_RIGHT:
                self.slide_index += 1
                if self.slide_index > 5:
                    self.slide_index = 5
                self.handle_new_slide()
            if event.key == pygame.K_LEFT:
                if self.slide_index >= 1:
                    self.slide_index -= 1
                    self.handle_new_slide()

