import pygame
import neat
import time
import os
import random
pygame.font.init()

#Load the dimensions of the game UI
WIN_WIDTH = 400
WIN_HEIGHT = 600

BIRD_IM1 = pygame.image.load(os.path.join("imgs", "bird1.png"))
BIRD_IM2 = pygame.image.load(os.path.join("imgs", "bird2.png"))
BIRD_IM3 = pygame.image.load(os.path.join("imgs", "bird3.png"))
new_width1 = int(BIRD_IM1.get_width() * 1.5)
new_height1 = int(BIRD_IM1.get_height() * 1.5)
BIRD_IMGS = [pygame.transform.scale(BIRD_IM1, (new_width1, new_height1)),
             pygame.transform.scale(BIRD_IM2, (new_width1, new_height1)),
             pygame.transform.scale(BIRD_IM3, (new_width1, new_height1))]
PIPE_IMG0 = pygame.image.load(os.path.join("imgs", "pipe.png"))
new_width_pipe = int(PIPE_IMG0.get_width() * 1.5)
new_height_pipe = int(PIPE_IMG0.get_height() * 1.5)
PIPE_IMG = pygame.transform.scale(PIPE_IMG0, (new_width_pipe, new_height_pipe))
BASE_IMG0 = pygame.image.load(os.path.join("imgs", "base.png"))
new_width_base = int(BASE_IMG0.get_width() * 1.5)
new_height_base = int(BASE_IMG0.get_height() * 1.5)
BASE_IMG = pygame.transform.scale(BASE_IMG0, (new_width_base, new_height_base))
BG_IMG0 = pygame.image.load(os.path.join("imgs", "bg.png"))
new_width = int(BG_IMG0.get_width() * 1.5)
new_height = int(BG_IMG0.get_height() * 1.5)
BG_IMG = pygame.transform.scale(BG_IMG0,(new_width, new_height))

STAT_FONT = pygame.font.SysFont("comicsans", 30)

#Program the bird class
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 #since pygame coordinates are 0,0 at the top left and the negative y axis is towards the top, we need to have a negative velocity to go upwards in the y direction
        self.tick_count = 0 #keeps track of when we last jumped, reset it to 0 to know when we change direction or velocity
        self.height = self.y #keeps track of where the bird originally started moving from

    #movement in every frame
    def move(self):
        self.tick_count += 1 #how many times we have moved since our last jump
        d = self.velocity*self.tick_count + self.tick_count**2 #how many pixels we were moving up or down in this frame
        if d >= 16: #terminal velocity
            d = 16
        if d < 0: 
            d -= 2

        self.y = self.y + d

        #tilt the bird
        if d < 0 or self.y<self.height+50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    #For the animation for the wings flapping up and down
    def draw(self, win): #win represents the window we are drawing the bird onto
        self.img_count += 1 #how many times we have shown one image

        #Checking what image to show based on the current image count
        if self.img_count < self.ANIMATION_TIME: #if image count less than 5(ANIMATION_TIME), we will display the first flappy bird
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #when the bird is tilted 90deg and going downwards, the wings should not flap
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        #we need to rotate the bird arounf its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
    
    #for collision 
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
        
#class for pipe
class Pipe:
    GAP = 170
    VEL = 5
    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    #Define the positions of the pipes 
    def set_height(self):
        self.height = random.randrange(100, 360)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #pixel perfect collisions, we create masks for the objects so they only collide when they actually do
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        #offset is how far away the pixels are from each other
        #offset for bird and the top pipe
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        #offset for bird and the bottom pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

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
        self.x1 -=  self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

#draws the window for the game
def draw_window(win, birds, pipes, base, score):
    #draw the bg, blit draws
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH-10-text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)

    pygame.display.update()



def main(genomes, config): #the parameters of the fitness function should have genomes, config(genomes is the number NN controlling the birds)
    nets = []
    ge = [] #track genomes' fitness based on how far they move
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(180,300))
        g.fitness = 0
        ge.append(g)


    base = Base(550)
    pipes = [Pipe(500)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock() #we set the custom frame rate
    
    score = 0
    run =True
    #main game loop
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0 #we are indexing the pipes so that we can calculate the distance for the closest pipe
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()


        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            #repeated pipes
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True 

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()
            #repeated pipes
        if add_pipe:
            score+=1
            for g in ge:
                g.fitness += 5 #encourages the bird to pass through the pipes more
            pipes.append(Pipe(500))

        for r in rem:
            pipes.remove(r)
        
        #when the bird hits the ground
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > 550 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50) #fitness

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)