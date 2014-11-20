##    This file is part of Simple Breakout.
##
##    Simple Breakout is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    Simple Breakout is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with Simple Breakout.  If not, see <http://www.gnu.org/licenses/>.
from tkFileDialog import askopenfilename
try: import cPickle as pickle
except ImportError: import pickle
from pygame.locals import *
import pygame, random, sys, ezmenu, level_editor

class Block(pygame.sprite.Sprite):
    """ A breakout block """
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.x = x; self.y = y

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

class Ball(pygame.sprite.Sprite):
    """ The ball of the game """
    def __init__(self, image, x, y, dx, dy, screensize, blocks):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.x = x; self.y = y
        self.dx = dx; self.dy = dy
        self.screensize = screensize
        self.belowscreen = False
        self._rect = pygame.Rect(self.rect)
        self.blocks = blocks
        self.paused = False
        self.points = 0

    def pause(self): self.paused = not self.paused

    def update(self):
        if not self.paused:
            self._rect = pygame.Rect(self.rect)

            for block in self.blocks.sprites():
                if self.rect.colliderect(block.rect):
                    # where are we in comparison to this object?
                    if block.rect.collidepoint(self.rect.topleft):
                        # upper left corner is in
                        if block.rect.collidepoint(self.rect.topright):
                            # top edge is in, move down by overlap
                            self.y = block.rect.bottom
                            self.dy = -self.dy
                        elif block.rect.collidepoint(self.rect.bottomleft):
                            # left edge is in, move right by overlap
                            self.x = block.rect.right
                            self.dx = abs(self.dx)
                        else:
                            # no edge in. (at least on this side)
                            # find the overlap for x and y
                            ovx = abs(self.x-block.rect.right)
                            ovy = abs(self.y-block.rect.bottom)
                            if ovx >= ovy: # came from bottom
                                self.y = block.rect.bottom
                                self.dy = -self.dy
                            else: # came from right
                                self.x = block.rect.right
                                self.dx = abs(self.dx)
                    elif block.rect.collidepoint(self.rect.topright):
                        # upper right corner is in
                        if block.rect.collidepoint(self.rect.bottomright):
                            # right edge is in, move left by overlap
                            self.x = block.rect.left-self.rect.width
                            self.dx = -abs(self.dx)
                        else:
                            # no edge is in. (at least on this side)
                            # find the overlap for x and y
                            ovx = abs(self.rect.right-block.rect.left)
                            ovy = abs(self.y-block.rect.bottom)
                            if ovx >= ovy: # came from bottom
                                self.y = block.rect.bottom
                                self.dy = -self.dy
                            else: # came from left
                                self.x = block.rect.left-self.rect.width
                                self.dx = -abs(self.dx)
                    elif block.rect.collidepoint(self.rect.bottomright):
                        # bottom right corner is in
                        if block.rect.collidepoint(self.rect.bottomleft):
                            # bottom edge is in
                            self.y = block.rect.top-self.rect.height
                            self.dy = -self.dy
                        else:
                            # no edge is in. (at least on this side)
                            # find the overlap for x and y
                            ovx = abs(self.x-block.rect.left-self.rect.width)
                            ovy = abs(self.y-block.rect.top-self.rect.height)
                            if ovx <= ovy: # came from top
                                self.y = block.rect.top-self.rect.height
                                self.dy = -self.dy
                            else: # came from left
                                self.x = block.rect.left-self.rect.width
                                self.dx = -abs(self.dx)
                    elif block.rect.collidepoint(self.rect.bottomleft):
                        # bottom left corner is in
                        # we have eliminiated all sides
                        # find the overlap for x and y
                        ovx = abs(self.x-block.rect.right)
                        ovy = abs(self.rect.bottom-block.rect.top)
                        if ovx >= ovy: # came from top
                            self.y = block.rect.top-self.rect.height
                            self.dy = -self.dy
                        elif ovx < ovy: # came from right
                            self.x = block.rect.right
                            self.dx = abs(self.dx)
                    block.kill()
                    self.points += 1
                    break
            
            if self.rect.right > self.screensize[0]:
                self.x = self.screensize[0]-self.rect.width
                self.dx = -self.dx
            if self.y > self.screensize[1]:
                self.belowscreen = True
            if self.x < 0:
                self.x = 0
                self.dx = -self.dx
            if self.y < 0:
                self.y = 0
                self.dy = -self.dy

            self.x += self.dx
            self.y += self.dy
            self.rect.x = self.x
            self.rect.y = self.y

class Paddle(pygame.sprite.Sprite):
    """ The paddle of the game """
    def __init__(self, image, x, y, ball, screensize):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.x = x; self.y = y
        self.screensize = screensize
        self.ball = ball
        self.paused = False

    def pause(self): self.paused = not self.paused

    def update(self):
        if not self.paused:
            if self.rect.colliderect(self.ball.rect):
                self.ball.y  = self.y-self.ball.rect.height
                self.ball.dy = -random.randint(1,7)
                self.ball.dx = random.randint(-7,7)

            self.rect.x = self.x
            self.rect.y = self.y

def load_level(path):
    blocks = pickle.load(open(path, 'rb'))
    level = pygame.sprite.Group()
    for block in blocks:
        blimg = pygame.Surface((20,10))
        blimg.fill(block[1])
        blpos = block[0]
        bl = Block(blimg, blpos[0], blpos[1])
        level.add(bl)
    return level

def main_menu():
    pygame.init()
    pygame.display.set_caption('Simple Breakout')
    screen = pygame.display.set_mode((640,480), DOUBLEBUF)
    pygame.mouse.set_visible(1)

    def option1():
        main(screen)
    def option2():
        level = askopenfilename()
        try: test = pickle.load(open(level, 'rb'))
        except pickle.UnpicklingError:
            showerror('Error Loading File', 'File selected is not a level')
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
        clock.tick(30)
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

