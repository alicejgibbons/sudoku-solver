# Sudoku Solver

A sudoku solver that uses Donald Knuth's [Dancing Links](<https://en.wikipedia.org/wiki/Dancing_Links>) technique to implement his Algorithm X. Algorithm X is a procedure used to find all solutions to the exact cover problem. In order to represent a sudoku grid as an exact covering problem, the grid must be transformed into a binary matrix that holds the necessary constraints of a sudoku puzzle. The data structures in dataStructures.py were used for this purpose.

Usage: python sudokuToDL.py 3 400000805030000000000700000020000060000080400000010000000603070500200000104000000
