#!/usr/bin/env python3
import pygame
import os
import time

def mostrar_splash():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    
    # Cargar imagen de logo
    logo_path = os.path.join(os.path.expanduser('~'), 'assets', 'logo.png')
    if os.path.exists(logo_path):
        logo = pygame.image.load(logo_path)
        logo = pygame.transform.scale(logo, (screen.get_width(), screen.get_height()))
        screen.blit(logo, (0, 0))
    else:
        # Pantalla por defecto si no hay logo
        font = pygame.font.Font(None, 74)
        text = font.render("CONSOLA RETRO", True, (255, 165, 0))
        text_rect = text.get_rect(center=(screen.get_width()/2, screen.get_height()/2))
        screen.fill((0, 0, 0))
        screen.blit(text, text_rect)
    
    pygame.display.flip()
    
    # Reproducir sonido si existe
    sound_path = os.path.join(os.path.expanduser('~'), 'assets', 'sonido.mp3')
    if os.path.exists(sound_path):
        pygame.mixer.init()
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
            time.sleep(3)
        except:
            time.sleep(2)
    else:
        time.sleep(2)
    
    pygame.quit()

if __name__ == "__main__":
    mostrar_splash()