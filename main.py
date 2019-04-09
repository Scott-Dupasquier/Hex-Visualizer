# Hex game and visualizer
# Created by Scott Dupasquier
# Made as a project for CMPUT 497

import pygame
from GameScreen import GameScreen
from pygame.locals import *

def main():
    # Create the window, then run the game screen
    window, width, height = create_window()
    game_screen = GameScreen(window,width,height)
    game_screen.run()
    
def create_window():
    pygame.init()
    height = 600
    width = 800
    window = pygame.display.set_mode((width,height))
    pygame.display.set_caption("Hex Visualizer")
    return window,width,height

main()