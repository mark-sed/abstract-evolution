#!/usr/bin/python3
"""
VIN project
Uses genetic programming to evolve image into passes in image,
generating similar images
"""
__author__ = "Marek Sedlacek (xsedla1b)"
__date__ = "September 2021"
__version__ = "0.1.0"
__email__ = ("xsedla1b@fit.vutbr.cz", "mr.mareksedlacek@gmail.com")


import PyQt5
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QAction,
                             QPushButton,
                             QFileDialog,
                             QLabel,
                             QLineEdit,
                             QFormLayout,
                             QSlider, 
                             QCheckBox,
                             QProgressBar,
                             QComboBox)
from PyQt5.QtGui import (QPixmap,
                         QIntValidator)
import gp

# TODO: Make another and new evolution work
# TODO: Language support - EN, CZ, FR
# TODO: About menu possibly with help (describe what this is and some tips on what stuff does)
# TODO: Icon/Logo
# TODO: Documentation
# TODO: Add (?) mouseover to params so people know what it does and if more or less is better
class MainWindow(QMainWindow):
    """
    Main program windows
    """

    def __init__(self, width, height):
        super(MainWindow, self).__init__()
        #self.resize(width, height)
        self.setFixedSize(width, height)
        # Center the screen
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center = QApplication.desktop().screenGeometry(screen).center()
        self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)
        self.evolution_params = EvolutionParams(self)
        self.reference_image = None
        self.image_label = QLabel(self)
        self.original_image_label = QLabel(self)
        self.save_image_button = QPushButton("Save", self)
        self.save_image_button.pressed.connect(self.save_image)
        self.save_image_button.hide()
        self.current_displyed_image = None
        self.evolve_another_button = QPushButton("Evolve new", self)
        self.evolve_another_button.pressed.connect(self.evolve_new)
        self.evolve_another_button.hide()
        self.evolve_again_button = QPushButton("Evolve again", self)
        self.evolve_again_button.pressed.connect(self.evolve_again)
        self.evolve_again_button.hide()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(0, 0, 400, 25)
        self.progress_bar.move(self.width()//2-self.progress_bar.width()//2, self.height()-200)
        self.please_wait_label = QLabel("In silico evolution might take a few minutes...", self)
        self.please_wait_label.adjustSize()
        self.please_wait_label.move(self.width()//2-self.please_wait_label.width()//2, self.progress_bar.y()-self.please_wait_label.height()-5)
        self.initUI()
    
    def initUI(self):
        """
        Initialize UI
        """
        self.setWindowTitle("Abstract Evolution")
        
        # Adding a menu bar
        self.menuBar().clear()
        self.menu_bar = self.menuBar()
        self.mb_file = self.menu_bar.addMenu("File")

        # Setting up File menu bar
        # Upload image
        self.mb_upload_image = QAction("Upload image")
        self.mb_file.addAction(self.mb_upload_image)
        self.mb_upload_image.triggered.connect(self.upload_image)

        # Evolution params
        self.mb_evolution_params = QAction("Evolution parameters")
        self.mb_file.addAction(self.mb_evolution_params)
        self.mb_evolution_params.triggered.connect(lambda: self.evolution_params.show())

        # Quit
        self.mb_quit = QAction("Quit")
        self.mb_file.addAction(self.mb_quit)
        self.mb_quit.triggered.connect(lambda: app.exit())

        # Upload image button in the middle of the windows when nothing is open
        self.button_upload_image = QPushButton("Upload image", self)
        self.button_upload_image.resize(200, 50)
        self.button_upload_image.move(self.width() // 2 - self.button_upload_image.width() // 2,
                                      self.height() // 2 - self.button_upload_image.height() // 2)
        self.button_upload_image.pressed.connect(self.upload_image)

        # Hide progress
        self.progress_bar.hide()
        self.please_wait_label.hide()

        # Show the window
        self.show()

    def upload_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select file to evolve into", "","Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if fileName:
            self.reference_image = fileName
            self.evolution_params.show()

    def display_image(self, image):
        self.current_displyed_image = image
        # Resize window
        buttons_width = 5 + self.save_image_button.width() + 5 + self.evolve_again_button.width() + 5 + self.evolve_again_button.width() + 5
        min_width = image.width()*2+15 if image.width()*2+15 > buttons_width else buttons_width
        
        #self.resize(min_width, image.height()+10 + self.save_image_button.height() + 5)
        self.setFixedSize(min_width, image.height()+10 + self.save_image_button.height() + 5)
        # Hide extra gui
        self.button_upload_image.hide()
        self.menu_bar.hide()
        # Display the image
        self.image_label.setPixmap(image)
        self.image_label.resize(image.width(), image.height())
        self.image_label.move(5, 5)

        self.original_image_label.setPixmap(QPixmap(self.reference_image))
        self.original_image_label.resize(image.width(), image.height())
        self.original_image_label.move(5+5+image.width(), 5)
        
        # Display save
        # Button will be shown when image is fully rendered
        self.save_image_button.move(self.width() - self.save_image_button.width() - 5,
                                    self.height() - self.save_image_button.height() - 5)

        # Display evolve again
        self.evolve_again_button.move(self.width() - self.save_image_button.width() - 5*2 - self.evolve_again_button.width(),
                                      self.height() - self.save_image_button.height() - 5)

        # Display evolve new
        self.evolve_another_button.move(self.width() - self.save_image_button.width() - 5*3 - self.evolve_again_button.width() - self.evolve_another_button.width(),
                                        self.height() - self.save_image_button.height() - 5)

        self.progress_bar.setGeometry(5, self.evolve_another_button.y()+2, self.evolve_another_button.x()-10, self.evolve_another_button.height()-4)
        self.progress_bar.repaint()
        self.please_wait_label.move(self.evolve_another_button.x()+5, self.evolve_another_button.y()+self.evolve_another_button.height()//2-self.please_wait_label.height()//2)
        self.repaint()

    def update_progress(self, v):
        if type(v) == str:
            self.please_wait_label.hide()
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat(v)
            self.save_image_button.show()
            self.evolve_again_button.show()
            self.evolve_another_button.show()
        else:
            self.please_wait_label.show()
            self.progress_bar.setValue(v)
        self.please_wait_label.repaint()
        self.progress_bar.show()
        

    def save_image(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save image', "evolved-painting.png")
        if name is not None and len(name) > 0:
            self.evolution_params.curr_evolution.save_image(name)

    def evolution_running(self):
        self.button_upload_image.setEnabled(False)
        self.mb_file.setEnabled(False)

    def evolve_new(self):
        ...

    def evolve_again(self):
        ...
            

class EvolutionParams(QMainWindow):
    """
    Window containing sliders and buttons for evolution param settings
    """
    # TODO: Determine the values based on the image size

    def __init__(self, parent=None):
        super(EvolutionParams, self).__init__(parent)
        self.set_defaults()
        self.parent = parent
        self.setWindowTitle("Evolution parameters")
        #self.resize(600, 400)
        # Remove maximize and minimize button
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMinimizeButtonHint)
        # Center the screen
        #self.setMinimumWidth(EvolutionParams.MIN_WIDTH)
        #self.setMaximumWidth(EvolutionParams.MAX_WIDTH)
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center = QApplication.desktop().screenGeometry(screen).center()
        self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)

        # Input form
        self.form_layout = QFormLayout()

        # Iterations
        self.input_iterations = QLineEdit()
        it_validator = QIntValidator()
        it_validator.setBottom(1)
        self.input_iterations.setValidator(it_validator)
        self.input_iterations.show()
        self.input_iterations.textChanged.connect(self.changed_iterations)
        self.form_layout.addRow("Iterations", self.input_iterations)

        # Population size
        self.input_population_size = QLineEdit()
        ps_validator = QIntValidator()
        ps_validator.setBottom(1)
        self.input_population_size.setValidator(ps_validator)
        self.input_population_size.show()
        self.input_population_size.textChanged.connect(self.changed_population_size)
        self.form_layout.addRow("Population size", self.input_population_size)

        # Randomize colors
        self.input_randomize_colors = QCheckBox()
        self.input_randomize_colors.toggled.connect(self.changed_randomize_colors)
        self.form_layout.addRow("Random colors", self.input_randomize_colors)

        # Unique colors
        self.input_unique_colors = QCheckBox()
        self.input_unique_colors.toggled.connect(self.changed_unique_colors)
        self.form_layout.addRow("Unique colors", self.input_unique_colors)

        # Elitism
        self.input_elitism = QCheckBox()
        self.input_elitism.toggled.connect(self.changed_elitism)
        self.form_layout.addRow("Elitism", self.input_elitism)

        # Crossover percentage
        self.input_crossover_percentage = QSlider(Qt.Horizontal)
        self.input_crossover_percentage.setSingleStep(10)
        self.input_crossover_percentage.setMinimum(1)
        self.input_crossover_percentage.setMaximum(100)
        self.input_crossover_percentage.valueChanged[int].connect(self.changed_crossover_percentage)
        self.input_crossover_percentage_label = QLabel("Crossover 50 %")
        self.form_layout.addRow(self.input_crossover_percentage_label, self.input_crossover_percentage)

        # Fitness function
        self.input_fitness_fun = QComboBox()
        self.input_fitness_fun.addItem("CH (Color histogram)")
        self.input_fitness_fun.addItem("RPM (Random point match)")
        self.input_fitness_fun.addItem("UPM (Uniform point match)")
        self.input_fitness_fun.currentIndexChanged.connect(self.changed_fitness_fun)
        self.form_layout.addRow("Fitness function", self.input_fitness_fun)

        # PM values
        self.input_pm_amount = QLineEdit()
        pma_validator = QIntValidator()
        pma_validator.setRange(1, 1000000)
        self.input_pm_amount.setValidator(pma_validator)
        self.input_pm_amount.textChanged.connect(self.changed_pm_amount)
        self.form_layout.addRow("Amount of points", self.input_pm_amount)
        self.input_pm_amount.setEnabled(False)


        self.input_pm_size = QLineEdit()
        pms_validator = QIntValidator()
        pms_validator.setRange(1, 100000)
        self.input_pm_size.setValidator(pms_validator)
        self.input_pm_size.textChanged.connect(self.changed_pm_size)
        self.form_layout.addRow("Point size", self.input_pm_size)
        self.input_pm_size.setEnabled(False)

        # Update frequency
        self.input_update_freq = QSlider(Qt.Horizontal)
        self.input_update_freq.setSingleStep(5)
        self.input_update_freq.setMinimum(1)
        self.input_update_freq.setMaximum(100)
        #self.input_update_freq.setValidator(QIntValidator(1, 100))
        #self.input_update_freq.show()
        self.input_update_freq.valueChanged[int].connect(self.changed_update_freq)
        self.input_update_freq_label = QLabel("Update image every 10 %")
        self.form_layout.addRow(self.input_update_freq_label, self.input_update_freq)

        # Set values
        self.set_input_defaults()

        # Set defaults
        self.defaults_button = QPushButton("Set defaults", self)
        self.defaults_button.pressed.connect(self.button_set_defaults)
        #self.defaults_button.move(self.width() - self.defaults_button.width() - 10*2 - self.ok_button.width(),
        #                          self.height() - self.defaults_button.height() - 10)
        self.form_layout.addRow(self.defaults_button)

        # Ok button
        self.ok_button = QPushButton("OK", self)
        self.ok_button.pressed.connect(self.ok_pressed)
        #self.ok_button.move(self.width() - self.ok_button.width() - 10,
        #                    self.height() - self.ok_button.height() - 10)
        self.form_layout.addRow(self.ok_button)

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(self.form_layout)
        self.update()

    def initUI(self):
        ...

    def set_defaults(self):
        self.iterations = 100
        self.update_freq = 10
        self.population_size = 10
        self.randomize_colors = False
        self.unique_colors = False
        self.elitism = True
        self.crossover_percentage = 50
        self.fitness_fun = 0
        self.pm_amount = 100
        self.pm_size = 3

    def set_input_defaults(self):
        self.input_iterations.setText(str(self.iterations))
        self.input_update_freq.setValue(self.update_freq)
        self.input_update_freq_label.setText("Update image every {} %".format(self.update_freq))
        self.input_population_size.setText(str(self.population_size))
        self.input_elitism.setChecked(self.elitism)
        self.input_randomize_colors.setChecked(self.randomize_colors)
        self.input_unique_colors.setChecked(self.unique_colors)
        self.input_crossover_percentage.setValue(self.crossover_percentage)
        self.input_crossover_percentage_label.setText("Crossover {} %".format(self.crossover_percentage))
        self.input_fitness_fun.setCurrentIndex(self.fitness_fun)
        self.input_pm_amount.setText(str(self.pm_amount))
        self.input_pm_size.setText(str(self.pm_size))

    def button_set_defaults(self):
        self.set_defaults()
        self.set_input_defaults()

    def ok_pressed(self):
        self.hide()
        if self.parent.reference_image is not None:
            print("Starting evolution with image "+self.parent.reference_image)
            self.parent.evolution_running()
            self.parent.repaint()
            self.parent.update_progress(0)
            self.curr_evolution = gp.Evolution(self, self.parent, self.parent.reference_image)
            self.curr_evolution.start_evolution()

    def changed_randomize_colors(self):
        self.randomize_colors = not self.randomize_colors

    def changed_unique_colors(self):
        self.unique_colors = not self.unique_colors

    def changed_elitism(self):
        self.elitism = not self.elitism

    def changed_fitness_fun(self, v):
        self.fitness_fun = v
        if v == 1 or v == 2:
            self.input_pm_amount.setEnabled(True)
            self.input_pm_size.setEnabled(True)
        else:
            self.input_pm_amount.setEnabled(False)
            self.input_pm_size.setEnabled(False)

    def changed_pm_amount(self, v):
        self.pm_amount = self.check_input_change(self.input_pm_amount, v, int, 1, 1_000_000)

    def changed_pm_size(self, v):
        self.pm_size = self.check_input_change(self.input_pm_size, v, int, 1, 100_000)

    def changed_crossover_percentage(self, v):
        self.crossover_percentage = v
        self.input_crossover_percentage_label.setText("Crossover {} %".format(self.crossover_percentage))

    def changed_update_freq(self, v):
        self.update_freq = v
        self.input_update_freq_label.setText("Update image every {} %".format(self.update_freq))

    def changed_iterations(self, v):
        self.iterations = self.check_input_change(self.input_iterations, v, int, 1, 1_000_000_000)

    def changed_min_seeds(self, v):
        self.min_seeds = self.check_input_change(self.input_min_seeds, v, int, 1, self.max_seeds)

    def changed_max_seeds(self, v):
        self.max_seeds = self.check_input_change(self.input_max_seeds, v, int, self.min_seeds, 1000)

    def changed_population_size(self, v):
        self.population_size = self.check_input_change(self.input_population_size, v, int, 1, 1_000_000)

    def check_input_change(self, component, value, cast, min, max):
        if len(value) == 0:
            component.setText(str(min))
            return min
        value = cast(value)
        if value < min:
            component.setText(str(min))
            return min
        if value > max:
            component.setText(str(max))
            return max
        return value


def simulate_open(win, file):
    win.reference_image = file
    win.evolution_params.ok_pressed() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    win = MainWindow(1024, 600)
    
    if len(sys.argv) > 1:
        simulate_open(win, sys.argv[1])

    sys.exit(app.exec_())