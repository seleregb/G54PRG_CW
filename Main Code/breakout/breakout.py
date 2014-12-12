
#   Breakout V 0.1 November 2014
#
#   Copyright (C) 2014 Lee How Kiat, SelereGB
#
#   web   : https://github.com/seleregb/G54PRG_CW
#   email : khcx4lha@nottingham.edu.my - Lee How Kiat
#         : khcxoor@nottingham.edu.my - SelereGB
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#    
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from tkFileDialog import askopenfilename
try: import cPickle as pickle
except ImportError: import pickle
from pygame.locals import *
import pygame, random, sys, ezmenu, levelbuilder


def main(screen):

    xspeed_init = 3
    yspeed_init = 3
    max_lives = 5
    bat_speed = 30
    score = 0
    bgcolour = 0x2F, 0x4F, 0x4F  # darkslategrey
    size = width, height = 640, 480
    gamelevel = 0


    pygame.init()
    screen = pygame.display.set_mode(size)
    #screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    bat = pygame.image.load("bat.png").convert()
    batrect = bat.get_rect()

    ball = pygame.image.load("ball.png").convert()
    ball.set_colorkey((255, 255, 255))
    ballrect = ball.get_rect()

    pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
    pong.set_volume(10)

    wall = Wall()
    wall.build_wall(width)

    # Initialise ready for game loop
    batrect = batrect.move((width / 2) - (batrect.right / 2), height - 20)
    ballrect = ballrect.move(width / 2, height / 2)
    xspeed = xspeed_init
    yspeed = yspeed_init
    lives = max_lives
    clock = pygame.time.Clock()
    pygame.key.set_repeat(1,30)
    pygame.mouse.set_visible(0)       # turn off mouse pointer

    '''
    gamemsg = pygame.font.Font(None,70).render(str("Level {}".format(gamelevel)), True, (0,255,255), bgcolour)
    gamemsgrect = gamemsg.get_rect()
    gamemsgrect = gamemsgrect.move(width / 2 - (gamemsgrect.center[0]), height / 3)
    screen.blit(gamemsg, gamemsgrect)
    pygame.display.flip()
    pygame.time.delay(1000)
    '''

    while 1: #Game loop

        # 60 frames per second
        clock.tick(60)

        # process key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
        	        sys.exit()
                if event.key == pygame.K_LEFT:
                    batrect = batrect.move(-bat_speed, 0)
                    if (batrect.left < 0):
                        batrect.left = 0
                if event.key == pygame.K_RIGHT:
                    batrect = batrect.move(bat_speed, 0)
                    if (batrect.right > width):
                        batrect.right = width

        # check if bat has hit ball
        if ballrect.bottom >= batrect.top and \
            ballrect.bottom <= batrect.bottom and \
            ballrect.right >= batrect.left and \
            ballrect.left <= batrect.right:
                yspeed = -yspeed
                pong.play(0)
                offset = ballrect.center[0] - batrect.center[0]
                # offset > 0 means ball has hit RHS of bat
                # vary angle of ball depending on where ball hits bat
                if offset > 0:
                    if offset > 30:
                        xspeed = 7
                    elif offset > 23:
                        xspeed = 6
                    elif offset > 17:
                        xspeed = 5
                else:
                    if offset < -30:
                        xspeed = -7
                    elif offset < -23:
                        xspeed = -6
                    elif xspeed < -17:
                        xspeed = -5

        # move bat/ball
        ballrect = ballrect.move(xspeed, yspeed)
        if ballrect.left < 0 or ballrect.right > width:
            xspeed = -xspeed
            pong.play(0)
        if ballrect.top < 0:
            yspeed = -yspeed
            pong.play(0)

        # check if ball has gone past bat - lose a life
        if ballrect.top > height:
            lives -= 1


            # start a new ball
            xspeed = xspeed_init
            rand = random.random()
            if random.random() > 0.5:
                xspeed = -xspeed
            yspeed = yspeed_init
            ballrect.center = width * random.random(), height / 3
            if lives == 0:
                msg = pygame.font.Font(None,70).render("Game Over", True, (0,255,255), bgcolour)
                msgrect = msg.get_rect()
                msgrect = msgrect.move(width / 2 - (msgrect.center[0]), height / 3)
                screen.blit(msg, msgrect)
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
                        screen.fill(bgcolour)
                        wall.build_wall(width)
                        lives = max_lives
                        score = 0
                        break

        if xspeed < 0 and ballrect.left < 0:
            xspeed = -xspeed
            pong.play(0)

        if xspeed > 0 and ballrect.right > width:
            xspeed = -xspeed
            pong.play(0)

        # check if ball has hit wall
        # if yes then delete brick and change ball direction
        index = ballrect.collidelist(wall.brickrect)
        if index != -1:
            if ballrect.center[0] > wall.brickrect[index].right or \
                ballrect.center[0] < wall.brickrect[index].left:
                xspeed = -xspeed
            else:
                yspeed = -yspeed
            pong.play(0)
            wall.brickrect[index:index + 1] = []
            score += 10

        #display the scores
        screen.fill(bgcolour)
        scoretext = pygame.font.Font(None,40).render(str(score), True, (0,255,255), bgcolour)
        scoretextrect = scoretext.get_rect()
        scoretextrect = scoretextrect.move(width - scoretextrect.right, 0)
        screen.blit(scoretext, scoretextrect)

        #display the lives left
        #adding the hearts image to the display
        #livesleft = pygame.font.Font(None,40).render(str(lives), True, (0,255,255), bgcolour)
        #livesleftrect = livesleft.get_rect()
        #livesleftrect = livesleftrect.move(0,0)
        #screen.blit(livesleft, livesleftrect)

        #Display the number of live left.
        livepos = 0
        for i in range(lives):

            hearts = pygame.image.load("ball.png").convert()
            hearts.set_colorkey((255, 255 , 255))
            heartsrect = hearts.get_rect()
            heartsrect = heartsrect.move(livepos,0)
            screen.blit(hearts, heartsrect)
            livepos+=30


        for i in range(0, len(wall.brickrect)):
            screen.blit(wall.brick, wall.brickrect[i])    #displaying the brick wall

        # if wall completely gone then rebuild it
        if wall.brickrect == []:
            wall.build_wall(width)
            xspeed = xspeed_init
            yspeed = yspeed_init
            ballrect.center = width / 2, height / 3

        screen.blit(ball, ballrect)
        screen.blit(bat, batrect)
        pygame.display.flip()


