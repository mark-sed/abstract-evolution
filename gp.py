import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
import random

class Evolution():
    """
    Genetic programming over images
    """

    def __init__(self, params_window, main_window, reference_image):
        self.params_window = params_window
        self.main_window = main_window
        self.ref_img = Image.open(reference_image).convert('RGBA')
        self.ref_img_arr = np.array(self.ref_img)
        self.start_evolution()

    def start_evolution(self):
        """
        Main evolution cycle, takes parameters from params_window directly
        """
        img = np.zeros_like(self.ref_img_arr)
        self.display_image(img)
        params = self.params_window
        for iter in range(params.iterations):
            if iter % (params.iterations//params.update_freq) == 0:
                print(iter)
                for x in img:
                    for y in x:
                        y[0] = random.randint(0, 255)
                        y[1] = random.randint(0, 255)
                        y[2] = random.randint(0, 255)
                        y[3] = 255
                self.display_image(img)


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