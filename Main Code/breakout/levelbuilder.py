#!/usr/bin/env python

"""
Pygame Tutorial 4
Breakout: Step 3 - The Level Editor

Written by Collin "Keeyai" Green
Version 1.0.0 - 2010-12-31
"""

try:
    import sys, os
    import pygame
    from pygame.locals import *

except ImportError, err:
    print "%s Failed to Load Module: %s" % (__file__, err)
    sys.exit(1)

class Block(pygame.sprite.Sprite):
    """A block sprite. Has a level and a position."""
    def __init__(self, xy, images, level=1):
        pygame.sprite.Sprite.__init__(self)

        # save images and level
        self.images = images
        self.level = level

        # create initial rect
        self.rect = pygame.Rect(xy[0]-25, xy[1]-10, 50, 20) # left, top, width, height

        # set image and rect so we can be rendered
        self.resetImage()

    def up(self):
        self.level += 1
        self.resetImage()

    def down(self):
        self.level -= 1
        self.resetImage()

    def resetImage(self):
        if self.level in self.images:
            self.image = self.images[self.level]
            xy = self.rect.center               # save previous position
            self.rect = self.image.get_rect()   # reset rect in case shape changes
            self.rect.center = xy               # reset block to old position


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
            5: pygame.image.load(os.path.join('images','block_purple.png')),
            6: pygame.image.load(os.path.join('images','block_gray.png'))
        }

    def getBlock(self, xy, level=1):
        return Block(xy, self.images, level)


class Button(pygame.sprite.Sprite):
    """An extremely simple button sprite."""
    def __init__(self, xy, text):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy
        self.font = pygame.font.Font(None, 25)  # load the default font, size 25
        self.color = (0, 0, 0)         # our font color in rgb
        self.text = text
        self.generateImage() # generate the image

    def generateImage(self):
        # draw text with a solid background - about as simple as we can get
        self.image = self.font.render(self.text, True, self.color, (200,200,200))
        self.rect = self.image.get_rect()
        self.rect.center = self.xy


class TextSprite(pygame.sprite.Sprite):
    """An extremely simple text sprite."""

    def __init__(self, xy, text=''):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy    # save xy -- will center our rect on it when we change the text
        self.font = pygame.font.Font(None, 25)  # load the default font, size 25
        self.color = (255, 165, 0)         # our font color in rgb
        self.text = text
        self.generateImage() # generate the image

    def setText(self, text):
        self.text = text
        self.generateImage()

    def generateImage(self):
        """Updates the text. Renders a new image and re-centers at the initial coordinates."""
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.xy


class LevelBuilder(object):
    """Our level builder object! Initializes everything."""

    def __init__(self):
        """Initializes pygame and sets up our pygame window
        and other pygame tools."""

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
        pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])

        # make background
        self.background = pygame.image.load(os.path.join('images','background.jpg'))
        # blit the background onto the window
        self.window.blit(self.background, (0,0))
        # flip the display so the background is on there
        pygame.display.flip()

        # create sprite group for blocks
        self.blocks = pygame.sprite.RenderUpdates()

        # create sprite group for everything else
        self.sprites = pygame.sprite.RenderUpdates()

        # create our blockfactory object
        self.blockfactory = BlockFactory()

        # create a blank level
        self.resetLevel()

        # Save button sprite
        self.savebutton = Button((260,450), 'Save')
        self.sprites.add(self.savebutton)

        # feedback sprite
        self.feedback = TextSprite((260, 550),  '')
        self.sprites.add(self.feedback)

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

            # render blocks
            self.blocks.clear(self.window, self.background)
            dirty = self.blocks.draw(self.window)

            # render everything else
            self.sprites.clear(self.window, self.background)
            dirty += self.sprites.draw(self.window)

            # draw a grid on our background
            self.drawGrid()

            # blit the dirty areas of the screen
            pygame.display.update(dirty)                        # updates just the 'dirty' areas

        print 'Quitting. Thanks for playing'

    def resetLevel(self):
        # empty our sprite group
        self.blocks.empty()

        # create our level object -- 2D array of blocks with level 0
        self.level = []
        for y in range(5):
            row = []
            for x in range(10):
                pos = (35+(x*50), 20+(y*20))    # calculate the position for the block
                block = self.blockfactory.getBlock(pos, 0)  # create the block
                row.append(block)               # add the block to the row
            self.level.append(row)              # add the row to the array

    def drawGrid(self):
        # draw lines on the background where blocks can go
        linecolor = (255,255,255)
        for col in range(11):   # 11 so we get both sides of all the columns
            # surface, color, start, end
            pygame.draw.line(self.window, linecolor, (10+(col*50),10), ((10+col*50),110))

            for row in range(6):    # 6 so we get both sides of all the rows
                pygame.draw.line(self.window, linecolor, (10, 10+(row*20)), (510, 10+(row*20)))
        # render the display
        pygame.display.flip()

    def handleEvents(self):
        """Poll for PyGame events and behave accordingly. Return false to stop
        the event loop and end the level builder."""

        # poll for pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            # handle user input
            elif event.type == KEYDOWN:

                # if the user presses escape, quit the event loop.
                if event.key == K_ESCAPE:
                    return False

                # ctrl-s saves the level
                elif event.key == K_s and event.mod & KMOD_CTRL:
                    self.save()

            # handle mouse clicks in self.mouseDown
            elif event.type == MOUSEBUTTONDOWN:
                self.mouseDown(event.pos, event.button)

        return True

    def mouseDown(self, position, button):
        """Handles all the mouse clicks. We want left clicks
        to add to a block or create one and right clicks to take away."""
        posx, posy = position

        # check if the save button was clicked
        if self.savebutton.rect.collidepoint( position):
            self.save()
            return

        # otherwise, only care about clicks in the level area
        if posx < 10 or posx >= 510 or posy < 0 or posy >= 110:
            return

        # convert mouse position to block coordinate
        x = int((posx-10) / 50)     # subtract 10 for the wall and divide by block width
        y = int((posy-10) / 20)     # subtract 10 for the wall and divide by block height

        # get the block we are on
        block = self.level[y][x]    # notice y then x because our level is rows then cols

        # Left click
        if button == 1:
            # if the block in this space is level 0, increment and add for render
            if block.level == 0:

                # increment block level
                block.up()

                # add to rendering group so it gets displayed
                self.blocks.add(block)

            # on a block with level less than 6
            elif block.level < 6:
                # increment block level
                block.up()

            # on a block with level > 6
            else:
                # loop back to an empty block
                block.level = 0

                # remove from rendering group
                self.blocks.remove(block)

        # right click
        elif button == 3:
            # if the block in this space is greater than 1
            if block.level > 1:
                # decrement block level
                block.down()

            # on a block with level < 1
            else:
                # change back to an empty block
                block.level = 0

                # remove from rendering group
                self.blocks.remove(block)

    def save(self):
        self.feedback.setText('Saving...')

        # generate unique level name
        count = 1
        name = 'level%d.level'%count
        while os.path.isfile( os.path.join('levels', name) ):
            count += 1
            name = 'level%d.level'%count

        # create file
        f = open(os.path.join('levels',name), 'w')

        # generate contents from self.level
        for row in self.level:
            for col in row:
                f.write('%d ' % col.level)    # write block level
            f.write('\n')   # write new line

        # close file handle
        f.close()

        # show level name in feedback
        self.feedback.setText('Saved level to levels/%s' % name)
        print 'Saved levels/%s' % name

        # reset level
        self.resetLevel()


if __name__ == '__main__':
    lb = LevelBuilder()
    lb.run()
