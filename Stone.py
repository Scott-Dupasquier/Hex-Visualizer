# Stone object for Hex, can be black, white or no colour

import pygame
from pygame.locals import *

class Stone:
    def __init__(self, window, centerx, centery, colour, row, col):
        self.window = window
        
        # For indexing purposes
        self.row = row
        self.col = col
        
        self.pos = (int(centerx),int(centery))
        self.radius = 15
        
        self.colour = colour
        
        # Keep track of if the stone is captured/dead
        self.is_dead = False
        self.captured = False
        self.captured_colour = None
        self.rect = pygame.draw.circle(self.window, self.colour, self.pos, self.radius)
        
    def update(self):
        # If the stone has been placed then simply draw it, otherwise only draw
        # the stone the user is hovering over
        if self.colour == (0,0,0) or self.colour == (255,255,255) or self.is_dead or self.captured:
            self.draw()
        else:
            mouse_loc = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_loc):
                self.draw()
            
    def draw(self):
        # Draw a black outline to better see the white stone
        if self.colour == (255,255,255) or (self.captured and self.capture_colour==2):
            pygame.draw.circle(self.window, (0,0,0), self.pos, self.radius+1)
            
        if self.is_dead:
            # Draws a small black circle to indicate the cell is dead
            pygame.draw.circle(self.window, (0,0,0), self.pos, 4)
        elif not self.captured:
            # Draw the stone on the board, it has been placed normally
            pygame.draw.circle(self.window, self.colour, self.pos, self.radius)
        
        # Draw the stone as captured, indicated by the large portion of the
        # stone being the capture colour, and draw a second smaller circle in 
        # that of the opponent colour, to distinguish it is captured and not
        # placed 
        if self.captured and self.capture_colour == 1:
            pygame.draw.circle(self.window, (0,0,0), self.pos, self.radius)
            pygame.draw.circle(self.window, (255,255,255), self.pos, 4)
        elif self.captured and self.capture_colour == 2:
            pygame.draw.circle(self.window, (255,255,255), self.pos, self.radius)
            pygame.draw.circle(self.window, (0,0,0), self.pos, 4)            
        
    def place(self, colour):
        # Places a stone only if that stone was clicked
        mouse_loc = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_loc):
            self.set_colour(colour)
            if self.is_dead:
                self.set_live()
            # NEED TO DEAL WITH CAPTURED CELLS HERE
            return self.row,self.col
        
    # Getters and setters for various variables
    def get_coords(self):
        return self.pos
    
    def get_index(self):
        return self.row, self.col
    
    def set_colour(self, colour):
        self.colour = colour
        
    def set_dead(self):
        self.is_dead = True
        
    def set_live(self):
        self.is_dead = False
        
    def set_captured(self, colour, captured):
        self.captured = captured
        self.capture_colour = colour
        
    def get_captured(self):
        return self.captured