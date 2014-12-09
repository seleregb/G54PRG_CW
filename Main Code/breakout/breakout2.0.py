#!/usr/bin/env python



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
        self.image = pygame.image.load("bat.png").convert()
        #self.image = pygame.transform.rotate(self.image, 90)
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
        """Moves the paddle to the center of the board"""
        self.rect.center = 260, 550

    def grow(self):
        """Increases the size of the paddle."""
        # get current position
        xy = self.rect.center

        # set image and rect
        self.image = pygame.image.load("bat.png").convert()
        self.image = pygame.transform.rotate(self.image, 90)

        # double image size
        self.image = pygame.transform.scale2x(self.image)

        # get new rect
        self.rect = self.image.get_rect()

        # reset position
        self.rect.centerx, self.rect.centery = xy

        # if paddle is now over a wall, fix it
        if self.rect.right > 510:
            self.rect.right = 509
        elif self.rect.left < 10:
            self.rect.left = 11

    def shrink(self):
        """Returns the size of the paddle to normal"""
        # get current position
        xy = self.rect.center

        # set image and rect
        self.image = pygame.image.load("bat.png").convert()
        #self.image = pygame.transform.rotate(self.image, 90)

        # get new rect
        self.rect = self.image.get_rect()

        # reset position
        self.rect.centerx, self.rect.centery = xy

        # if paddle is now over a wall, fix it
        if self.rect.right > 510:
            self.rect.right = 509
        elif self.rect.left < 10:
            self.rect.left = 11


class Ball(pygame.sprite.Sprite):
    """A ball sprite. Subclasses the pygame sprite class."""

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        # set the image and rect for rendering
        self.image = pygame.image.load("ball.png").convert()
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

    def slowDown(self):
        """Called for the slowball powerup"""
        self.maxspeed = 5

    def speedUp(self):
        """Called for the slowball powerup"""
        self.maxspeed = 10


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

        points = 0
        while damage > 0 and self.level > 0:
            # points earned for hitting the block
            points += 100 * self.level

            # decrement the block level
            self.level -= damage

            # decrement the damage remaining to apply
            damage -= 1

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
        self.image = pygame.image.load("brick.png").convert()
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
            1: pygame.image.load("brick.png").convert(),
            2: pygame.image.load("brick.png").convert(),
            3: pygame.image.load("brick.png").convert(),
            4: pygame.image.load("brick.png").convert(),
            5: pygame.image.load("brick.png").convert()
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
        self.ballimage = pygame.image.load("ball.png").convert()  # path to the ball image
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
        self.rect.centerx, self.rect.centery = self.xy


class Powerup(pygame.sprite.Sprite):
    """A powerup."""
    def __init__(self, type='bigpaddle'):
        pygame.sprite.Sprite.__init__(self)

        # some variables we need
        self.type = type            # which powerup is it
        self.collected = False      # has it been collected yet?
        self.countdown = 1          # duration of the effect

        # set individual countdowns for the powerups with actual durations
        if type == 'bigpaddle':
            self.countdown = 60 * 25
        elif type == 'slowball':
            self.countdown = 60 * 10

        self.imagepaths = {
            'bigpaddle': os.path.join('images', 'powerup_paddle.png'),
            'laser': os.path.join('images', 'powerup_laser.png'),
            '1up': os.path.join('images', 'powerup_lightning.png'),
            'slowball': os.path.join('images', 'powerup_ball.png'),
        }

        # set image and rect so we can be rendered
        self.image = pygame.image.load(self.imagepaths[type])
        self.rect = self.image.get_rect()

        # set initial position somewhere near the top but below the blocks
        self.rect.center = random.randint(20, 500), 125

    def update(self):
        """Called every frame. Move the powerup down a bit so it 'falls' down
        the screen. Return false if below the screen because the player
        missed it."""
        self.rect.y += 2
        if self.rect.y > 600:
            return False
        return True


class Laser(pygame.sprite.Sprite):
    """A laser sprite for use with the laser powerup."""
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)

        # create an image
        image = pygame.Surface((50, 550))
        image.fill( (255,0,0) )      # fill it with red
        pygame.draw.rect(image, (255,255,0), pygame.Rect(10,0,30,550))   # yellow rect
        pygame.draw.rect(image, (0,255,250), pygame.Rect(20,0,10,550))   # cyan rect

        # set image and rect so we can be rendered
        self.image = image
        self.rect = self.image.get_rect()

        # set initial position somewhere near the top but below the blocks
        self.rect.centerx = x
        self.rect.bottom = 550

    def update(self):
        """Called every frame. Moves the laser up and off the screen. Returns
        false when the laser is completely gone and can be deleted."""
        self.rect.y -= 20
        if self.rect.bottom < 0:
            return False
        return True


