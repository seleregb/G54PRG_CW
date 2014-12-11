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
        self.pimage = pygame.image.load("bat.png").convert()


        # get new rect
        self.paddlerect = self.pimage.get_rect()

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
            self.image = pygame.image.load("powerup_paddle.png").convert()
        elif type == 'slowball':
            self.countdown = 60 * 10
            self.image = pygame.image.load("powerup_ball.png").convert()
        elif type == 'laser':
            self.image = pygame.image.load("powerup_laser.png").convert()
        else:
            self.image = pygame.image.load("powerup_lightning.png").convert()



        # set image and rect so we can be rendered
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

        # track the state of the game
        #self.isReset = True
        self.playing = True


        # a sprite rendering group for our ball and paddle
        self.sprites = pygame.sprite.RenderUpdates()

        # variables for powerups
        self.currentpowerup = None
        self.powerupdrop = 60 * 10



        # Initialise ready for game loop
        self.paddle.paddlerect = self.paddle.paddlerect.move((self.width / 2) - (self.paddle.paddlerect.right / 2), self.height - 20)
        self.ball.ballrect = self.ball.ballrect.move(self.width / 2, self.height / 2)
        self.xspeed = self.xspeed_init
        self.yspeed = self.yspeed_init
        self.lives = self.max_lives
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(1,30) 

        pygame.key.set_repeat(1,30)
        pygame.mouse.set_visible(0)  # turn off mouse pointer



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

            self.managePowerups()
            # render our sprites
            # clears the window where the sprites currently are, using the background
            dirty = self.sprites.draw(self.window)

            pygame.display.update(dirty)
            # update our sprites
            for sprite in self.sprites:
                alive = sprite.update()
                if alive is False:
                    self.sprites.remove(sprite)



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


    def managePowerups(self):
        """Called each frame. Drops new powerups as necessary. Checks if the
        paddle hits a powerup and applies the powerup. Manages the powerups
        timing out."""
        # no powerup, update countdown and drop one if necessary


        if self.currentpowerup is None:
            # decrement powerup drop countdown
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


        # if powerup hasn't been collected yet, check for collision
        elif not self.currentpowerup.collected:
            # collision, ie: the player collected the powerup
            if self.paddle.paddlerect.colliderect(self.currentpowerup.rect):
                # apply the powerup
                if self.currentpowerup.type == 'bigpaddle':
                    # increase paddle size
                    self.paddle.grow()

                elif self.currentpowerup.type == '1up':
                    # increment player lives
                    self.lives += 1

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
                # set current to none
                self.currentpowerup = None


                # set new powerupdrop countdown
                self.powerupdrop = random.randint(60 * 30, 60 * 60)


# create a game and run it
if __name__ == '__main__':
    game = Game()
    game.run()
