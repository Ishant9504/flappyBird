import pygame
import os

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

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
