#!/usr/bin/env python

"""
Pygame Tutorial 4
Breakout: Step 1 - The Setup

Written by Collin "Keeyai" Green
Version 1.0.0 - 2010-12-27
"""

try:
    import sys, os, math, random
    import pygame
    from pygame.locals import *

except ImportError, err:
    print "%s Failed to Load Module: %s" % (__file__, err)
    sys.exit(1)

class Paddle(pygame.sprite.Sprite):
    """A paddle sprite. Subclasses the pygame sprite class.
    Handles its own position so it will not go off the screen."""

    def __init__(self, xy):
        # initialize the pygame sprite part
        pygame.sprite.Sprite.__init__(self)
        # set image and rect
        self.image = pygame.image.load(os.path.join('images','paddle.gif'))
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()

        # set position
        self.rect.centerx, self.rect.centery = xy

        # the movement speed of our paddle
        self.movementspeed = 5

        # the current velocity of the paddle -- can only move in X direction
        self.velocity = 0

    def left(self):
        """Increases the velocity"""
        self.velocity -= self.movementspeed

    def right(self):
        """Decreases the velocity"""
        self.velocity += self.movementspeed

    def move(self, dx):
        """Move the paddle in the x direction. Don't go past the sides"""
        if dx != 0:
            if self.rect.right + dx > 510:
                self.rect.right = 510
            elif self.rect.left + dx < 10:
                self.rect.left = 10
            else:
                self.rect.x += dx

    def update(self):
        """Called to update the sprite. Do this every frame. Handles
        moving the sprite by its velocity"""
        self.move(self.velocity)

    def reset(self):
        """Moves the paddle to the center of the booard"""
        self.center = 260, 550


class Block(pygame.sprite.Sprite):
    """A block sprite. Has a level and a position."""
    def __init__(self, xy, images, level=1):
        pygame.sprite.Sprite.__init__(self)

        # save images and level
        self.images = images
        self.level = level

        # set image and rect so we can be rendered
        self.image = self.images[self.level]
        self.rect = self.image.get_rect()

        # set initial position
        self.rect.center = xy


class SolidBlock(pygame.sprite.Sprite):
    """A block that can't be destroyed"""
    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', 'block_gray.png'))
        self.rect = self.image.get_rect()

        # set position
        self.rect.center = xy


class BlockFactory(object):
    """Using this class to return blocks with a copy of the images
        already loaded. No sense in re-loaded all the images for
        every block every time one is created."""

    def __init__(self):
        # load all our block images
        self.images = {
            1: pygame.image.load(os.path.join('images','block_blue.png')),
            2: pygame.image.load(os.path.join('images','block_green.png')),
            3: pygame.image.load(os.path.join('images','block_red.png')),
            4: pygame.image.load(os.path.join('images','block_orange.png')),
            5: pygame.image.load(os.path.join('images','block_purple.png'))
        }

    def getBlock(self, xy, level=1):
        return Block(xy, self.images, level)

    def getSolidBlock(self, xy):
        return SolidBlock(xy)


