# Minesweeper solver
This project consists of a program that creates and automatically solves a Minesweeper board, using 4 different algorithms.

![Minesweeper](https://i.giphy.com/media/lPX3G4r1evdXa34qb4/giphy.gif)

## Repository files:
- Minesweeper.py : The main program, in python.
- Images/ : Folder containing all necessary images for the main program.\
\
(Minesweeper.py and Images/ must have the same path or be in the same folder!)
## The program:
### Parameters
-Difficulty: Default is 0.15 (Moderate). It's the density of mines in the board. More than 0.15 is not guaranteed full resolution.\
-Map size (x,y): Default is 30x30 (Medium size).\
-Random seed: randomly generated seed for random generation of the board. A random seed has no sense, but you can change it to whatever you want.
### The 4 algorithms
As the Minesweeper game is an NP-complete problem (it has no efficient solution algorithm), I have designed 4 algorithms that work for almost all situations, but, if the complexity is too high and none of the four is useful there, it will guess randomly, which may result in exploding a mine.
#### 1st
***Still to be edited***
