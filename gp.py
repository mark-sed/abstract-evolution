"""
Abstract evolution
Genetic programming unit
"""

import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
import random
from random import randint
from copy import deepcopy
from abstract_evolution import Lang


# TODO: Leave the option to grow seeds continuously as it is now but also add option to evolve them at the start
class Seed:
    """
    Paint seed, grows on the canvas leaving paint trail
    """

    # Used for unique color
    CLOSED_LIST = []

    def __init__(self, min_x, max_x, min_y, max_y, min_w, max_w, ref_arr, randomize_colors=False, unique_colors=False):
        """
        Constructor
        :param min_x Minimal x position
        :param max_x Maximal x position
        :param min_y Minimal y position
        :param max_y Maximal y position
        :param min_w Minimal width
        :param max_w Maximal width
        :param ref_arr Reference image
        :param randomize_colors If random colors should be used or the colors in reference image
        :param unique_colors No 2 seeds can have the same color
        """
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.x = randint(min_x, max_x)
        self.y = randint(min_y, max_y)
        if randomize_colors:
            # Pick random color
            self.color = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            # If uniqueness is required generate new color
            while unique_colors and self.c in Seed.CLOSED_LIST:
                self.color = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            Seed.CLOSED_LIST.append(self.color)
        else:
            self.color = [x for x in ref_arr[randint(0, len(ref_arr)-1)][randint(0, len(ref_arr[0])-1)]]
            while unique_colors and self.color in Seed.CLOSED_LIST:
                self.color = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            Seed.CLOSED_LIST.append(self.color)
        self.generate_directions()
        self.w = randint(min_w, max_w)

    def grow(self):
        """
        Grows the seed in its direction
        """
        self.x += 1*self.dir_x
        self.y += 1*self.dir_y
        if self.x < self.min_x or self.x > self.max_x or self.y < self.min_y or self.y > self.max_y:
            self.x = randint(self.min_x, self.max_x)
            self.y = randint(self.min_y, self.max_y)
        
    def generate_directions(self):
        """
        Picks random direction for the seed
        """
        r = randint(0, 7)
        if r == 0:  # N
            self.dir_x = 0
            self.dir_y = -1
        elif r == 1: # NE
            self.dir_x = 1
            self.dir_y = -1
        elif r == 2: # E
            self.dir_x = 1
            self.dir_y = 0
        elif r == 3: # SE
            self.dir_x = 1
            self.dir_y = 1
        elif r == 4: # S
            self.dir_x = 0
            self.dir_y = 1
        elif r == 5: # SW
            self.dir_x = -1
            self.dir_y = 1
        elif r == 6: # W
            self.dir_x = -1
            self.dir_y = 0
        else: # NW
            self.dir_x = -1
            self.dir_y = -1


class Phenotype:
    """
    Phenotype of potential image
    """

    # List of colors used by other phenotypes
    CLOSED_LIST = []

    def __init__(self, ref_arr, seed_amount=0, min_w=0, max_w=0, randomize_colors=True, unique_colors=False):
        """
        Constructor
        :param ref_arr Reference image as an numpy array used for fitness
        :param seed_amount Amount of seeds to generate
        :param min_w Minimum seed width
        :param max_w Maximum seed width
        :param randomize_colors If True color of the phenotype will be picked at random
                                otherwise values will be extracted from the reference image
        :param unique_colors If True then no 2 phenotypes will have the same color
        """
        self.arr = np.zeros_like(ref_arr)
        if randomize_colors:
            # Pick random color
            pixel = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            # If uniqueness is required generate new color
            while unique_colors and pixel in Phenotype.CLOSED_LIST:
                pixel = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            Phenotype.CLOSED_LIST.append(pixel)
        else:
            pixel = [x for x in ref_arr[randint(0, len(ref_arr)-1)][randint(0, len(ref_arr[0])-1)]]
            while unique_colors and pixel in Phenotype.CLOSED_LIST:
                pixel = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            Phenotype.CLOSED_LIST.append(pixel)
        for i in range(len(self.arr)):
            for a in range(len(self.arr[0])):
                self.arr[i][a] = pixel
        self.seed_amount = seed_amount
        # TODO: Apply color settings also to lines
        self.seeds = [Seed(0, len(self.arr)-1, 0, len(self.arr[0])-1, min_w, max_w, ref_arr, randomize_colors, unique_colors) for _ in range(seed_amount)]
        self.paint_seeds()

    def paint_seeds(self):
        """
        Paints seeds on the canvas
        """
        for x, y, c, w in self.get_seeds():
            pixel = np.full((w, w, 4), c)
            start_x = x-w//2 if x-w//2 >= 0 else 0
            end_x = x+w//2 if x+w//2 < len(self.arr) else len(self.arr)-1
            start_y = y-w//2 if y-w//2 >= 0 else 0
            end_y = y+w//2 if y+w//2 < len(self.arr[0]) else len(self.arr[0])-1
            # TODO: Dont continue but fill
            if end_x-start_x != w or end_y-start_y != w:
                continue
            self.arr[start_x:end_x, start_y:end_y] = pixel

    def grow_seeds(self, dir_change_chance=0.0):
        """
        Grows all seeds
        :param dir_change_chance Chance that the direction of the seed will change
        """
        for s in self.seeds:
            s.grow()
            if random.random() <= dir_change_chance:
                s.generate_directions()

    def paint_line(self, length, dir_change_chance=0.0):
        """
        Paints line of set length
        :param length Length of the line (number of grows)
        :param dir_change_chance Chance that the direction of the seed will change
        """
        for _ in range(length):
            self.grow_seeds(dir_change_chance)
            self.paint_seeds()

    def get_seeds(self):
        """
        :return Seed as tuple of x, y, color and width
        """
        return [(s.x, s.y, s.color, s.w) for s in self.seeds]


