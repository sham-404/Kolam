import pygame


class Colors:
    # Achromatic (Grayscale)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    MEDIUM_GRAY = (70, 70, 70)
    LIGHT_GRAY = (211, 211, 211)
    DARK_GRAY = (30, 30, 30)

    # Primary Colors
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Secondary Colors
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

    # Shades and Tints
    MAROON = (128, 0, 0)
    DARK_GREEN = (0, 128, 0)
    NAVY = (0, 0, 128)
    TEAL = (0, 128, 128)
    PURPLE = (128, 0, 128)
    OLIVE = (128, 128, 0)

    # Bright and Pastel
    ORANGE = (255, 165, 0)
    PINK = (255, 192, 203)
    LIME = (0, 255, 0)
    SKY_BLUE = (135, 206, 235)
    GOLD = (255, 215, 0)


class Button:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        text="default",
        one_press=False,
        toggle=False,
        border_radius=5,
        font: str | None = None,
        font_size=20,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.one_press = one_press
        self.border_radius = border_radius
        self.toggle = toggle
        self.colors = {
            "normal": Colors.TEAL,
            "hover": Colors.CYAN,
            "pressed": Colors.DARK_GREEN,
        }
        self.font = pygame.font.SysFont(font, font_size)
        self.pressed = False
        self.toggled = False

    def get_topleft(self):
        return self.rect.topleft

    def get_topright(self):
        return self.rect.topright

    def get_bottomleft(self):
        return self.rect.bottomleft

    def get_bottomright(self):
        return self.rect.bottomright

    def check_click(self, event):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.toggle:
                    self.toggled = not self.toggled
                    action = True

                else:
                    self.pressed = True
                    if self.one_press:
                        action = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if not self.toggle and self.pressed:
                    self.pressed = False
                    if not self.one_press:
                        action = True

        else:
            if not self.toggle and self.pressed:
                self.pressed = False

        return action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        if self.toggle:
            color = self.colors["pressed"] if self.toggled else self.colors["normal"]

        else:
            if self.pressed:
                color = self.colors["pressed"]

            elif self.rect.collidepoint(mouse_pos):
                color = self.colors["hover"]

            else:
                color = self.colors["normal"]

        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, Colors.BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
