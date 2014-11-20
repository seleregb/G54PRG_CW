# level editor
try: import cPickle as pickle
except ImportError: import pickle
from pygame.locals import *
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import showerror
import pygame

def level_editor(screen):
    pygame.display.set_caption('Simple Breakout Level Editor')
    pygame.mouse.set_visible(1)

    grid = []; curblocks = []; curcolor = (255,255,255)
    font = pygame.font.Font(None, 18)
    paddleimg = pygame.Surface((50,10))
    paddleimg.fill((255,255,255))
    chcolor = font.render('Choose Color', 1, (255,255,255))
    chcolorrect = chcolor.get_rect()
    chcolorrect.x = 10; chcolorrect.y = 10
    save = font.render('Save Level', 1, (255,255,255))
    saverect = save.get_rect()
    saverect.x = chcolorrect.right+10; saverect.y = 10
    load = font.render('Load Level', 1, (255,255,255))
    loadrect = load.get_rect()
    loadrect.x = saverect.right+10; loadrect.y = 10
    new = font.render('New Level', 1, (255,255,255))
    newrect = new.get_rect()
    newrect.x = loadrect.right+10; newrect.y = 10
    done = font.render('Quit', 1, (255,255,255))
    donerect = done.get_rect()
    donerect.x = newrect.right+10; donerect.y = 10

    # create a grid of positions
    for x in range(0,screen.get_width(),20):
        for y in range(40,screen.get_height()-80,10):
            grid.append((x, y, x+20, y+10))

    screen.fill((0,0,0))
    screen.blit(paddleimg, (300,450))
    screen.blit(chcolor, chcolorrect)
    screen.blit(save, saverect)
    screen.blit(load, loadrect)
    screen.blit(new, newrect)
    screen.blit(done, donerect)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(30)

        mousepos = pygame.mouse.get_pos()
        mouserect = pygame.Rect(mousepos[0],mousepos[1], 1,1)
        if chcolorrect.colliderect(mouserect):
            chcolor = font.render('Choose Color', 1, (255,0,0))
        else:
            chcolor = font.render('Choose Color', 1, (255,255,255))
        if saverect.colliderect(mouserect):
            save = font.render('Save Level', 1, (255,0,0))
        else:
            save = font.render('Save Level', 1, (255,255,255))
        if loadrect.colliderect(mouserect):
            load = font.render('Load Level', 1, (255,0,0))
        else:
            load = font.render('Load Level', 1, (255,255,255))
        if newrect.colliderect(mouserect):
            new = font.render('New Level', 1, (255,0,0))
        else:
            new = font.render('New Level', 1, (255,255,255))
        if donerect.colliderect(mouserect):
            done = font.render('Quit', 1, (255,0,0))
        else:
            done = font.render('Quit', 1, (255,255,255))

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == MOUSEBUTTONUP:
                if chcolorrect.colliderect(mouserect):
                    nextcolor = askcolor()[0]
                    if nextcolor == None: pass # they pressed cancel
                    else: curcolor = nextcolor
                elif saverect.colliderect(mouserect):
                    try:
                        tofile = open(asksaveasfilename(), 'wb')
                        pickle.dump(curblocks, tofile)
                        tofile.close()
                    except IOError: pass # they pressed cancel
                elif loadrect.colliderect(mouserect):
                    try: curblocks = pickle.load(open(askopenfilename(), 'rb'))
                    except pickle.UnpicklingError: showerror('Error Loading File', 'File selected is not a level') # Oops! not a level
                    except IOError: pass # they pressed cancel
                elif newrect.colliderect(mouserect):
                    curblocks = []
                elif donerect.colliderect(mouserect):
                    return
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for pos in grid:
                        if mousepos[0] >= pos[0] and mousepos[0] <= pos[2] and\
                           mousepos[1] >= pos[1] and mousepos[1] <= pos[3]:
                            curblocks.append(((pos[0], pos[1]), curcolor))
                            break
                if event.button == 3:
                    for pos in grid:
                        if mousepos[0] >= pos[0] and mousepos[0] <= pos[2] and\
                           mousepos[1] >= pos[1] and mousepos[1] <= pos[3]:
                            nextblocks = []
                            for block in curblocks:
                                if block[0] == (pos[0], pos[1]):
                                    continue
                                else:
                                    nextblocks.append(block)
                            curblocks = nextblocks
                            del nextblocks

        screen.fill((0,0,0))
        for block in curblocks:
            toblit = pygame.Surface((20,10))
            toblit.fill(block[1])
            screen.blit(toblit, block[0])   
        screen.blit(paddleimg, (300,450))
        screen.blit(chcolor, chcolorrect)
        screen.blit(save, saverect)
        screen.blit(load, loadrect)
        screen.blit(new, newrect)
        screen.blit(done, donerect)
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((640,480), DOUBLEBUF)
    level_editor(screen)
    pygame.quit()

if __name__ == '__main__': main()
