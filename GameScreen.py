# Game Screen class for Hex game
# Deals with the majority of calculations for the visualizer

import pygame
from pygame.locals import *
import math
from Button import Button
from Stone import Stone
import drawtext

class GameScreen:
    def __init__(self,window,width,height):
        self.window = window
        self.window_width = width
        self.window_height = height
        
        self.bg_color = (255,255,255) # Background colour
        
        self.img_board = pygame.image.load("hex6x6.png")
        
        # 6x6 board
        self.n = 6
        self.board = self.initialize_board()
        
        # Virtual connections/dead cells/captured cells buttons and arrays
        self.vcs_button = None
        self.virtual_connections = []
        self.dead_button = None
        self.dead_cells = []
        self.captured_button = None
        self.captured_cells = []
        
        # Necessary buttons: Place Black/White Stone, Clear Board, Remove Stone,
        # Dead Cells, Captured Cells, Virtual Connections
        self.button_list = []
        self.create_buttons()
        
        # Highlight in this colour when hovering over an open stone position
        self.highlight_pos = (125,125,125)
        self.stone_colour = self.highlight_pos
        self.stone_list = []
        self.place_stones()
        
        self.text = [("Hex Visualizer", [width/2,drawtext.get_height("Hex Visualizer", 48)/2], 48),
                     ("Created by Scott Dupasquier", [width/2,drawtext.get_height("Hex Visualizer", 48) + 
                                                      drawtext.get_height("Created by Scott Dupasquier", 18)/2], 18)]
        
        pygame.display.update()
        
    def run(self):
        # Game loop, does all updates on screen
        run = True
        while run:
            # Draw the game board, text
            # Updates the buttons, virtual connections and stones
            self.window.fill(self.bg_color)
            self.window.blit(self.img_board, (self.window_width/4, self.window_height/4))
            self.update_text()
            self.update_buttons()
            if self.vcs_button.is_pushed():
                self.update_vcs()
            self.update_stones()
            pygame.display.update()
            
            for event in pygame.event.get():
                # If user quits or presses escape close the game
                if event.type == QUIT:
                    run = False
                    pygame.quit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        run = False
                        pygame.quit()
                        
                if event.type == MOUSEBUTTONDOWN:
                    # On a click, see if a button has been pressed or a stone
                    # has been placed
                    self.change_button_state()
                    self.place_single_stone()
                    
                    # When these buttons are pressed, find the corresponding things
                    if self.vcs_button.is_pushed():
                        self.find_virtual_connections()
                    if self.dead_button.is_pushed():
                        self.find_dead_cells()
                    if self.captured_button.is_pushed():
                        self.find_captured_cells()
                        
    def create_buttons(self):
        # Makes all the buttons in the game and adds them to the buttons list
        brown = (151,77,5)
        width = 100
        height = 50
        
        black = Button(self.window, self.window_width/8, self.window_height/3,
                              width, height, brown, "Place Black")
        self.button_list.append(black)
        
        white = Button(self.window, self.window_width/8, self.window_height/3 + 75, 
                       width, height, brown, "Place White")
        self.button_list.append(white)
        
        remove = Button(self.window, self.window_width/8, self.window_height/3 + 150,
                       width, height, brown, "Remove")
        self.button_list.append(remove)
        
        clear = Button(self.window, self.window_width/8, self.window_height/3 + 225,
                       width, height, brown, "Clear")
        self.button_list.append(clear)
        
        self.vcs_button = Button(self.window, self.window_width * 7/8, self.window_height/3,
                                 width*3/2, 40, brown, "Virtual Connections");
        self.button_list.append(self.vcs_button)
        
        self.dead_button = Button(self.window, self.window_width * 7/8, self.window_height/3 + 60,
                      width*3/2, 40, brown, "Dead Cells")
        self.button_list.append(self.dead_button)
        
        self.captured_button = Button(self.window, self.window_width * 7/8, self.window_height/3 + 120,
                          width*3/2, 40, brown, "Captured Cells")
        self.button_list.append(self.captured_button)
        
    def change_button_state(self):
        for button in self.button_list:
            # Determine if button has been pushed and if it is on or off
            on = button.change_pushed()
            
            # Unpress other buttons that may be held down and can't be
            if on:
                index = self.button_list.index(button)
                
                # Only 4 buttons should change the held down state of others
                if index < 4:
                    for btn in range(3): # Only 3 buttons can be held down
                        if btn != index and self.button_list[btn].is_pushed():
                            self.button_list[btn].change_pushed(True)
            
            if on and ("Black" in button.get_type()):
                self.stone_colour = (0,0,0) # Stone colour is now black
                
            elif on and ("White" in button.get_type()):
                self.stone_colour = (255,255,255) # Stone colour is now white
                
            elif on and ("Remove" in button.get_type()):
                self.stone_colour = self.highlight_pos # Stone reset to highlight
                
            elif on and ("Clear" in button.get_type()):
                # Resets all necessary things after being cleared
                self.stone_colour = self.highlight_pos
                self.stone_list = []
                self.virtual_connections = []
                self.dead_cells = []
                self.captured_cells = []
                self.place_stones()
                self.board = self.initialize_board() # Clear board
                if "Win" in self.text[len(self.text)-1][0]:
                    self.text.pop() # Remove win statement
                button.change_pushed() # Can only press once, not holdable
                
            elif on and ("Virtual" in button.get_type()):
                self.find_virtual_connections() # Find the virtual connections
                
            elif on and ("Dead" in button.get_type()):
                self.find_dead_cells() # Find the dead cells
            elif not self.dead_button.is_pushed() and ("Dead" in button.get_type()):
                for row,col in self.dead_cells:
                    # Change all stones to now be live again
                    self.stone_list[row * (self.n+2) + col].set_live()
                self.dead_cells = []
                
            elif on and ("Captured" in button.get_type()):
                self.find_captured_cells() # Find all captured cells
            elif not on and ("Captured" in button.get_type()):
                for row,col in self.captured_cells:
                    self.stone_list[row * (self.n+2) + col].set_captured(None, False)
                self.captured_cells = []
        
        # If place black/white buttons both aren't pressed reset the stone 
        # colour to the default highlight colour
        if not self.button_list[0].is_pushed() and not self.button_list[1].is_pushed():
            self.stone_colour = self.highlight_pos

    def update_buttons(self):
        for button in self.button_list:
            button.check_push() # Check if the button has been pushed
        
    def update_stones(self):
        for stone in self.stone_list:
            row,col = stone.get_index()
            if row >= 1 and row <= self.n and col >= 1 and col <= self.n:
                # Only update stones that we want to see on the board
                stone.update()
            
    def place_stones(self):
        # Places all the stones on the board in their correct location. Goes to
        # n+2 since we place "fake" stones at the top/bottom and sides to easier
        # determine virtual connections/dead cells etc
        x = 255 - (45.75*3/2)
        y = 207 - 39.5
        for row in range(0, self.n+2):
            for col in range(0, self.n+2):
                stone = Stone(self.window, x, y, self.stone_colour, row, col)
                if row == 0 or row == self.n + 1:
                    stone.set_colour((0,0,0))
                elif col == 0 or col == self.n + 1:
                    stone.set_colour((255,255,255))
                self.stone_list.append(stone)
                x+=45.75
            x-=(45.75*(self.n+1)) + (45.75/2)
            y+=39.5
            
    def place_single_stone(self):
        for stone in self.stone_list:
            try:
                # Can't click a stone that is not supposed to show up
                row, col = stone.place(self.stone_colour)
                assert row >= 1 and row <= self.n
                assert col >= 1 and col <= self.n
            except:
                continue
            else:
                # Change the board to reflect the click, check if a win happened
                if self.stone_colour == (0,0,0):
                    self.board[row][col] = 1
                    self.check_win((row,col), 1)
                    self.remove_vcs((row,col))
                elif self.stone_colour == (255,255,255):
                    self.board[row][col] = 2
                    self.check_win((row,col), 2)
                    self.remove_vcs((row,col))
                else:
                    self.board[row][col] = 0
                    self.remove_vcs((row,col))
                    
                    if "Win" in self.text[len(self.text)-1][0]: # Know a win did/still does exist
                        if "Black" in self.text[2][0]:
                            # Check to see if the win statement should still exist
                            for col in range(self.n):
                                win = self.check_win((0,col), 1)
                                if win:
                                    break
                                elif col == self.n-1:
                                    self.text.pop()
                                    
                        elif "White" in self.text[2][0]:
                            # Check to see if the win statement should still exist
                            for row in range(self.n):
                                win = self.check_win((row,0), 2)
                                if win:
                                    break
                                elif row == self.n-1:
                                    self.text.pop()
        
    def initialize_board(self):
        # Creates an array of numbers to reflect the board state, 0 is empty,
        # 1 is black, and 2 is white
        board = []
        board.append([1] * (self.n + 2))
        for row in range(self.n):
            new_row = [0] * (self.n+2)
            new_row[0] = 2
            new_row[self.n+1] = 2
            board.append(new_row)
        board.append([1] * (self.n+2))
        
        return board
    
    def update_text(self):
        # Draws all necessary text on the screen
        for text in self.text:
            # Center the coordinates
            loc = list(text[1])
            loc[0] -= drawtext.get_width(text[0], text[2])/2 # x
            loc[1] -= drawtext.get_height(text[0], text[2])/2 # y
            
            drawtext.draw_text(text[0], loc, self.window, text[2], (0,0,0))
    
    def check_win(self, pos, colour):
        # Gets the line of all connected pieces to what was just placed
        if self.board[pos[0]][pos[1]] != colour:
            # If the point is not the same colour we are checking then it will
            # not be a win for that colour and so return False
            return False
        
        line = self.find_line(pos, colour, [])
        
        stretch = [] # Find how far the line stretches accross the board
        
        for index in line:
            if index[colour-1] not in stretch:
                stretch.append(index[colour-1])
                
        if "Win" not in self.text[len(self.text)-1][0]: # No need to re-add if win already exists
            # If the line stretches the entire board then we have a win
            if len(stretch) >= self.n and colour == 1:
                self.text.append(("Black Wins!", [self.window_width/2, self.window_height * 7/8], 32))
            
            elif len(stretch) >= self.n and colour == 2:
                self.text.append(("White Wins!", [self.window_width/2, self.window_height * 7/8], 32))
        
        if len(stretch) >= self.n:
            return True
        else:
            return False
    
    def find_line(self, pos, colour, connected_inds):
        # Starting at a given cell, find the entire line of connected cells
        # by finding the neighbours then recursively finding the next cells
        # neighbours and so on
        neighbours = self.find_neighbours(pos[0], pos[1]) # row, col
        connected_inds.append(pos)
        
        for neighbour in neighbours:
            # Neighbour must contain the same colour
            if neighbour not in connected_inds and self.board[neighbour[0]][neighbour[1]] == colour:
                self.find_line(neighbour, colour, connected_inds)
                
        return connected_inds
    
    def find_neighbours(self, row, col):
        # Finds all the neighbours of a given cell. The calculations can be seen
        # by observing a hex board and seeing what the neighbours row/col is
        nbrs = []
        
        if (row-1 >= 1):
            nbrs.append((row-1,col))
            if (col+1 <= self.n):
                nbrs.append((row-1,col+1))
        if (col+1 <= self.n):
            nbrs.append((row,col+1))
        if (col-1 >= 1):
            nbrs.append((row,col-1))
        if (row+1 <= self.n):
            nbrs.append((row+1,col))
            if (col-1 >= 1):
                nbrs.append((row+1,col-1))
                
        return nbrs
    
    def find_virtual_connections(self):
        # Need to find all virtual connections that exist on the board
        # If time permits, try to find better virtual connections that show good moves
        
        # ALGORITHM:
        # 1. Find potential cells that will form a vc: (row-2,col+1), (row-1,col+2), (row+1,col+1), (row+2,col-1), (row+1,col-2), (row-1,col-1)
        # 2. Check that if said cells contain the same colour as our cell
        # 3. Check that the cells between those are empty
        # 4. If non-empty do nothing, otherwise display a connection between them
        
        for row in range(1, self.n+2):
            for col in range(0, self.n+1):
                if self.board[row][col] == 0:
                    continue # No virtual connections for empty cells
                else:
                    # 6 potential virtual connection cases, only consider each
                    # once (3 cases), consider cases where the connection is 
                    # above origin,rest of cases will be taken care of by lower cells
                    potential = [(row-2,col+1), (row-1,col+2), (row-1,col-1)]
                
                for vc in potential:
                    # Check that the potential connection is within the bounds
                    # of the board, then check they are the same colour
                    if vc[0] >= 0 and vc[0] <= self.n+1 and vc[1] >= 0 and vc[1] <= self.n+1:
                        if self.board[vc[0]][vc[1]] == self.board[row][col]:
                            nbrs1 = self.find_neighbours(row, col)
                            nbrs2 = self.find_neighbours(vc[0], vc[1])
                            # Find the intersection of the lists
                            intersect = list(set(nbrs1) & set(nbrs2))
                            # Now determine if both cells are empty
                            if len(intersect) == 2 and \
                               self.board[intersect[0][0]][intersect[0][1]] == 0 and \
                               self.board[intersect[1][0]][intersect[1][1]] == 0:
                                # Cells empty, add virtual connection
                                self.add_vc((row,col), vc, intersect, potential.index(vc))
        
        return
    
    def add_vc(self, origin, end, intersect, case):
        # Add the existing virtual connection to the list so it can be updated
        pos1 = self.stone_list[origin[0]*(self.n+2) + origin[1]].get_coords()
        pos2 = self.stone_list[end[0]*(self.n+2) + end[1]].get_coords()
    
        arc_len = 86
        
        # The specs following this are specifications for drawing the arc on
        # screen when displaying the virtual connection
        # TOP: 7/4, 1/4
        if case == 0:
            specs = [(origin, end, intersect[0], intersect[1]), 
                     [pos1[0] - (arc_len*.8), pos1[1] - (arc_len*.93), arc_len, arc_len], -math.pi/4, math.pi/4]
            specs2 = [(origin, end, intersect[0], intersect[1]), 
                      [pos1[0] - (arc_len*.2), pos1[1] - (arc_len*.93), arc_len, arc_len], math.pi*3/4, math.pi*5/4]
        # RIGHT: 3/2, 0
        elif case == 1:
            specs = [(origin, end, intersect[0], intersect[1]), 
                     [pos1[0] - (arc_len*.31), pos1[1] - (arc_len*.95), arc_len, arc_len], math.pi*4/3 + math.pi/8, math.pi*11/6 + math.pi/8]
            specs2 = [(origin, end, intersect[0], intersect[1]), 
                      [pos1[0] + (arc_len/20), pos1[1] - (arc_len*.45), arc_len, arc_len], math.pi/3 + math.pi/8, math.pi*5/6 + math.pi/8]
        # LEFT: 0, 1/2
        else:
            specs = [(origin, end, intersect[0], intersect[1]), 
                     [pos1[0] - (arc_len*1.05), pos1[1] - (arc_len*.45), arc_len, arc_len], -(math.pi*11/6 + math.pi/8), -(math.pi*4/3 + math.pi/8)]
            specs2 = [(origin, end, intersect[0], intersect[1]), 
                      [pos1[0] - (arc_len*.7), pos1[1] - (arc_len*.98), arc_len, arc_len], -(math.pi*5/6 + math.pi/8), -(math.pi/3 + math.pi/8)]
        
        if specs not in self.virtual_connections and \
           specs2 not in self.virtual_connections:
            self.virtual_connections.append(specs)
            self.virtual_connections.append(specs2)
        return
    
    def remove_vcs(self, origin):
        # Upon removing a stone/placing a stone remove any virtual connections
        # that should no longer exist
        for connection in range(len(self.virtual_connections)-1, -1, -1):
            if origin in self.virtual_connections[connection][0]:
                del(self.virtual_connections[connection])
    
    def update_vcs(self):
        # Draw all virtual connections on the board
        for connect in self.virtual_connections:
            pygame.draw.arc(self.window, (0,0,0), connect[1], connect[2], connect[3])
        return
    
    def find_dead_cells(self):
        # Find all the dead cells that exist on the board
        for row in range(1, self.n+1):
            for col in range(1, self.n+1):
                if self.board[row][col] == 0:
                    # Find if dead from the is_dead function
                    dead = self.is_dead(row,col)
                
                    if dead:
                        self.stone_list[row*(self.n+2) + col].set_dead()
                        self.dead_cells.append((row,col))
                    else:
                        self.stone_list[row*(self.n+2) + col].set_live()
                        try:
                            self.dead_cells.remove((row,col))
                        except:
                            continue
                
        return
    
    def is_dead(self, row, col):
        # Find if a single cell on the board is dead
        nbrs = self.find_neighbours(row,col)
        
        # Must be dead to black and white
        dead = [False, False]
        
        for colour in range(1,3): # Black/White
            
            empty = []
            initial = []
            for nbr in nbrs:
                connect = []
                if self.board[nbr[0]][nbr[1]] == 0:  # For all empty neighbours
                    empty.append(nbr)
                else:
                    # Find all lines relevant to the colour
                    if self.board[nbr[0]][nbr[1]] == colour:
                        line = self.find_line(nbr, colour, [])
                        for cell in line:
                            if cell in nbrs:
                                connect.append(cell)
                                
                        # Make sure it hasn't already been added as a line
                        seen = False
                        for prev_line in initial:
                            if nbr in prev_line:
                                seen = True
                                break
                                
                        if not seen:
                            initial.append(connect)
            
            # Checks to see if the empty cells are already connected
            connected = []
            for empty_cell in empty:
                empty_cell_nbrs = self.find_neighbours(empty_cell[0], empty_cell[1])
                shared_nbrs = list(set(empty_cell_nbrs) & set(nbrs))
                for shared_cell in shared_nbrs:
                    if self.board[shared_cell[0]][shared_cell[1]] == colour or \
                       (((empty_cell[0] == 1 or empty_cell[0] == 6) and colour == 1) or \
                        ((empty_cell[1] == 1 or empty_cell[1] == 6) and colour == 2)):
                        if empty_cell not in connected:
                            connected.append(empty_cell)
            
            # All empty cells are connected to, cell could be dead
            if len(connected) == len(empty):
                dead[colour-1] = True # Assume dead until proven otherwise
                for line in initial:
                                
                    # Find how far the stretch is with and without the cell we
                    # are trying to determine if dead
                    stretch_initial = self.stretch(line,colour)
                    line.append((row,col))
                    stretch_with = self.stretch(line,colour)
                    
                    if stretch_with > stretch_initial:
                        dead[colour-1] = False # Improves the stretch so can't be dead
                        
            elif len(connected) < len(empty) and len(empty) < 3 and len(nbrs) > 2:
                # Need to find a way to determine if the cell is surrounded by
                # the other colour and is no longer advantageous to use
                for nbr in nbrs:
                    amnt_connected_nbrs = 0
                    opponent_colour = 2
                    if colour == 2:
                        opponent_colour = 1
                    line = self.find_line(nbr, opponent_colour, [])
                    for cell in line:
                        if cell in nbrs:
                            amnt_connected_nbrs += 1
                            
                    if ((nbr[0] == 1 or nbr[0] == 6) and opponent_colour == 1) or \
                       ((nbr[1] == 1 or nbr[1] == 6) and opponent_colour == 2):
                        # On an edge so we're automatically connected to 2 
                        # ending cells
                        amnt_connected_nbrs += 2
                        
                    # If the opponent has a line surrounding the cell it is not
                    # advantageous to use
                    if amnt_connected_nbrs >= 4:
                        dead[colour-1] = True
        
        # Return true if both black and white find the cell to be dead
        return dead[0] and dead[1]

    def stretch(self, array, colour):
        # How far does the set stretch on the board
        stretch = []
        for cell in array:
            if cell[colour-1] not in stretch:
                stretch.append(cell[colour-1])
        return len(stretch)
                
    def find_captured_cells(self):
        # Find all captured cells that exist on the board
        for row1 in range(1, self.n+1):
            for col1 in range(1, self.n+1):
                if self.board[row1][col1] != 0:
                    # Cell is already colored, so move to the next cell
                    continue
                for row2 in range(1, self.n+1):
                    for col2 in range(1, self.n+1):
                        if self.board[row2][col2] != 0:
                            # Cell is already coloured, move to next cell
                            continue
                        
                        if row1==row2 and col1==col2:
                            # Same cell, move to next cell
                            continue
                        
                        # Have two cells, need to determine if coloring one
                        # leaves the other dead in both cases
                        for colour in range(1,3):
                            self.board[row1][col1] = colour
                            dead1 = self.is_dead(row2, col2)
                            self.board[row1][col1] = 0                 
                            self.board[row2][col2] = colour
                            dead2 = self.is_dead(row1,col1)
                            self.board[row2][col2] = 0
                            
                            if dead1 and dead2 and not self.stone_list[row1*(self.n+2) + col1].get_captured():
                                # Both these cells have been captured
                                self.stone_list[row1*(self.n+2) + col1].set_captured(colour, True)
                                self.stone_list[row2*(self.n+2) + col2].set_captured(colour, True)
                                self.captured_cells.append((row1,col1))
                                self.captured_cells.append((row2,col2))
                                
        return
     
    def print_board(self):
        # Purely for debugging, convenience for me only
        for row in self.board:
            print(row)
        print()