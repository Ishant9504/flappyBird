import pygame
import neat
import os
import random
import time
pygame.font.init()  # Initialize fonts

from base import Base  # Import the Base class from the base module
from bird import Bird  # Import the Bird class from the bird module
from pipe import Pipe  # Import the Pipe class from the pipe module

# Global variables
GEN = 0  # Keeps track of the current generation
WIN_WIDTH = 500  # Width of the game window
WIN_HEIGHT = 800  # Height of the game window
MAX_FPS = 30  # Maximum frames per second

# Load background image and scale it up
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# Define the font for displaying score and generation count
STAT_FONT = pygame.font.SysFont("comicsans", 50)

def draw_window(win, birds, pipes, base, score, gen):
    """
    Draw all elements on the game window.

    Parameters:
    win (pygame.Surface): The game window surface.
    birds (list): List of Bird objects.
    pipes (list): List of Pipe objects.
    base (Base): The Base object.
    score (int): The current score.
    gen (int): The current generation.
    """
    win.blit(BG_IMG, (0, 0))  # Draw the background
    for pipe in pipes:
        pipe.draw(win)  # Draw each pipe

    # Display the current score
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # Display the current generation
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)  # Draw the base

    for bird in birds:
        bird.draw(win)  # Draw each bird

    pygame.display.update()  # Update the display with the new drawings

def main(genomes, config):
    """
    The main loop for the game, where the AI is trained and gameplay occurs.

    Parameters:
    genomes (list): List of genomes provided by NEAT.
    config (neat.config.Config): NEAT configuration object.
    """
    global GEN
    GEN += 1  # Increment generation count

    nets = []  # List to hold the neural networks
    ge = []  # List to hold the genomes
    birds = []  # List to hold the bird objects

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # Create a neural network from the genome
        nets.append(net)  # Add the network to the list
        birds.append(Bird(230, 350))  # Add a new bird at the starting position
        g.fitness = 0  # Initialize the fitness score for the genome
        ge.append(g)  # Add the genome to the list

    base = Base(730)  # Create a Base object
    pipes = [Pipe(600)]  # Create a list with one initial Pipe object
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # Create the game window

    clock = pygame.time.Clock()  # Create a clock object to manage frame rate

    score = 0  # Initialize the score
    
    run = True
    while run:
        clock.tick(MAX_FPS)  # Limit the loop to MAX_FPS frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        # Determine the index of the pipe to use for input to the neural network
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1  # If bird has passed the first pipe, target the next pipe
        else:
            run = False  # If no birds left, end the loop
            break

        for x, bird in enumerate(birds):
            bird.move()  # Move the bird
            ge[x].fitness += 0.01  # Increment fitness for staying alive

            # Get output from the neural network
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            # Make the bird jump if the output exceeds the threshold
            if output[0] > 0.5:
                bird.jump()

        rem = []  # List to hold pipes to be removed
        add_pipe = False  # Flag to check if a new pipe should be added
    
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # Penalize fitness for hitting a pipe
                    birds.pop(x)  # Remove the bird from the list
                    nets.pop(x)  # Remove the corresponding network
                    ge.pop(x)  # Remove the corresponding genome
           
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True  # Mark the pipe as passed
                    add_pipe = True  # Set flag to add a new pipe

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)  # Mark pipe for removal if it is off the screen
            pipe.move()  # Move the pipe

        if add_pipe:
            score += 1  # Increment score
            for g in ge:
                g.fitness += 5  # Reward fitness for passing a pipe
            pipes.append(Pipe(600))  # Add a new pipe

        for r in rem:
            pipes.remove(r)  # Remove the old pipes

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)  # Remove bird if it hits the ground or flies too high
                nets.pop(x)  # Remove the corresponding network
                ge.pop(x)  # Remove the corresponding genome
        
        if score > 30:  # End the loop if a bird scores more than 30 points
            break

        base.move()  # Move the base
        draw_window(win, birds, pipes, base, score, GEN)  # Draw all game elements

def run(config_path):
    """
    Run the NEAT algorithm to train a neural network to play the game.

    Parameters:
    config_path (str): Path to the NEAT configuration file.
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)  # Create a population with the given config

    # Add reporters to give us some output during the training process
    p.add_reporter(neat.StdOutReporter(True))  # Print progress to the console
    stats = neat.StatisticsReporter()  # Collect statistics
    p.add_reporter(stats)  # Add the statistics reporter

    # Run the NEAT algorithm for up to 50 generations
    winner = p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)  # Get the directory containing the script
    config_path = os.path.join(local_dir, "config-feedforward.txt")  # Path to the config file
    run(config_path)  # Run the NEAT algorithm