class Population:
    """
    Population of phenotypes
    """

    def __init__(self, size, ref_arr, min_seeds, max_seeds, min_w, max_w, randomize_colors, unique_colors):
        """
        Constructor
        :param size How many phenotypes will there be in one population
        :param ref_arr Reference image as an array used for the fitness
        :param min_seeds Minimum amount of seeds
        :param max_seeds Maximum amount of seeds
        :param min_w Minimum line width
        :param max_w Maximum line width
        :param randomize_colors If True color of the phenotype will be picked at random
                                otherwise values will be extracted from the reference image
        :param unique_colors If True then no 2 phenotypes will have the same color
        """
        self.size = size
        self.ref_arr = ref_arr
        self.phenotypes = [Phenotype(self.ref_arr, randint(min_seeds, max_seeds), min_w, max_w, randomize_colors, unique_colors) for _ in range(size)]
        
    def grow_seeds(self):
        """
        Grows all seeds
        """
        for p in self.phenotypes:
            p.grow_seeds()
            p.paint_seeds()

    def paint_lines(self, min, max, dir_change_chance=0.0):
        """
        Paints a line of of random length in between min and max
        :param min Minimum line length
        :param max Maximum line length
        :param dir_change_chance Chance of direction being changed
        """
        for p in self.phenotypes:
            p.paint_line(randint(min, max), dir_change_chance)

    def __getitem__(self, key):
        """
        Returns phenotype's array
        :param key Key to the phenotype's dict
        """
        return self.phenotypes[key].arr


