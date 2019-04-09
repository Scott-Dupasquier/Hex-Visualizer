# This code has been taken and modified from past projects by myself
# and from the uaio module

import pygame
from pygame.locals import *

def draw_text(print_text, text_loc, window, size=18, colour=(255,255,255)):
	# Draws text on the window
	font = pygame.font.SysFont('times', size) # Font and size
	text = font.render(print_text, True, colour) # Font colour and rendering
	window.blit(text, text_loc)
	
def get_width(print_text, size=18, colour=(255,255,255)):
	# Finds the width of the text to be drawn
	font = pygame.font.SysFont('times', size)
	text = font.render(print_text, True, colour)
	return text.get_width()

def get_height(print_text, size=18, colour=(255,255,255)):
	# Finds the height of the text to be drawn
	font = pygame.font.SysFont('times', size)
	text = font.render(print_text, True, colour)
	return text.get_height()