__author__ = 'khcx4oor'

##Game version 2.0

try:
    import sys, os, math, random
    import pygame
    from pygame.locals import *

except ImportError, err:
    print "%s Failed to Load Module: %s" % (__file__, err)
    sys.exit(1)

class Paddle():
    def __init__(self):
        # set image and rect
        self.pimage = pygame.image.load("bat.png").convert()
        self.paddlerect = self.pimage.get_rect()

    def grow(self):
        """Increases the size of the paddle."""
        # get current position
        xy = self.paddlerect.center

        # set image and rect
        self.pimage = pygame.image.load("bat.png")
        self.pimage = pygame.transform.rotate(self.pimage, 90)

        # double image size
        self.pimage = pygame.transform.scale2x(self.pimage)

        # get new rect
        self.paddlerect = self.pimage.get_rect()

        # reset position
        self.paddlerect.centerx, self.paddlerect.centery = xy

        # if paddle is now over a wall, fix it
        if self.paddlerect.right > 510:
            self.paddlerect.right = 509
        elif self.paddlerect.left < 10:
            self.paddlerect.left = 11

    def shrink(self):
        """Returns the size of the paddle to normal"""
        # get current position
        xy = self.paddlerect.center

        # set image and rect
        self.image = pygame.image.load("bat.png").convert()
        self.image = pygame.transform.rotate(self.image, 90)

        # get new rect
        self.paddlerect = self.image.get_rect()

        # reset position
        self.paddlerect.centerx, self.paddlerect.centery = xy

        # if paddle is now over a wall, fix it
        if self.paddlerect.right > 510:
            self.paddlerect.right = 509
        elif self.paddlerect.left < 10:
            self.paddlerect.left = 11


class Ball():
    def __init__(self):
        # set image and rect
        self.bimage = pygame.image.load("ball.png").convert()
        self.ballrect = self.bimage.get_rect()


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