class Game(object):
    """Our game object! This is a fairly simple object that handles the
    initialization of pygame and sets up our game to run."""

    def __init__(self):
        """Called when the the Game object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools
        that we will need for more complicated tutorials."""

        # load and set up pygame
        pygame.init()

        # create our window
        self.window = pygame.display.set_mode((520, 600))

        # clock for ticking
        self.clock = pygame.time.Clock()

        # set the window title
        pygame.display.set_caption("Pygame Tutorial 4 - Breakout")

        # tell pygame to only pay attention to certain events
        # we want to know if the user hits the X on the window, and we
        # want keys so we can close the window with the esc key
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        # make background
        self.background = pygame.image.load(os.path.join('images','background.jpg'))
        # blit the background onto the window
        self.window.blit(self.background, (0,0))
        # flip the display so the background is on there
        pygame.display.flip()

        # a sprite rendering group for our ball and paddle
        self.sprites = pygame.sprite.RenderUpdates()

        # create our paddle and add to sprite group
        self.paddle = Paddle((260,550))
        self.sprites.add(self.paddle)

        # create sprite group for blocks
        self.blocks = pygame.sprite.RenderUpdates()

        # create our blockfactory object
        self.blockfactory = BlockFactory()

        # load the first level
        self.loadLevel()

    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        print 'Starting Event Loop'

        running = True
        # run until something tells us to stop
        while running:

            # tick pygame clock
            # you can limit the fps by passing the desired frames per seccond to tick()
            self.clock.tick(60)

            # handle pygame events -- if user closes game, stop running
            running = self.handleEvents()

            # update the title bar with our frames per second
            pygame.display.set_caption('Pygame Tutorial 4 - Breakout   %d fps' % self.clock.get_fps())

            # update our sprites
            for sprite in self.sprites:
                sprite.update()

            # render our sprites
            self.sprites.clear(self.window, self.background)    # clears the window where the sprites currently are, using the background
            dirty = self.sprites.draw(self.window)              # calculates the 'dirty' rectangles that need to be redrawn

            # render blocks
            self.blocks.clear(self.window, self.background)
            dirty += self.blocks.draw(self.window)

            # blit the dirty areas of the screen
            pygame.display.update(dirty)                        # updates just the 'dirty' areas

        print 'Quitting. Thanks for playing'

    def handleEvents(self):
        """Poll for PyGame events and behave accordingly. Return false to stop
        the event loop and end the game."""

        # poll for pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            # handle user input
            elif event.type == KEYDOWN:
                # if the user presses escape, quit the event loop.
                if event.key == K_ESCAPE:
                    return False

                # paddle control
                if event.key == K_a or event.key == K_LEFT:
                    self.paddle.left()
                if event.key == K_d or event.key == K_RIGHT:
                    self.paddle.right()

                # serve with space if the ball isn't moving
                if event.key == K_SPACE:
                    pass

            elif event.type == KEYUP:
                # paddle control
                if event.key == K_a or event.key == K_LEFT:
                    self.paddle.right()
                if event.key == K_d or event.key == K_RIGHT:
                    self.paddle.left()
        return True

    def loadLevel(self):
        """Loads a level. Places blocks on the board and adds them to the
        blocks render group"""
        level = [
            [0, 1, 1, 2, 1, 1, 2, 1, 1, 0],
            [0, 0, 2, 3, 4, 4, 3, 2, 0, 0],
            [0, 0, 0, 4, 5, 5, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

##        level = [
##            [0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
##            [0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
##            [0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
##            [0, 0, 0, 0, 0, 0, 0, 0, 0 ,0],
##            [0, 0, 0, 0, 0, 0, 0, 0, 0 ,0]
##        ]

        # levels are a 2d array with 5 rows and 10 columns
        # each space represents a block
        for i in range(5):              # for every row
            for j in range(10):         # for every column
                if level[i][j] != 0:    # if the space isnt empty
                    blocklevel = level[i][j]    # get the level of the block
                    x = 35 + (50*j) # x = 10 (for the wall) + 25 (to center of first block)
                                    # + 50 (width of a block) * j (number of blocks over we are)
                    y = 20 + (20*i) # y = 10 (for the wall ) + 10 (to center of first block)
                                    # + 20 (height of a block) * i (number of blocks down)

                    # if greater than 0 and less than 6, ie not a gray block
                    if blocklevel > 0 and blocklevel < 6:
                        # create a block and add it
                        self.blocks.add(self.blockfactory.getBlock((x,y), blocklevel))

                    # if block level == 6, solid block
                    elif blocklevel == 6:
                        # create solid block and add it
                        self.blocks.add(self.blockfactory.getSolidBlock((x,y)))


# create a game and run it
if __name__ == '__main__':
    game = Game()
    game.run()