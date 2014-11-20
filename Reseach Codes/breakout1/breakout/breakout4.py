#!/usr/bin/env python

"""
Pygame Tutorial 4
Breakout: Step 4 - Make it a Game

Written by Collin "Keeyai" Green

Version 1.0.0 - 2010-12-31
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
        self.rect.center = 260, 550


class Ball(pygame.sprite.Sprite):
    """A ball sprite. Subclasses the pygame sprite class."""

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        # set the image and rect for rendering
        self.image = pygame.image.load(os.path.join('images','ball.gif'))
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = xy

        # keep track of some info about the ball
        self.maxspeed = 10
        self.servespeed = 5
        self.damage = 1

        # the ball velocity
        self.velx = 0
        self.vely = 0

    def move(self, dx, dy):
        """Move the ball"""
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        """Called to update the sprite. Do this every frame. Handles
        moving the sprite by its velocity. Caps the speed as necessary."""
        speed = math.hypot(self.velx, self.vely)
        # if going faster than max speed
        if speed > self.maxspeed:
            speed = self.maxspeed                       # cap speed
            angle = math.atan2(self.vely, self.velx)    # get angle
            self.velx = math.cos(angle) * speed         # x component at new speed
            self.vely = math.sin(angle) * speed         # y component at new speed

        # move the ball
        self.move(self.velx, self.vely)

    def reset(self):
        """Put the ball back in the middle and stop it from moving"""
        self.rect.centerx = 260
        self.rect.bottom = 549   # place just above the paddle so we dont collide
        self.velx = 0
        self.vely = 0

    def serve(self):
        angle = -90 + random.randint(-30, 30)

        # do the trig to get the x and y components
        x = math.cos(math.radians(angle))
        y = math.sin(math.radians(angle))

        self.velx = self.servespeed * x
        self.vely = self.servespeed * y


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

    def hit(self, damage=1):
        """Called when the block gets hit. Damage is the amount
        of levels to drop the block down from one hit -- perhaps for
        powerups or something later on.
        Returns a tuple (destroyed, points)
        destroyed is true if the block is destroyed, False otherwise
        points is the number of points gained by hitting the block"""
        # points earned for hitting the block
        points = 100 * self.level

        # decrement the block level
        self.level -= damage

        # check if destroyed
        if self.level <= 0:
            return True, points

        # not destroyed, set new image
        else:
            self.image = self.images[self.level]
            xy = self.rect.center               # save previous position
            self.rect = self.image.get_rect()   # reset rect in case shape changes
            self.rect.center = xy               # reset block to old position
            return False, points


class SolidBlock(pygame.sprite.Sprite):
    """A block that can't be destroyed"""
    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', 'block_gray.png'))
        self.rect = self.image.get_rect()

        # set position
        self.rect.center = xy

    def hit(self, damage):
        """Returns false, 0 since it cannot be destroyed"""
        return False, 0


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


