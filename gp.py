import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
import random
from random import randint
from copy import deepcopy


class Seed:

    def __init__(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.x = randint(min_x, max_x)
        self.y = randint(min_y, max_y)
        self.color = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
        self.generate_directions()

    def grow(self):
        self.x += 1*self.dir_x
        self.y += 1*self.dir_y
        if self.x < self.min_x or self.x > self.max_x or self.y < self.min_y or self.y > self.max_y:
            self.x = randint(self.min_x, self.max_x)
            self.y = randint(self.min_y, self.max_y)
        

    def generate_directions(self):
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

    def __init__(self, ref_arr, seed_amount):
        self.arr = np.zeros_like(ref_arr)
        self.seed_amount = seed_amount
        self.seeds = [Seed(0, len(self.arr)-1, 0, len(self.arr[0])-1) for _ in range(seed_amount)]
        self.paint_seeds()

    def paint_seeds(self):
        for x, y, c in self.get_seeds():
            self.arr[x][y] = c

    def grow_seeds(self):
        for s in self.seeds:
            s.grow()

    def get_seeds(self):
        return [(s.x, s.y, s.color) for s in self.seeds]


class Population:
    """
    Population of phenotypes
    """

    def __init__(self, size, ref_arr, min_seeds, max_seeds):
        self.size = size
        self.ref_arr = ref_arr
        self.phenotypes = [Phenotype(self.ref_arr, random.randint(min_seeds, max_seeds)) for _ in range(size)]

    def evolve(self):
        for p in self.phenotypes:
            p.grow_seeds()
            p.paint_seeds()

    def __getitem__(self, key):
        """
        Returns phenotype's array
        """
        return self.phenotypes[key].arr


class Evolution:
    """
    Genetic programming over images
    """

    def __init__(self, params_window, main_window, reference_image):
        self.params_window = params_window
        self.main_window = main_window
        self.ref_img = Image.open(reference_image).convert('RGBA')
        self.ref_img_arr = np.array(self.ref_img)
        self.population = Population(params_window.population_size, self.ref_img_arr, params_window.min_seeds, params_window.max_seeds)
        self.start_evolution()

    def fitness_hist(self, arr1, arr2):
        """
        Calculates fitness based on histograms
        """
        bin_counts1, _ = np.histogram(arr1.ravel(), bins=256, range=(0, 254))
        bin_counts2, _ = np.histogram(arr2.ravel(), bins=256, range=(0, 254))
        fitness = np.sum(np.absolute(np.subtract(bin_counts1, bin_counts2)))
        return fitness

    def cross2phenos(self, p1, p2):
        ...

    def crossover(self):
        for i in range(int(self.params_window.population_size*(self.params_window.crossover_percentage/100))):
            i2 = randint(0, self.params_window.population_size-1)
            if i2 == i: # Just skip if its the same one
                continue 
            self.cross2phenos(self.fits[i], self.fits[i2])

    def start_evolution(self):
        """
        Main evolution cycle, takes parameters from params_window directly
        """
        self.img_arr = np.zeros_like(self.ref_img_arr)
        self.display_image(self.img_arr)
        params = self.params_window
        for iter in range(params.iterations):
            self.population.evolve()
            self.fits = [(self.fitness_hist(x, self.ref_img_arr), x) for x in self.population]
            self.fits.sort(key=lambda x: x[0])
            self.crossover()
            if (iter+1) % (params.iterations * (params.update_freq/100)) == 0:
                print("Best fitness: {}".format(self.fits[0][0]))
            
        self.display_image(self.fits[0][1])
        print("Fitness: {}".format(self.fitness_hist(self.img_arr, self.ref_img_arr)))
        

    def save_image(self, path):
        img_s = Image.fromarray(self.img_arr, 'RGBA')
        img_s.save(path, 'png')

    def display_image(self, img):
        qim = ImageQt(Image.fromarray(img, 'RGBA'))
        pix = QtGui.QPixmap.fromImage(qim)
        self.main_window.display_image(pix)