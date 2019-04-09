# Button object in pygame
# All code in this class by Scott Dupasquier

import drawtext
import pygame
from pygame.locals import *

class Button:
    def __init__(self, window, centerx, centery, width, height, colour, text):
        # Location should be a tuple, and the button will be centered around it
        self.centerx = centerx-(width/2) # Center the x coordinate
        self.centery = centery-(height/2) # Center the y coordinate
        
        # Specifications for the buttons rectangle
        self.specs = (self.centerx,self.centery,width,height)
        self.outline = (self.centerx+2,self.centery+2,width+4,height+4)
        self.window = window
        self.colour = colour
        self.text = text
        self.text_loc = (self.centerx + (width/2) - (drawtext.get_width(text)/2)\
                         ,self.centery + (height/2) - (drawtext.get_height(text)/2))
        self.rect = None
        
        # Is the button currently pressed
        self.pushed = False
        
        self.draw()
        return
    
    def draw(self):
        # Draws the button on the window
        pygame.draw.rect(self.window, pygame.Color('Black'), self.outline)
        self.rect = pygame.draw.rect(self.window, self.colour, self.specs)
        drawtext.draw_text(self.text, self.text_loc, self.window)
        return
    
    def check_push(self):
        # Draws the button as pushed down if the user hovers over it or the
        # button has been pushed, otherwise draws it as normal with draw function
        mouse_loc = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_loc) or self.pushed:
            outline_specs = (self.outline[0], self.outline[1], self.outline[2]-2, self.outline[3]-2)
            pygame.draw.rect(self.window, pygame.Color('Black'), outline_specs)
            specs = (self.outline[0], self.outline[1], self.specs[2], self.specs[3])
            self.rect = pygame.draw.rect(self.window, (112,59,7), specs)
            drawtext.draw_text(self.text, (self.text_loc[0]+2,self.text_loc[1]+2), self.window)
        else:
            self.draw()
            
    def change_pushed(self, override=False):
        # Changes the state of the button if the user clicks on it
        mouse_loc = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_loc) or override:
            if self.pushed:
                self.pushed = False
            else:
                self.pushed = True
            return self.pushed
                
    def is_pushed(self):
        # Returns the state of the button (either pushed or not pushed)
        return self.pushed
    
    def get_type(self):
        # Returns the text of the button to determine functionality
        return self.text