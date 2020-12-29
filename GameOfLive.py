'''
    A game of life simulation running on a christmas tree
    
    The LED coordinates are used to construct a k-nearest neighbour graph which in turn
    serves as a constrained board for a game of life simulation. 
    The board does not wrap, nor is the nearest neighbour relation symmetric.
'''

def xmaslight():
    # This is the code from my

    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # Here are the libraries I am currently using:
    import time
    import board
    import neopixel
    import re
    import math

    coordfilename = "Python/coords.txt"

    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()

    coords_bits = [i.split(",") for i in coords_raw]

    coords = []

    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)

    # set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords)  # this should be 500

    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

    # YOU CAN EDIT FROM HERE DOWN

    import numpy as np
    import random

    ### Settings

    color = {}
    # Alive color
    color[True]  = [50,0,0] # green
    # Dead color
    color[False] = [20,20,20] # white

    # The number of neihghbours for each cell
    # If the neihghbours are adjusted the rules in Node.updateState should be adjusted as well
    kNeighbours = 8

    # pause between cycles in seconds.
    delay = 20/60

    # Cells are randomly initialized upon start
    #[0-99] Probability that a cell is alive 
    initialProbability = 50

    # convert coordinates to individual numpy vectors
    coords_np = [np.array(coord) for coord in coords]

    class Node:
        '''
            Tree node for k-nearest neighbor graph. 
            Each node represents a single LED
        '''
        def __init__(self, coord, pixelIndex):
            # Coordinates in real world space
            self.coord = coord            
            # The cells current state (True: alive, False: dead)
            self.state = False
            # The cells state for the next animation step
            self.nextState = None
            # index of this node in the pixel array
            self.pixelIndex = pixelIndex
            # k nearest neighbours 
            self.neighbours = []

        def connect(self, neighbour):
            '''
                Let this node know about a potential neighbour. This function should be called
                for all candidates
            '''
            # Calculate euclidean distance between 2 points.
            distance = np.linalg.norm(self.coord - neighbour.coord)

            self.neighbours.append({
                "neighbour": neighbour,
                "distance": distance
                })
        
        def filterNeighbours(self):
            '''
                Sort the neighour candidates by distance and keep only the k closest nodes
            '''
            self.neighbours = sorted(self.neighbours, key = lambda node : node["distance"])[:kNeighbours-1]


        def updateState(self):
            '''
                Update game state for this node. Atomic operation.
                Should be followed by calling updatePixel to reset Node for next frame
            '''
            aliveNeighbours = 0

            for tupel in self.neighbours:
                neighbour = tupel["neighbour"]
                if neighbour.state:
                    aliveNeighbours += 1

            #dead = kNeighbours - aliveNeighbours

            #Any live cell ,
            if self.state :
                #1. with fewer than two live neighbours dies
                if aliveNeighbours < 2:
                    self.nextState = False
                #2 two or three live neighbours lives on to the next generation.
                #3 with more than three live neighbours dies, as if by overpopulation
                elif aliveNeighbours > 3:
                    self.nextState = False
                else:
                    self.nextState = True
            else:
                #4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
                if aliveNeighbours == 3:
                    self.nextState = True
                else:
                    self.nextState = False

        def updatePixel(self):
            self.state = self.nextState
            self.nextState = None
            pixels[self.pixelIndex] = color[self.state]
            
        # def printDistance(self):
            # return str(self.coord) + " " + '<'.join('%.2f' % neighbour["distance"] for neighbour in self.neighbours)


    class RandomAccessGraph:
        '''
            Wrapper class to access individual nodes by index as well as propagating 
            function calls to each node
        '''
        def __init__(self,coords):
            self.nodes = []

            for i in range(len(coords)):
                self.nodes.append(Node(coords[i],i))

            # Fully connect graph. Calculate distance between each point
            for n0 in self.nodes:
                for n1 in self.nodes:
                    if n0 != n1:
                        n0.connect(n1)

            # Only keep the closest x nodes as neighbours
            for node in self.nodes:
                node.filterNeighbours()

        def updateNetwork(self):
            '''
                Animation frame
            '''
            for node in self.nodes:
                node.updateState()

            for node in self.nodes:
                node.updatePixel()

        def length(self):
            return len(self.nodes)

        def __getitem__(self,index):
            return self.nodes[index]

    # Construct the game of life board
    graph = RandomAccessGraph(coords_np)

    ##Initialize state
    for node in graph:
        
        node.state = (initialProbability != 0) and random.randint(0,100) <= initialProbability

    while True:

        # Each node tells it's neighbours about it's current color and brightness
        graph.updateNetwork()
        #debug boardState = [x.state for x in graph]
        
        pixels.show()      

        #Sleep of 0 causes context switch. does this matter for performance on a pi?
        time.sleep(delay)      

xmaslight()
