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


class Phenotype:
    """
    Phenotype of potential image
    """

    # List of colors used by other phenotypes
    CLOSED_LIST = []

    def __init__(self, ref_arr, randomize_colors=True, unique_colors=False):
        """
        Constructor
        :param ref_arr Reference image as an numpy array used for fitness
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


class Population:
    """
    Population of phenotypes
    """

    def __init__(self, size, ref_arr, randomize_colors, unique_colors):
        """
        Constructor
        :param size How many phenotypes will there be in one population
        :param ref_arr Reference image as an array used for the fitness
        :param randomize_colors If True color of the phenotype will be picked at random
                                otherwise values will be extracted from the reference image
        :param unique_colors If True then no 2 phenotypes will have the same color
        """
        self.size = size
        self.ref_arr = ref_arr
        self.phenotypes = [Phenotype(self.ref_arr, randomize_colors, unique_colors) for _ in range(size)]

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
        self.population = Population(params_window.population_size, self.ref_img_arr, params_window.randomize_colors, params_window.unique_colors)

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