class NameSprite(pygame.sprite.Sprite):
    """A sprite for the play to enter their name"""

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.xy = xy
        self.text = ''
        self.color = (255, 0, 0)
        self.font = pygame.font.Font(None, 35)  # load the default font, size 35
        self.reRender() # generate the image

    def addLetter(self, letter):
        """Adds the given letter"""
        self.text += str(letter)
        self.reRender()

    def removeLetter(self):
        if len(self.text) == 1:
            self.text = ''
        else:
            self.text = self.text[:-1]
        self.reRender()

    def reRender(self):
        """Updates the text."""
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.xy


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
        self.background = pygame.image.load("background.jpg").convert()
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
        self.enteringname = False

        # create our score object
        self.score = Score((75, 575))
        self.sprites.add(self.score)

        # create our lives object
        self.lives = Lives((450, 575), 3)
        self.sprites.add(self.lives)

        # variables for powerups
        self.currentpowerup = None
        self.powerupdrop = 60 * 10

        # sprite group for name block
        self.namesprites = pygame.sprite.RenderUpdates()

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
                    alive = sprite.update()
                    if alive is False:
                        self.sprites.remove(sprite)

                # handle ball -- all our ball management here
                self.manageBall()

                # manageCollisions
                self.manageCollisions()

                # check if we beat the level
                if len(self.blocks) == 0:
                    self.newLevel()

                # manage powerups
                self.managePowerups()

                # render our sprites
                self.sprites.clear(self.window, self.background)    # clears the window where the sprites currently are, using the background
                dirty = self.sprites.draw(self.window)              # calculates the 'dirty' rectangles that need to be redrawn

                # render blocks
                self.blocks.clear(self.window, self.background)
                dirty += self.blocks.draw(self.window)

                # blit the dirty areas of the screen
                pygame.display.update(dirty)                        # updates just the 'dirty' areas

            # entering name, render name sprite
            elif self.enteringname:
                font = pygame.font.Font(None, 35)  # load the default font, size 50
                color = (255, 50, 0)
                nameimage = font.render('Enter Name:', True, color)
                namerect = nameimage.get_rect()
                namerect.center = 260, 250
                self.window.blit(nameimage,namerect)

                self.namesprites.clear(self.window, self.background)
                dirty = self.namesprites.draw(self.window)
                pygame.display.update(dirty+[namerect])
                #pygame.display.flip()

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

                # if entering name, save keys
                if self.enteringname:

                    # if backspace, remove last letter until empty string
                    if event.key == K_BACKSPACE:
                        self.namesprite.removeLetter()

                    # if enter, self.nameEntered with name
                    elif event.key == K_RETURN:
                        self.nameEntered()

                    else:
                        try:
                            char = chr(event.key)
                            # all the characters we want to allow
                            if str(char) in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_':
                                self.namesprite.addLetter(char)
                        except:
                            pass    # exception from not being able to get char, dont care

                # not entering name
                else:
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

            elif event.type == KEYUP and not self.enteringname:
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

    def managePowerups(self):
        """Called each frame. Drops new powerups as necessary. Checks if the
        paddle hits a powerup and applies the powerup. Manages the powerups
        timing out."""
        # no powerup, update countdown and drop one if necessary
        if self.currentpowerup is None:
            # decrement powerup drop countdown
            if not self.isReset:    # dont continue countddown if waiting to serve
                self.powerupdrop -= 1

                # drop a powerup if time
                if self.powerupdrop <= 0:

                    # drop chances to use with random
                    droppercentages = [
                    (10, '1up'),        # 10% chance
                    (30, 'laser'),      # 20% chance
                    (55, 'slowball'),   # 25% chance
                    (100, 'bigpaddle')  # 45% chance
                    ]

                    # decide which powerup to drop
                    choice = random.uniform(0,100)
                    for chance, type in droppercentages:
                        if choice <= chance:
                            # create new powerup and add it to render group
                            self.currentpowerup = Powerup(type)
                            self.sprites.add(self.currentpowerup)
                            break
            return

        # if powerup hasn't been collected yet, check for collision
        if not self.currentpowerup.collected:
            # collision, ie: the player collected the powerup
            if self.paddle.rect.colliderect(self.currentpowerup.rect):
                # apply the powerup
                if self.currentpowerup.type == 'bigpaddle':
                    # increase paddle size
                    self.paddle.grow()
                elif self.currentpowerup.type == 'laser':
                    # create laser sprite for rendering
                    laser = Laser(self.paddle.rect.centerx)
                    self.sprites.add(laser)

                    # destroy all blocks it touches
                    touchedblocks = pygame.sprite.spritecollide(laser, self.blocks, False)
                    for b in touchedblocks:
                        # add score for those blocks
                        alive,points = b.hit(1000)
                        self.score.add(points)

                        # remove blocks from render group
                        self.blocks.remove(b)

                elif self.currentpowerup.type == '1up':
                    # increment player lives
                    self.lives.setLives( self.lives.getLives() + 1)

                elif self.currentpowerup.type == 'slowball':
                    # decrease ball max speed
                    self.ball.slowDown()

                # set collected so timer starts
                self.currentpowerup.collected = True
                self.sprites.remove(self.currentpowerup)

            # not colliding - keep moving and check if we missed it
            else:
                # update powerup and delete if necessary
                alive = self.currentpowerup.update()
                if not alive:
                    self.sprites.remove(self.currentpowerup)
                    self.currentpowerup = None

                    # reset drop counter
                    self.powerupdrop = random.randint(60 * 10, 60 * 20)

        # if powerup is currently active, continue countdown
        elif self.currentpowerup.countdown > 0:
            # decrement countdown
            self.currentpowerup.countdown -= 1

        # powerup is over -- has been collected and countdown <= 0
        else:

            # if we haven't turned off the current powerup yet, do so
            if self.currentpowerup is not None:
                if self.currentpowerup.type == 'bigpaddle':
                    self.paddle.shrink()

                elif self.currentpowerup.type == 'slowball':
                    self.ball.speedUp()

                # set current to none
                self.currentpowerup = None

                # set new powerupdrop countdown
                self.powerupdrop = random.randint(60 * 30, 60 * 60)

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
            endmessagerect.center = (260, 135)

            # blit it on the background and flip (render) the display one last time
            self.window.blit(endmessage, endmessagerect)
            pygame.display.flip()

            # turn off all the gameplay
            self.playing = False

            # handle showing and inputing high scores
            self.handleHighScores()

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
            endmessagerect.center = (260, 135)

            # blit it on the background and flip (render) the display one last time
            self.window.blit(endmessage, endmessagerect)
            pygame.display.flip()

            # turn off all the gameplay
            self.playing = False

            # show high score table
            self.handleHighScores()

    def handleHighScores(self):
        """Called to prompt the user to enter a new
        high score name and show the high score table."""

        # load high scores
        highscores = self.parseHighScores()

        # if current score belongs on the table
        if self.score.score > int(highscores[-1][1]):
            # prompt for user name
            self.enteringname = True
            self.namesprite = NameSprite( (260, 310) )
            self.namesprites.add(self.namesprite)

        # otherwise just show table
        else:
            self.showHighScores(highscores)

    def nameEntered(self):
        self.enteringname = False
        username = self.namesprite.text

        # blit the background onto the window
        self.window.blit(self.background, (0,0))
        # flip the display so the background is on there
        pygame.display.flip()

        # load high scores
        highscores = self.parseHighScores()

        # insert the player's score into the highscore table
        newscores = []
        for name, score in highscores:
            if self.score.score > int(score):
                newscores.append((username, str(self.score.score)))
                self.score.score = 0    # set to 0 so we dont add it again
            newscores.append((name, score))
        newscores = newscores[0:10] # only take 10

        # write scores to high score table
        highscorefile = 'highscores.txt'
        f = open(highscorefile, 'w')
        for name, score in newscores:
            f.write("%s:%s\n" % (name, score))
        f.close()

        # display high scores
        self.showHighScores(newscores)

    def parseHighScores(self):
        """Parses the high score table and returns a
        list of scores and their owners"""
        highscorefile = 'highscores.txt'
        if os.path.isfile(highscorefile):
            # read the file into lines
            f = open(highscorefile, 'r')
            lines = f.readlines()
            # break lines into length 2 lists [name, score]
            scores = []
            for line in lines:
                scores.append( line.strip().split(':'))
            return scores
        else:
            # generate default highscore table
            f = open(highscorefile, 'w')
            f.write("""JJJ:10000
III:9000
HHH:8000
GGG:7000
FFF:6000
EEE:5000
DDD:4000
CCC:3000
BBB:2000
AAA:1000""")
            f.close()
            # call method again - will load the scores we just wrote this time
            return self.parseHighScores()

    def showHighScores(self, scores):
        """Draws the high score table onto the screen."""
        font = pygame.font.Font(None, 35)  # load the default font, size 50
        color = (255, 50, 0)

        for i in range(len(scores)):
            name, score = scores[i]
            # render name
            nameimage = font.render(name, True, color)
            namerect = nameimage.get_rect()
            namerect.left, namerect.y = 40, 100 + (i*(namerect.height + 20))
            self.window.blit(nameimage,namerect)

            # render score
            scoreimage = font.render(score, True, color)
            scorerect = scoreimage.get_rect()
            scorerect.right, scorerect.y = 480, namerect.y
            self.window.blit(scoreimage, scorerect)

            # draw dots from name until score
            for d in range(namerect.right + 25, scorerect.left-10, 25):
                pygame.draw.rect(self.window, color, pygame.Rect(d, scorerect.centery, 5, 5))

        # flip display
        pygame.display.flip()

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