def main_menu():
        pygame.init()
        pygame.display.set_caption("Simple Breakout")
        screen = pygame.display.set_mode((640,480), DOUBLEBUF)
        pygame.mouse.set_visible(1)

        def option1():
            main(screen)
        def option2():
            level = askopenfilename()
            try: test = pickle.load(open(level, 'rb'))
            except pickle.UnpicklingError:
                print('Error Loading File', 'File selected is not a level')
                return
            except IOError: return # they pressed cancel
            finally: del test
            main(screen, level)
        def option3():
            level_editor.level_editor(screen)
        def option4():
            main(screen, None, True)
        def option5():
            pygame.quit()
            sys.exit()

        font = pygame.font.Font('freesansbold.ttf', 32)

        titletext = font.render('Simple Breakout', True, (255,255,255))
        titletextrect = titletext.get_rect()
        titletextrect.centerx = 320; titletextrect.y = 110

        menu = ezmenu.EzMenu(
            ['New Game', option1],
            ['Load Level', option2],
            ['Level Editor', option3],
            ['Watch AI', option4],
            ['Quit Game', option5])

        menu.center_at(320, 240)
        menu.set_normal_color((255,255,255))

        screen.blit(titletext, titletextrect)

        clock = pygame.time.Clock()
        pygame.display.flip()

        while 1:
            clock.tick(60)
            events = pygame.event.get()

            menu.update(events)

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            screen.fill((0,0,0))
            menu.draw(screen)
            screen.blit(titletext, titletextrect)
            pygame.display.flip()



class Wall():

    def __init__(self):
        self.brick = pygame.image.load("brick.png").convert()
        brickrect = self.brick.get_rect()
        self.bricklength = brickrect.right - brickrect.left
        self.brickheight = brickrect.bottom - brickrect.top

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

            self.brickrect.append(self.brick.get_rect())
            self.brickrect[i] = self.brickrect[i].move(xpos, ypos)
            xpos = xpos + self.bricklength

if __name__ == '__main__':
    #br = Breakout()
    main_menu()


