__author__ = 'khcx4oor'

##Game version 2.0

try:
    import sys, os, math, random
    import pygame
    from pygame.locals import *

except ImportError, err:
    print "%s Failed to Load Module: %s" % (__file__, err)
    sys.exit(1)

class Paddle(pygame.sprite.Sprite):
    def __init__(self, xy):
        # initialize the pygame sprite part
        pygame.sprite.Sprite.__init__(self)

        # set image and rect
        self.image = pygame.image.load("bat.png")
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()

    def move(self, dx):
        """Move the paddle in the x direction. Don't go past the sides"""
        if dx != 0:
            if self.rect.right + dx > 510:
                self.rect.right = 510
            elif self.rect.left + dx < 10:
                self.rect.left = 10
            else:
                self.rect.x += dx

    def grow(self):
        """Increases the size of the paddle."""
        # get current position
        xy = self.rect.center

        # set image and rect
        self.image = pygame.image.load("bat.png")
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
        self.image = pygame.image.load("bat.png")
        self.image = pygame.transform.rotate(self.image, 90)

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
    def __init__(self, xy):
        # initialize the pygame sprite part
        pygame.sprite.Sprite.__init__(self)

        # set image and rect
        self.image = pygame.image.load("ball.png")
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect = self.image.get_rect()

class Wall():
    def __init__(self):
        # set image and rect
        self.image = pygame.image.load("brick.png").convert()
        self.rect = self.image.get_rect()
        self.bricklength = self.rect.right - self.rect.left
        self.brickheight = self.rect.bottom - self.rect.top

    def build_wall(self, width):
        xpos = 0
        ypos = 60
        adj = 0
        self.brickrect = []
        for i in range (0, 52):
            if xpos > width:
                if adj == 0:
                    adj = self.bricklength / 2
                else:
                    adj = 0
                xpos = -adj
                ypos += self.brickheight

            self.brickrect.append(self.image.get_rect())
            self.brickrect[i] = self.brickrect[i].move(xpos, ypos)
            xpos = xpos + self.bricklength


class Powerups(pygame.sprite.Sprite):
    def __init__(self, xy):
        # initialize the pygame sprite part
        pygame.sprite.Sprite.__init__(self)


class Game(object):
    """Our game object! This is a fairly simple object that handles the
    initialization of pygame and sets up our game to run."""

    def __init__(self):
        """Called when the the Game object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools
        that we will need for more complicated tutorials."""

        # load and set up pygame
        pygame.init()

        self.size = width,height = 640,480

        # create our window
        self.window = pygame.display.set_mode(self.size)

        # clock for ticking
        self.clock = pygame.time.Clock()

        # set the window title
        pygame.display.set_caption("Simple Breakout")

        # tell pygame to only pay attention to certain events
        # we want to know if the user hits the X on the window, and we
        # want keys so we can close the window with the esc key
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        # make background
        self.background = pygame.image.load("background.jpg")
        # blit the background onto the window
        self.window.blit(self.background, (0,0))
        # flip the display so the background is on there
        pygame.display.flip()

        # a sprite rendering group for our ball and paddle
        self.sprites = pygame.sprite.RenderUpdates()

        # create our paddle and add to sprite group
        self.paddle = Paddle((260,550))
        self.sprites.add(self.paddle)

        self.pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
        self.pong.set_volume(10)

        self.wall = Wall()
        self.wall.build_wall(width)

        pygame.key.set_repeat(1,30)
        pygame.mouse.set_visible(0)       # turn off mouse pointer

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
            pygame.display.set_caption('Simple Breakout   %d fps' % self.clock.get_fps())

            # update our sprites
            for sprite in self.sprites:
                sprite.update()

            # render our sprites
            self.sprites.clear(self.window, self.background)    # clears the window where the sprites currently are, using the background


            for i in range(0, len(self.wall.brickrect)):
                self.window.blit(self.wall.image, self.wall.brickrect[i])



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


# create a game and run it
if __name__ == '__main__':
    game = Game()
    game.run()
