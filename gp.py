import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
import random
from random import randint
from copy import deepcopy


class Phenotype:
    """
    Phenotype of potential image
    """

    def __init__(self, ref_arr):
        self.arr = np.zeros_like(ref_arr)
        pixel = [randint(0, 255), randint(0, 255), randint(0, 255), 255]
        for i in range(len(self.arr)):
            for a in range(len(self.arr[0])):
                self.arr[i][a] = pixel

class Population:
    """
    Population of phenotypes
    """

    def __init__(self, size, ref_arr):
        self.size = size
        self.ref_arr = ref_arr
        self.phenotypes = [Phenotype(self.ref_arr) for _ in range(size)]

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
        self.population = Population(params_window.population_size, self.ref_img_arr)

    def fitness_hist(self, arr1, arr2):
        """
        Calculates fitness based on histograms
        """
        bin_counts1, _ = np.histogram(arr1.ravel(), bins=256, range=(0, 254))
        bin_counts2, _ = np.histogram(arr2.ravel(), bins=256, range=(0, 254))
        fitness = np.sum(np.absolute(np.subtract(bin_counts1, bin_counts2)))
        return fitness

    def cross2phenos(self, p1, p2):
        n1 = deepcopy(p1)
        n2 = p2
        start_x = randint(0, len(p2.arr)-2)
        start_y = randint(0, len(p2.arr[0])-2)
        end_x = randint(start_x, len(p2.arr)-1)
        end_y = randint(start_y, len(p2.arr[0])-1)
        # TODO: Do i need deepcopy?
        n1.arr[start_x:end_x,start_y:end_y] = n2.arr[start_x:end_x,start_y:end_y]
        return n1

    def crossover(self):
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
        for iter in range(params.iterations):
            self.fits = [(self.fitness_hist(x.arr, self.ref_img_arr), x, c) for c, x in enumerate(self.population.phenotypes)]
            self.fits.sort(key=lambda x: x[0])
            self.crossover()
            if (iter+1) % (params.iterations * (params.update_freq/100)) == 0:
                print("Best fitness: {}".format(self.fits[0][0]))
            
        best = self.fits[0][1].arr
        self.display_image(best)
        print("Fitness: {}".format(self.fitness_hist(best, self.ref_img_arr)))
        

    def save_image(self, path):
        img_s = Image.fromarray(self.img_arr, 'RGBA')
        img_s.save(path, 'png')

    def display_image(self, img):
        qim = ImageQt(Image.fromarray(img, 'RGBA'))
        pix = QtGui.QPixmap.fromImage(qim)
        self.main_window.display_image(pix)