import pygame
import os

class Button:
    def __init__(self, text, x, y, width, height, callback, sound_manager=None, type=0):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.sound_manager = sound_manager
        self.type = type
        if type == 1:
            self.color = (63, 48, 43)
            self.text_color = (251, 226, 204)
        else:
            self.color = (251, 226, 204)
            self.text_color = (63, 48, 43)
        self.border_color = (63, 48, 43)
        self.border_width = 3
        font_path = os.path.join("assets", "fonts", "newsweekly", "newsweekly-Regular.ttf")
        self.font = pygame.font.Font(font_path, 36)
        self.joystick_connected = False
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_connected = True

    def draw(self, screen):
        pygame.draw.rect(screen, self.border_color, self.rect.inflate(self.border_width * 2, self.border_width * 2), border_radius=10)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=7)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if self.joystick_connected and event.type == pygame.JOYBUTTONDOWN and self.joystick.get_button(0):
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if self.sound_manager:
                    self.sound_manager.play_sound("select")
                self.callback()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.sound_manager:
                    self.sound_manager.play_sound("select")
                self.callback()