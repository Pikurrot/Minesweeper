# Minesweeper solver
This project consists of a program that creates and automatically solves a Minesweeper board, using 4 different algorithms.

**DISCLAIMER**: I've not solved the P=NP problem, the algorithm in this program uses randomness as a last resort (no guarantee to find the solution).

![Minesweeper](https://i.giphy.com/media/lPX3G4r1evdXa34qb4/giphy.gif)

## Repository files:
- Minesweeper.py : The main program, in python.
- Images/ : Folder containing all necessary images for the main program.\
\
(Minesweeper.py and Images/ must have the same path or be in the same folder!)
## The program:
### Parameters
-Difficulty: Default is 0.15 (Moderate). It's the density of mines in the board. With difficluty ≤ 0.15 the solution will almost always be found.\
-Map size (x,y): Default is 30x30 (Medium size).\
-Random seed: randomly generated seed for random generation of the board (you can set it to whatever you want).
### The 4 algorithms
As the Minesweeper game is an NP-complete problem (it has no efficient solution algorithm), I have designed 4 algorithms that work for almost all situations, but, if the complexity is too high and none of the four is useful there, it will guess randomly, which may result in exploding a mine.
#### 1st algorithm
For each tile A, if the number of unknown tiles neighboring tile A is equal to the number of tile A, then all those tiles will be flagged.\
![1st algorithm](/Readme_images/1st_algorithm.png)
#### 2nd algorithm
For each tile A, if the number of flag tiles neighboring tile A is equal to the number of that tile and tile A still has unknown neighbor tiles, then all those tiles will be shown.\
![2nd algorithm](/Readme_images/2nd_algorithm.png)
#### 3rd algorithm
For a tile A, if the difference between the tile number and the number of nearby flags is 1 (or simply the number of tile A is 1), if all its neighboring unknown tiles coincide with a part of the neighboring unknown tiles of a tile B (which is a neighboring number of any of the neighboring unknown tiles of tile A), and the difference between the number of tile B and the number of flags near it is 1 (or simply the number of tile B is 1), then, the other unknown neighboring tiles of tile B can be shown.\
In the example below, tile A is the 2 in the third row, and tile B is the 1 in the fourth row.\
![3rd algorithm](/Readme_images/3rd_algorithm.png)
#### 4th algorithm
This algorithm focuses on a region of the board where there is a group of unknown tiles together and none of the previous three algorithms is useful. For a tile A from around this group, it checks every possibility where the mine may be in its unknown neighboring tiles. It then uses the other three algorithms to determine where there are mines and where there are no mines in that region in each possibility. Finally, it checks in each possibility if the numbers of the tiles around the region match the number of its neighboring flags, in this case, that possibility will be the correct one.
![4th algorithm](/Readme_images/4rd_algorithm.png)