def lastscreen(screen, points, deaths):
    screen.fill((0,0,0))
    pygame.mouse.set_visible(1)

    # create all text
    font1 = pygame.font.Font('freesansbold.ttf', 28)
    font2 = pygame.font.Font('freesansbold.ttf', 20)
    text1 = font1.render('CONGRATULATIONS!!!', True, (255,255,255))
    text2 = font2.render('Final Score:', True, (255,255,255))
    if points-(deaths*10) < 0: final = 0
    else: final = points-(deaths*10)
    text3 = font2.render(str(points)+' - '+str(deaths)+' * 10 = '+str(final), True, (255,255,255))
    text4 = font2.render('Press any key to return to menu', True, (255,255,255))

    # figure out where it goes
    text1rect = text1.get_rect()
    text2rect = text2.get_rect()
    text3rect = text2.get_rect()
    text4rect = text4.get_rect()

    text1rect.centerx = 320
    text1rect.y = 40
    text2rect.x = text1rect.x
    text2rect.y = text1rect.bottom+20
    text3rect.x = text1rect.x
    text3rect.y = text2rect.bottom+10
    text4rect.centerx = 320
    text4rect.y = 470-text4rect.height

    # put it all on the screen
    screen.blit(text1, text1rect)
    screen.blit(text2, text2rect)
    screen.blit(text3, text3rect)
    screen.blit(text4, text4rect)

    # set up the fps
    clock = pygame.time.Clock()
    pygame.display.flip()

    while 1:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                return

        screen.blit(text1, text1rect)
        screen.blit(text2, text2rect)
        screen.blit(text3, text3rect)
        screen.blit(text4, text4rect)

        pygame.display.flip()

def main(screen, level=None, ai=False):
    pygame.init()
    pygame.mouse.set_visible(0)

    if level == None: level = 1
    ballimg = pygame.Surface((10,10))
    ballimg.fill((255,255,255))
    paddleimg = pygame.Surface((50,10))
    paddleimg.fill((255,255,255))
    blockimg = pygame.Surface((20,10))
    blockimg.fill((255,255,255))
    startballdelay = 30;
    count = 0; balloff = False; deaths = 0
    font = pygame.font.Font('freesansbold.ttf', 18)
    points = font.render('Points: 0', True, (255,255,255))
    pointsrect = points.get_rect()
    pointsrect.x = 630 - pointsrect.width
    pointsrect.y = 10

    if type(level) == int:
        blocks = load_level('./data/levels/lvl'+str(level)+'.lvl'); level += 1
    else:
        blocks = load_level(level)
    ball = Ball(ballimg, 320,430, 0, 0, (640,480), blocks)
    paddle = Paddle(paddleimg, 300,450, ball, (640,480))
    clock = pygame.time.Clock()

    ball.update()
    paddle.update()
    blocks.update()

    screen.blit(font.render('Deaths: '+str(deaths), True, (255,255,255)), (10, 450))
    screen.blit(points, pointsrect)
    screen.blit(ball.image, ball.rect)
    screen.blit(paddle.image, paddle.rect)
    blocks.draw(screen)
    pygame.display.flip()

    while 1:
        clock.tick(60)

        if not pygame.display.get_active():
            ball.paused = True
            paddle.paused = True
        else:
            if not ball.paused:
                ball.paused = False
            if not paddle.paused:
                paddle.paused = False

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                if event.key == K_RETURN:
                    ball.pause()
                    paddle.pause()

        if not balloff:
            if count < startballdelay:
                count += 1
                ball.x = paddle.rect.centerx-ball.rect.width/2
                ball.y = 430
            else:
                count = 0
                ball.dx = random.randint(-7,7)
                ball.dy = random.randint(-7,7)
                if ball.dy == 0: ball.dy = 1
                balloff = True

        if not ball.paused: ball.image.fill((random.randint(0,255), random.randint(0,255), random.randint(0,255)))

        if ball.belowscreen:
            ball.x = paddle.rect.centerx-ball.rect.width/2
            ball.y = 430
            ball.dx = 0
            ball.dy = 0
            balloff = False
            ball.belowscreen = False
            deaths += 1

        if len(blocks) == 0:
            if type(level) == int:
                level += 1
                if './data/levels/lvl'+str(level)+'.lvl' in os.listdir('./data/levels/'):
                    blocks = load_level('./data/levels/lvl'+str(level)+'.lvl')
                else:
                    lastscreeen(screen, ball.points, deaths)
                    return
                ball.blocks = blocks
                ball.dx = 0
                ball.dy = 0
                balloff = False
                ball.belowscreen = False
            else:
                lastscreen(screen, ball.points, deaths)
                return

        if not ai: paddle.x = pygame.mouse.get_pos()[0]-paddle.rect.width/2
        else: paddle.x = ball.x-ball.rect.width/2-paddle.rect.width/2
        points = font.render('Points: '+str(ball.points), True, (255,255,255))
        pointsrect = points.get_rect()
        pointsrect.x = 630 - pointsrect.width
        pointsrect.y = 450

        paddle.update()
        ball.update()
        blocks.update()
        screen.fill((0,0,0))
        screen.blit(font.render('Deaths: '+str(deaths), True, (255,255,255)), (10, 450))
        screen.blit(points, pointsrect)
        screen.blit(paddle.image, paddle.rect)
        screen.blit(ball.image, ball.rect)
        blocks.draw(screen)
        pygame.display.flip()


if __name__ == '__main__': main_menu()
