<img align="left" width="40" height="40" src="https://raw.githubusercontent.com/mark-sed/abstract-evolution/master/icon.png" alt="Icon">

# Abstract Evolution

Abstract Evolution is a program for generating abstract computer art using genetic programming.  

This program takes reference image into which it tries to evolve itself, creating abstract versions of reference image. Output of this program will always be different and the artist is the one who controls its parameters. This is not a photo filter app, outputs migth come out messy, too abstract or totally different based on the evolution parameters.  

The program is quite suited to create other variations of abstract art (might be a good tool to transform your own art).

![Image example 1](https://github.com/mark-sed/abstract-evolution/blob/master/example_outputs/evolved_ae_v0-1-0-kandinsky.png?raw=true)  
![Image example 1](https://github.com/mark-sed/abstract-evolution/blob/master/example_outputs/evolved_ae_v0-1-0.png?raw=true)  

But it also might be used with photos, where the longer the evolution runs the generally more defined the objects might be (depending on the fitness function - see wiki).

![Image example 1](https://github.com/mark-sed/abstract-evolution/blob/master/example_outputs/evolved_ae_v0-1-0-jlaw1.png?raw=true)
![Image example 1](https://github.com/mark-sed/abstract-evolution/blob/master/example_outputs/evolved_ae_v0-1-0-jlaw3.png?raw=true)  
![Image example 1](https://github.com/mark-sed/abstract-evolution/blob/master/example_outputs/evolved_ae_v0-1-0-vilda.png?raw=true)

The evolution itself migth take a very long time for big scale images so keep that in mind and it is encouraged to first try the program on smaller images (you can use examples from the `/example_inputs` folder) to get to know the program and then evolve bigger pieces.  

Use this tool to any extend you'd like to, generate references to your own paitings, edit the output to be more aesthetic or just simply try to evolve your reference until it is what you want it to be (even though this might take a long time).  

_Randomness plays big part in this, but luck of the draw is there always when it comes to art, here it's just more aplified._

## Installation

Download the whole repository - `git clone` or using the download button in GitHub (Green button "Code" -> "Download ZIP"). 

Required Python libraries can be installed using the `install.sh` script (`sh install.sh`) or using `requirements.txt` (`pip install -r requirements.txt`).

* Python3 and following packages:
  * PyQT5
  * Pillow (PIL)
  * Numpy

## Running the program

To run the program on POSIX system simply use the `run.sh` script (`sh run.sh`).  
Or universally run it using Python 3 - `python3 abstract_evolution.py`

The program might seem to be frozen at times and the OS might offer you to kill the program, this is not yet fixed issue. The evolution is happening (best option is to run the program from terminal and then see if any error happened).

## Wiki

To get to know the program better have a look into the [Abstract evolution's wiki](https://github.com/mark-sed/abstract-evolution/wiki)

## Examples

In the `/example_inputs` folder are some known fine art pieces to try to evolve into (make their variations). Also picture of a lovely cat to try the program on real pictures.  
These are there just for the convenience to test the program out, it's always better to use your own reference images and setting up the evolution parameters just right to make something new and unique.  
In the `/example_outputs` are some of the program outputs (screenshots) that are also used in this readme file.

## Languages

The program has currently language support for following languages:
* English
* Čeština (Czech)
* Français (French) - Peut-être qu'il y a des erreurs, désolé.

# Patch notes

## 0.2.1
_3/11/2021_
* Quick parameters setup
* Configuration parameters can now be saved and loaded
* Added logo (create by the app itself)
* Changed reference and output image positions to make it more clear what is the output.
* Added license.
* Added about text.
* Minor GUI fixes

## 0.1.0
_19/10/2021_