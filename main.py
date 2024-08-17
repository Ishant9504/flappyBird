import pygame
import neat
import os
import random
import time
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
MAX_FPS = 30

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VAL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0 #tick count keeps check of when we last jumped
        self.height = self.y 

    def move(self):
        # moving up is negative
        # moving down is positive

        self.tick_count += 1 #how mamny times we moved since the last jump
        #tick counts will specify how many seconds we've been moving for
        #in one direction, thats why we reset it when we jump or something
        d = self.vel * self.tick_count + 1.5*self.tick_count**2 #displacement = ut+1/2at^2

        if d >= 16:
            d = 16
        
        if d <= 0:
            d -=2
        
        self.y = self.y + d # updating our y coordinate

        # If we're moving upwards and we want to tilt the bird upwards
        if d < 0 or self.y < self.height + 50 :
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        
        # Tilting completely 90 degree downwards
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VAL
    
    def draw(self, win): # window
        self.img_count += 1

        # UPDATE THE BIRD IMAGE FOR THE NUMBER OF TICKS
        if self.img_count <self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0] 
            self.img_count = 0

        # Condition to check whenever we're falling downward
        # We dont want our bird to flap wings then
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        #Now we wish to rotate our bird and not just draw it
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        
        # The following line somehow rotates our bird around its center
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x,self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # Do collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# Pipe Class
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False # to check if bird passed by it

        # calling random height function
        self.set_height()

    #Generating the height of the pipe using RANDOM
    def set_height(self):
        self.height = random.randrange(50 , 450)
        #y cordinate for top pipe
        self.top =  self.height - self.PIPE_TOP.get_height()
        #y coordinate for bottom pipe
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL
    
    def draw(self, win):
        win.blit(self.PIPE_TOP,(self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # Collision detection using Masks
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #Point of collisions
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        
        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        # Cycle the base images continously without running out 
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base, score):

    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    clock = pygame.time.Clock()

    # variable to keep track of score
    score = 0
    
    run = True
    while run:

        clock.tick(MAX_FPS)
        #Checks for any event in our pygame window
        for event in pygame.event.get():

            # Checks if event is QUIT then quits the window(red cross)
            if event.type == pygame.QUIT:
                run = False
        #bird.move()
        rem = [] # list of removed pipes
        add_pipe = False
    
        for pipe in pipes:
            # if pipe collides with bird
            if pipe.collide(bird):
                pass
            if pipe.x + pipe.PIPE_TOP.get_width() <0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()
        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730:
            pass
        base.move()
        draw_window(win, bird, pipes, base, score)
    pygame.quit()
    quit()

main()
    

