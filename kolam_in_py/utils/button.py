from .colors import Colors
import pygame

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
            "toggled_hover": Colors.LIME,
        }
        self.font = pygame.font.SysFont(font, font_size)
        self.pressed = False
        self.toggled = False
        self.key_flash_timer = 0

    def get_topleft(self):
        return self.rect.topleft

    def get_topright(self):
        return self.rect.topright

    def get_bottomleft(self):
        return self.rect.bottomleft

    def get_bottomright(self):
        return self.rect.bottomright

    def trigger_key_action(self):
        if self.toggle:
            self.toggled = not self.toggled
        else:
            self.key_flash_timer = 5

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
        color = self.colors["normal"]

        if self.key_flash_timer > 0:
            color = self.colors["pressed"]
            self.key_flash_timer -= 1
        
        elif self.toggle:
            if self.toggled:
                if self.rect.collidepoint(mouse_pos):
                    color = self.colors["toggled_hover"]
                else:
                    color = self.colors["pressed"]
            elif self.rect.collidepoint(mouse_pos):
                color = self.colors["hover"]
        
        else:
            if self.pressed:
                color = self.colors["pressed"]
            elif self.rect.collidepoint(mouse_pos):
                color = self.colors["hover"]

        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        text_surf = self.font.render(self.text, True, Colors.BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