class Game(object):
    """Our game object! This is a fairly simple object that handles the
    initialization of pygame and sets up our game to run."""

    def __init__(self):
        """Called when the the Game object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools
        that we will need for more complicated tutorials."""

        self.xspeed_init = 3
        self.yspeed_init = 3
        self.max_lives = 5
        self.paddle_speed = 30
        self.score = 0 
        self.bgcolour = 0x2F, 0x4F, 0x4F  # darkslategrey        
        self.size = self.width, self.height = 640, 480

        # load and set up pygame
        pygame.init()

        # create our window
        self.window = pygame.display.set_mode(self.size)

        self.paddle = Paddle()

        self.ball = Ball()

        # set the window title
        pygame.display.set_caption("Simple Breakout")

        self.pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
        self.pong.set_volume(10)

        self.wall = Wall()
        self.wall.build_wall(self.width)

        # Initialise ready for game loop
        self.paddle.paddlerect = self.paddle.paddlerect.move((self.width / 2) - (self.paddle.paddlerect.right / 2), self.height - 20)
        self.ball.ballrect = self.ball.ballrect.move(self.width / 2, self.height / 2)
        self.xspeed = self.xspeed_init
        self.yspeed = self.yspeed_init
        self.lives = self.max_lives
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(1,30) 

        pygame.key.set_repeat(1,30)
        pygame.mouse.set_visible(0)       # turn off mouse pointer

    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        print 'Starting Event Loop'

        while 1:

            # 60 frames per second
            self.clock.tick(60)

            # process key presses
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
        	            sys.exit()
                    if event.key == pygame.K_LEFT:                        
                        self.paddle.paddlerect = self.paddle.paddlerect.move(-self.paddle_speed, 0)
                        if (self.paddle.paddlerect.left < 0):
                           self.paddle.paddlerect.left = 0
                    if event.key == pygame.K_RIGHT:                    
                        self.paddle.paddlerect = self.paddle.paddlerect.move(self.paddle_speed, 0)
                        if (self.paddle.paddlerect.right > self.width):
                            self.paddle.paddlerect.right = self.width

            # check if bat has hit ball    
            if self.ball.ballrect.bottom >= self.paddle.paddlerect.top and \
               self.ball.ballrect.bottom <= self.paddle.paddlerect.bottom and \
               self.ball.ballrect.right >= self.paddle.paddlerect.left and \
               self.ball.ballrect.left <= self.paddle.paddlerect.right:
                self.yspeed = -self.yspeed                
                self.pong.play(0)                
                self.offset = self.ball.ballrect.center[0] - self.paddle.paddlerect.center[0]
                # offset > 0 means ball has hit RHS of bat                   
                # vary angle of ball depending on where ball hits bat                      
                if self.offset > 0:
                    if self.offset > 30:  
                        self.xspeed = 7
                    elif self.offset > 23:                 
                        self.xspeed = 6
                    elif self.offset > 17:
                        self.xspeed = 5 
                else:  
                    if self.offset < -30:                             
                        self.xspeed = -7
                    elif self.offset < -23:
                        self.xspeed = -6
                    elif self.xspeed < -17:
                        self.xspeed = -5     
                      
            # move bat/ball
            self.ball.ballrect = self.ball.ballrect.move(self.xspeed, self.yspeed)
            if self.ball.ballrect.left < 0 or self.ball.ballrect.right > self.width:
                self.xspeed = -self.xspeed                
                self.pong.play(0)            
            if self.ball.ballrect.top < 0:
                self.yspeed = -self.yspeed                
                self.pong.play(0)               

            # check if ball has gone past bat - lose a life
            if self.ball.ballrect.top > self.height:
                self.lives -= 1
                # start a new ball
                self.xspeed = self.xspeed_init
                self.rand = random.random()                
                if random.random() > 0.5:
                    self.xspeed = -self.xspeed 
                self.yspeed = self.yspeed_init            
                self.ball.ballrect.center = self.width * random.random(), self.height / 3
                if self.lives == 0:                    
                    self.msg = pygame.font.Font(None,70).render("Game Over", True, (0,255,255), self.bgcolour)
                    self.msgrect = self.msg.get_rect()
                    self.msgrect = self.msgrect.move(self.width / 2 - (self.msgrect.center[0]), self.height / 3)
                    self.window.blit(self.msg, self.msgrect)
                    pygame.display.flip()
                    # process key presses
                    #     - ESC to quit
                    #     - any other key to restart game
                    while 1:
                        restart = False
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                    	            sys.exit()
                                if not (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):                                    
                                    restart = True      
                        if restart:                   
                            self.window.fill(self.bgcolour)
                            self.wall.build_wall(self.width)
                            self.lives = self.max_lives
                            self.score = 0
                            break
            
            if self.xspeed < 0 and self.ball.ballrect.left < 0:
                self.xspeed = -self.xspeed                                
                self.pong.play(0)

            if self.xspeed > 0 and self.ball.ballrect.right > self.width:
                self.xspeed = -self.xspeed                               
                self.pong.play(0)
           
            # check if ball has hit wall
            # if yes yhen delete brick and change ball direction
            self.index = self.ball.ballrect.collidelist(self.wall.brickrect)
            if self.index != -1:
                if self.ball.ballrect.center[0] > self.wall.brickrect[self.index].right or \
                   self.ball.ballrect.center[0] < self.wall.brickrect[self.index].left:
                    self.xspeed = -self.xspeed
                else:
                    self.yspeed = -self.yspeed                
                self.pong.play(0)              
                self.wall.brickrect[self.index:self.index + 1] = []
                self.score += 10

            #Display the score points
            self.window.fill(self.bgcolour)
            self.scoretext = pygame.font.Font(None,40).render(str(self.score), True, (0,255,255), self.bgcolour)
            self.scoretextrect = self.scoretext.get_rect()
            self.scoretextrect = self.scoretextrect.move(self.width - self.scoretextrect.right, 0)
            self.window.blit(self.scoretext, self.scoretextrect)

            #Display the number of live left.
            self.livepos = 0
            for i in range(self.lives):
                self.hearts = pygame.image.load("ball.png").convert()
                self.hearts.set_colorkey((255, 255 , 255))
                self.heartsrect = self.hearts.get_rect()
                self.heartsrect = self.heartsrect.move(self.livepos,0)
                self.window.blit(self.hearts, self.heartsrect)
                self.livepos+=30

            #build wall
            for i in range(0, len(self.wall.brickrect)):
                self.window.blit(self.wall.image, self.wall.brickrect[i])

            # if wall completely gone then rebuild it
            if self.wall.brickrect == []:              
                self.wall.build_wall(self.width)
                self.xspeed = self.xspeed_init
                self.yspeed = self.yspeed_init                
                self.ball.ballrect.center = self.width / 2, self.height / 3
         
            self.window.blit(self.ball.bimage, self.ball.ballrect)
            self.window.blit(self.paddle.pimage, self.paddle.paddlerect)
            pygame.display.flip()



# create a game and run it
if __name__ == '__main__':
    game = Game()
    game.run()
