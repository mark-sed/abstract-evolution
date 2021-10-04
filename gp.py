import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
import random


class Phenotype:
    """
    Phenotype of potential image
    """

    def __init__(self, ref_arr):
        self.arr = np.zeros_like(ref_arr)


class Population:
    """
    Population of phenotypes
    """

    def __init__(self, size, ref_arr):
        self.size = size
        self.ref_arr = ref_arr


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
        self.start_evolution()

    def fitness_hist(self, arr1, arr2):
        """
        Calculates fitness based on histograms
        """
        bin_counts1, _ = np.histogram(arr1.ravel(), bins=256, range=(0, 254))
        bin_counts2, _ = np.histogram(arr2.ravel(), bins=256, range=(0, 254))
        fitness = np.sum(np.absolute(np.subtract(bin_counts1, bin_counts2)))
        return fitness

    def start_evolution(self):
        """
        Main evolution cycle, takes parameters from params_window directly
        """
        self.img_arr = np.zeros_like(self.ref_img_arr)
        self.display_image(self.img_arr)
        params = self.params_window
        for iter in range(params.iterations):
            if (iter+1) % (params.iterations * (params.update_freq/100)) == 0:
                print(iter)
                for x in self.img_arr:
                    for y in x:
                        y[0] = random.randint(0, 255)
                        y[1] = random.randint(0, 255)
                        y[2] = random.randint(0, 255)
                        y[3] = 255
                self.display_image(self.img_arr)
        print("Fitness: {}".format(self.fitness_hist(self.img_arr, self.ref_img_arr)))
        

    def save_image(self, path):
        img_s = Image.fromarray(self.img_arr, 'RGBA')
        img_s.save(path, 'png')

    def display_image(self, img):
        #for x in img:
        #    for y in x:
        #        y[0] = 255
        #        y[1] = 255
        #        y[2] = 0
        #        y[3] = 255
        qim = ImageQt(Image.fromarray(img, 'RGBA'))
        pix = QtGui.QPixmap.fromImage(qim)
        self.main_window.display_image(pix)