class Evolution:
    """
    Genetic programming over images
    """

    def __init__(self, params_window, main_window, reference_image):
        """
        Constructor
        :param params_window Window containing evolution parameters
        :param main_window Main application window (needed for phenotype rendering)
        :param reference_image Image used as a reference for evolution
        """
        self.params_window = params_window
        self.main_window = main_window
        self.ref_img = Image.open(reference_image).convert('RGBA')
        self.ref_img_arr = np.array(self.ref_img)
        min_seeds = 0
        max_seeds = 0
        if params_window.evolve_lines:
            min_seeds = params_window.min_seeds
            max_seeds = params_window.max_seeds
        self.population = Population(params_window.population_size, self.ref_img_arr, 
                                     min_seeds, max_seeds, params_window.min_seed_w, params_window.max_seed_w,
                                     params_window.randomize_colors, params_window.unique_colors)

    def fitness_hist(self, arr1, arr2):
        """
        Calculates fitness based on histograms
        :param arr1 First image array
        :param arr2 Second image array
        """
        bin_counts1, _ = np.histogram(arr1.ravel(), bins=256, range=(0, 254))
        bin_counts2, _ = np.histogram(arr2.ravel(), bins=256, range=(0, 254))
        fitness = np.sum(np.absolute(np.subtract(bin_counts1, bin_counts2)))
        return fitness

    def init_fitness_points(self, ref_arr, amount, size, uniform):
        """
        Initializes values needed for fitness_points function
        :param amount Amount of points for check
        :param size Size of each point (square, where size is its side)
        :param uniform If True, then the points will be uniformly distributed
               otherwise random 
        """
        self.pm_size = size
        if uniform:
            self.pm_points = []
            area = len(ref_arr)*len(ref_arr[0])
            point_area = area / amount
            length = int(point_area**0.5)
            i = length//2
            while i < len(ref_arr):
                j = length//2
                while j < len(ref_arr[0]):
                    self.pm_points.append((i, j))
                    j+= length
                i += length
        else:
            self.pm_points = [(randint(0, len(ref_arr)-1), randint(0, len(ref_arr[0])-1)) for p in range(amount)]  

    def fitness_points(self, arr1, arr2):
        """
        Fitness function using points
        :param arr1 First image array
        :param arr2 Second image array
        :warning init_fitness_points needs to be called before this
        """
        fit = 0
        for x, y in self.pm_points:
            p1 = arr1[x:x+self.pm_size, y:y+self.pm_size]
            p2 = arr2[x:x+self.pm_size, y:y+self.pm_size]
            fit += np.sum(np.absolute(np.subtract(p1, p2)))
        return fit

    def cross2phenos(self, p1, p2):
        """
        Crossovers 2 phenotypes creating a new one
        :param p1 First phenotype to crossover
        :param p2 Second phenotype to crossover
        :return New phenotype which is a crossover of p1 and p2
        """
        n1 = deepcopy(p1)
        n2 = p2
        start_x = randint(0, len(p2.arr)-2)
        start_y = randint(0, len(p2.arr[0])-2)
        end_x = randint(start_x, len(p2.arr)-1)
        end_y = randint(start_y, len(p2.arr[0])-1)
        n1.arr[start_x:end_x,start_y:end_y] = n2.arr[start_x:end_x,start_y:end_y]
        return n1

    def crossover(self):
        """
        Performs crossovers on phenotypes in population
        """
        # TODO: Add rotation
        # TODO: Make other than just rect cuts
        new_phenos = []
        for i in range(int(self.params_window.population_size*(self.params_window.crossover_percentage/100))):
            i2 = randint(0, self.params_window.population_size-1)
            if i2 == i: # Just skip if its the same one
                continue 
            new_phenos.append(self.cross2phenos(self.fits[i][1], self.fits[i2][1]))
        for i, worst in enumerate(reversed(self.fits)):
            if i >= len(new_phenos):
                break
            self.population.phenotypes[worst[2]] = new_phenos[i]

    def start_evolution(self):
        """
        Main evolution cycle, takes parameters from params_window directly
        """
        params = self.params_window
        # Init fitness if needed be
        if params.fitness_fun == 0:  # CH
            self.fitness_function = self.fitness_hist
        elif params.fitness_fun == 1:  # RPM
            self.init_fitness_points(self.ref_img_arr, params.pm_amount, params.pm_size, False)
            self.fitness_function = self.fitness_points
        else:
            self.init_fitness_points(self.ref_img_arr, params.pm_amount, params.pm_size, True)
            self.fitness_function = self.fitness_points

        if params.evolve_lines:
            # Calculate diagonal length
            max_size = (len(self.ref_img_arr)**2 + len(self.ref_img_arr[1])**2)**0.5
            self.population.paint_lines(10, int(max_size), params.dir_change_chance/100)

        # TODO: Add mutation - Random one shape added to the image
        # TODO: Randomly add one color phenotypes to the population?
        # TODO: Try incorporating back options for lines as is in lines branch
        # Main loop of evolution
        for iteration in range(params.iterations):
            self.fits = [(self.fitness_function(x.arr, self.ref_img_arr), x, c) for c, x in enumerate(self.population.phenotypes)]
            self.fits.sort(key=lambda x: x[0])
            self.crossover()
            if (iteration+1) % (params.iterations * (params.update_freq/100)) == 0:
                print("Best fitness: {}".format(self.fits[0][0]))
                self.display_image(self.fits[0][1].arr)
                params.parent.repaint()
            params.parent.update_progress(int(iteration/params.iterations*100))
        
        params.parent.update_progress(Lang.TEXT["finished"][params.parent.lang])
        self.best_arr = self.fits[0][1].arr
        self.display_image(self.best_arr)
        print("Fitness: {}".format(self.fits[0][0]))

    def save_image(self, path):
        """
        Saves self.best phenotype's image as a png file
        This method is called by the GUI (from the outside)
        :param path Path to where should be the image saved
        """
        img_s = Image.fromarray(self.best_arr, 'RGBA')
        img_s.save(path, 'png')

    def display_image(self, img):
        """
        Displays passed in image to the GUI window
        :param img Image to be displayed
        """
        qim = ImageQt(Image.fromarray(img, 'RGBA'))
        pix = QtGui.QPixmap.fromImage(qim)
        self.main_window.display_image(pix)