class Score(pygame.sprite.Sprite):
    """A sprite for the score."""

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy    # save xy -- will center our rect on it when we change the score
        self.font = pygame.font.Font(None, 50)  # load the default font, size 50
        self.color = (255, 165, 0)         # our font color in rgb
        self.score = 0  # start at zero
        self.reRender() # generate the image

    def update(self):
        pass

    def add(self, points):
        """Adds the given number of points to the score."""
        self.score += points
        self.reRender()

    def reset(self):
        """Resets the scores to zero."""
        self.score = 0
        self.reRender()

    def reRender(self):
        """Updates the score. Renders a new image and re-centers at the initial coordinates."""
        self.image = self.font.render("%d"%(self.score), True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.xy


class Lives(pygame.sprite.Sprite):
    """An object to represent the player's remaining lives."""
    def __init__(self, xy, startinglives=3):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy        # our rendering position
        self.ballimage = pygame.image.load(os.path.join('images','ball.gif'))  # path to the ball image
        self.setLives(startinglives)        # sets lives and generates the lives image

    def getLives(self):
        return self.lives

    def setLives(self, lives):
        self.lives = lives
        self.generateLivesImage()

    def generateLivesImage(self):
        """Generates a new image for this sprite by repeating the ball image
        for each life the player still has."""
        # get a new surface that is the width of the ball image * the lives
        ballrect = self.ballimage.get_rect()
        padding = 5
        newwidth = (ballrect.width + padding) * self.lives

        # create the surface
        surface = pygame.Surface( (newwidth, ballrect.height) )
        surface.set_colorkey((0,0,0))   # set the color key to black so we
                                        # have a transparent background

        # draw the ball on it repeatedly
        for l in range(self.lives):
            surface.blit(self.ballimage, ((ballrect.width + padding) * l, 0))

        # set as image and rect so it can be rendered
        self.image = surface
        self.rect = surface.get_rect()

        # move rect to the proper location
        self.rect.left, self.rect.centery = self.xy


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

        # create ball
        self.ball = Ball((0,0))
        self.ball.reset()
        self.sprites.add(self.ball)

        # create sprite group for blocks
        self.blocks = pygame.sprite.RenderUpdates()

        # create our blockfactory object
        self.blockfactory = BlockFactory()

        # load the first level
        self.currentlevel = 1
        self.loadLevel(self.currentlevel)

        # track the state of the game
        self.isReset = True
        self.playing = True

        # create our score object
        self.score = Score((75, 575))
        self.sprites.add(self.score)

        # create our lives object
        self.lives = Lives((450, 575), 3)
        self.sprites.add(self.lives)

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

            # if we haven't lost yet
            if self.playing:

                # update our sprites
                for sprite in self.sprites:
                    sprite.update()

                # handle ball -- all our ball management here
                self.manageBall()

                # manageCollisions
                self.manageCollisions()

                # check if we beat the level
                if len(self.blocks) == 0:
                    self.newLevel()

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
                    if self.isReset:
                        self.ball.serve()
                        self.isReset = False

            elif event.type == KEYUP:
                # paddle control
                if event.key == K_a or event.key == K_LEFT:
                    self.paddle.right()
                if event.key == K_d or event.key == K_RIGHT:
                    self.paddle.left()
        return True

    def manageBall(self):
        """This basically runs the game. Moves the ball and handles
        wall and paddle collisions."""

        # if isReset is true, we are waiting to serve the ball so keep it on the paddle
        if self.isReset:
            self.ball.rect.centerx = self.paddle.rect.centerx
            return

        # if ball isn't below the walls
        if self.ball.rect.top < 550:
            # bounce ball off the ceiling
            if self.ball.rect.top <= 10:
                self.ball.rect.top = 11

                # reverse y velocity so it 'bounces'
                self.ball.vely *= -1

            # bounce ball off the left wall
            if self.ball.rect.left <= 10:
                self.ball.rect.left = 11

                # reverse X velocity so it 'bounces'
                self.ball.velx *= -1

            # bounce ball off the right wall
            elif self.ball.rect.right > 510:
                self.ball.rect.right = 509

                # reverse X velocity so it 'bounces'
                self.ball.velx *= -1

        # ball IS below the walls
        else:
            # if ball hits the bottom, reset the board
            if self.ball.rect.bottom > 600:
                self.reset()

    def manageCollisions(self):
        """Called every frame. Manages collisions between the ball and
        the paddle and the ball and the blocks"""
        # lets do the paddle and the ball first
        if pygame.sprite.collide_rect(self.ball, self.paddle):
            # need to get WHERE on the paddle the ball hit so we can apply
            # the proper rebound
            self.collisionHelper(self.ball, self.paddle)

        # ball and blocks
        collisions = pygame.sprite.spritecollide(self.ball, self.blocks, dokill=False)

        # if we hit two blocks at once we need to bounce differently
        if len(collisions) >= 2:    # going to just take the first 2
            # if between them horizontally, bounce like a flat horizontal wall
            if collisions[0].rect.y == collisions[1].rect.y:
                self.ball.vely *= -1            # bounce in y direction
                self.ball.rect.top = collisions[0].rect.bottom + 1  # move out of collision

            # if between them vertically, bounce like a flat vertical wall
            else:
                # we were moving right
                if self.ball.velx > 0:
                    self.ball.rect.right = collisions[0].rect.left - 1  # move out of collision
                # we were moving left
                else:
                    self.ball.rect.left = collisions[0].rect.right + 1  # move out of collision
                # bounce x direction
                self.ball.velx *= -1

            # apply damage to blocks
            for block in collisions:
                destroyed, points = block.hit(self.ball.damage)
                self.score.add(points)      # add the points to the score
                if destroyed:
                    self.blocks.remove(block)

        # if we hit one block, use the collisionHelper function
        if len(collisions) == 1:
            item = collisions[0]
            self.collisionHelper(self.ball, item)
            # collided with a block, call the block hit method
            if hasattr(item, 'hit'):
                destroyed, points = item.hit(self.ball.damage)
                self.score.add(points)      # add the points to the score
                # remove from render group if block is destroyed
                if destroyed:
                    self.blocks.remove(item)

    def collisionHelper(self, ball, item):
        """Function that takes the ball and an item it collides with
        and sets the new ball velocity and position based on how the
        two collided. Does a fairly cheap but also fairly inaccurate
        guess on how the ball collided with the object:)"""

        # going to simulate actual collision code my checking if the ball is in
        # certain areas of the block/paddle
        cornerwidth = 5

        # if the item is the paddle, apply some of its velocity to the ball
        if hasattr(item, 'velocity'):
            self.ball.velx += item.velocity/3.0

        # test corners first
        # if the ball hit the top left
        if self.ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.top, cornerwidth, cornerwidth) ):
            speed = math.hypot(self.ball.velx, self.ball.vely)
            component = speed * .7071 # sqrt2 estimate -- x and y component of 45 degrees
            if self.ball.velx >= 0: # only change x velocity if going right
                self.ball.velx = -component
            if self.ball.vely >= 0: # only change y velocity if going down
                self.ball.vely = -component
            self.ball.rect.bottom = item.rect.top -1    # move out of collision
            return

        # if the ball hit the top right
        if self.ball.rect.colliderect( pygame.Rect(item.rect.right, item.rect.top, cornerwidth, cornerwidth) ):
            speed = math.hypot(self.ball.velx, self.ball.vely)
            component = speed * .7071 # sqrt2 estimate -- x and y component of 45 degrees
            if self.ball.velx <= 0: # only change x velocity if going left
                self.ball.velx = component
            if self.ball.vely >= 0: # only change y velocity if going down
                self.ball.vely = -component
            self.ball.rect.bottom = item.rect.top -1    # move out of collision
            return

        # if the ball hit the bottom left
        if self.ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.bottom-cornerwidth, cornerwidth, cornerwidth) ):
            speed = math.hypot(self.ball.velx, self.ball.vely)
            component = speed * .7071 # sqrt2 estimate -- x and y component of 45 degrees
            if self.ball.velx >= 0: # only change x velocity if going right
                self.ball.velx = -component
            if self.ball.vely <= 0: # only change y velocity if going up
                self.ball.vely = component
            self.ball.rect.top  = item.rect.bottom + 1  # move out of collision
            return

        # if the ball hit the bottom right
        if self.ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.bottom-cornerwidth, cornerwidth, cornerwidth) ):
            speed = math.hypot(self.ball.velx, self.ball.vely)
            component = speed * .7071 # sqrt2 estimate -- x and y component of 45 degrees
            if self.ball.velx <= 0: # only change x velocity if going left
                self.ball.velx = component
            if self.ball.vely <= 0: # only change y velocity if going up
                self.ball.vely = component
            self.ball.rect.top = item.rect.bottom + 1   # move out of collision
            return

        # didnt hit the corners, let's try the sides
        # if the ball hit the top edge
        if self.ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.top, item.rect.width, 2) ):
            self.ball.vely *= -1                        # flip y velocity
            self.ball.rect.bottom = item.rect.top - 1   # move out of collision
            return

        # if the ball hit the bottom edge
        elif self.ball.rect.colliderect( pygame.Rect(item.rect.left, item.rect.bottom-2, item.rect.width, 2) ):
            self.ball.vely *= -1                        # flip y velocity
            self.ball.rect.top = item.rect.bottom + 1   # move out of collision
            return

        # if the ball hit the left side
        if self.ball.rect.collidepoint((item.rect.left, item.rect.centery)):
            self.ball.velx *= -1                        # flip x velocity
            self.ball.rect.right = item.rect.left - 1   # move out of collision
            return

        # if the ball hit the right side
        elif self.ball.rect.collidepoint((item.rect.right, item.rect.centery)):
            self.ball.velx *= -1                        # flip x velocity
            self.ball.rect.left = item.rect.right + 1   # move out of collision
            return

    def newLevel(self):
        """Called when the user completes the level. Loads the next level
        if possible and resets the paddle and ball. If no more levels are
        available, shows the win message."""
        self.currentlevel += 1
        # if there is a file for the next level, load it
        if os.path.isfile(os.path.join('levels', 'level%d.level'%self.currentlevel)):
            self.loadLevel(self.currentlevel)
            self.paddle.reset()
            self.ball.reset()
            self.isReset = True

        # no file, show win message
        else:
            # game over! render a game over message and stop the game
            font = pygame.font.Font(None, 50)  # load the default font, size 50
            endmessage = font.render("You Win!", True, (255,150,80))
            endmessagerect  = endmessage.get_rect()
            endmessagerect.center = (260, 250)

            # blit it on the background and flip (render) the display one last time
            self.window.blit(endmessage, endmessagerect)
            pygame.display.flip()

            # turn off all the gameplay
            self.playing = False

    def reset(self):
        """Called when the ball hits the bottom wall. The player loses
        a life and the ball is placed on the paddle, ready to be served."""

        # handle the lives
        lives = self.lives.getLives()
        # if we have lives to spare
        if lives > 0:
            self.lives.setLives(lives-1)
            self.paddle.reset()
            self.ball.reset()
            self.isReset = True
        else:
            # game over! render a game over message and stop the game
            font = pygame.font.Font(None, 50)  # load the default font, size 50
            endmessage = font.render("Game Over!", True, (255,100,50))
            endmessagerect  = endmessage.get_rect()
            endmessagerect.center = (260, 250)

            font = pygame.font.Font(None, 40)  # load the default font, size 40
            endmessage2 = font.render("Press Escape to Quit", True, (255,100,50))
            endmessagerect2  = endmessage2.get_rect()
            endmessagerect2.center = (260, endmessagerect.bottom + 20)

            # blit it on the background and flip (render) the display one last time
            self.window.blit(endmessage, endmessagerect)
            self.window.blit(endmessage2, endmessagerect2)
            pygame.display.flip()

            # turn off all the gameplay
            self.playing = False

    def parseLevelFile(self, filepath):
        """Parses a level file and returns a 2D array representing it.
        If it fails to find the level it returns a default level"""
        defaultlevel = [
            [0, 1, 1, 2, 1, 1, 2, 1, 1, 0],
            [0, 0, 2, 3, 4, 4, 3, 2, 0, 0],
            [0, 0, 0, 4, 5, 5, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]

        # verify the file exists
        if os.path.isfile(filepath):
            # open it for reading
            f = open(filepath, 'r')
            # read all the lines from it into an array
            rows = f.readlines()

            level = []
            # for all the rows in the array we read from the file
            for r in rows:
                # strip any /n from the row, then split on spaces so we get
                # an array of our block levels
                blocks = r.strip().split(' ')
                newrow = []
                # convert our strings to integers and place in the row
                for b in blocks:
                    newrow.append(int(b))
                level.append(newrow)

            # return the level
            return level

        else:
            return defaultlevel

    def loadLevel(self, levelnumber):
        """Loads a level. Places blocks on the board and adds them to the
        blocks render group"""
        # parse the desired level file
        level = self.parseLevelFile( os.path.join('levels', 'level%d.level' % levelnumber))

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