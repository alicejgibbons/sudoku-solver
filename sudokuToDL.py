#!/usr/bin/env python2.7

"""
Alice Gibbons
December 2015

A sudoku solver that uses Donald Knuth's "Dancing Links" technique to implement his Algorithm X.
<https://en.wikipedia.org/wiki/Dancing_Links>

Usage: python sudokuToDL.py 3 400000805030000000000700000020000060000080400000010000000603070500200000104000000
"""

import sys
import time
from dataStructures import SparseMatrix

class DancingLinks(object):

	def __init__(self, matrix):
		self.matrix = matrix
		self.soln = [0] * (len(self.matrix.columns) - 1)
		self.head = self.matrix.column_header
  
  	"""To minimize branching factor while backtracking choose the column with 
  	 the smallest number of 1's"""
	def choose_col(self):
		smallest_size = sys.maxint		#set smallest size to be infinty
		head = self.head

		j = head.right
		col_choice = None

		while j != head:
			if j.size < smallest_size:
				col_choice = j
				smallest_size = j.size
			j = j.right

		return col_choice

    	""" Implementation of Knuth's recursive procedure search(k)"""
  	def search(self, k=0):
	    if self.head.right == self.head:		# only one header node, matrix is empty or contains only 0's
	    	return self.soln

	    col = self.choose_col()				# choose the "most constrained" column left in the matrix
	    self.matrix.cover(col)				# cover column

	    row = col.down				
	    while row != col:					# iterate over all the nodes (matrix[row][col] = 1)
			self.soln[k] = row 								

			j = row.right 					
			while j != row:
				self.matrix.cover(j.column)
				j = j.right

			cont = self.search(k+1)
			if cont: return cont

			row = self.soln[k]		#backtrack here
			col = row.column 		

			j = row.left 			
			while j != row:
				self.matrix.uncover(j.column)
				j = j.left

			row = row.down			

	    self.matrix.uncover(col)
	    return None			#cannot continue any further so return 


"""Create a binary grid out of a 9x9 sudoku board"""
def create_dl_matrix(sudoku_grid):
	dl_matrix = []
	for r in range(0,9):
		for c in range(0,9):
			dl_matrix += create_dl_rows(r, c, sudoku_grid[r][c])

	return dl_matrix

"""Given a single square in a sudoku grid create all the possible rows in the binary 
 matrix that satisfy the conditions; Returns multiple rows if the number is 0, 
 one row if the number is not"""
def create_dl_rows(r, c, n):
	if n in range(1,10):	# number is a given clue in the sudoku grid so return only the one row
		return [ create_dl_row(r, c, n) ]
	else:					# number is a zero in sudoku grid so create row for each of the 9 possibilities
		return map( (lambda(n): create_dl_row(r, c, n)), range(1,10))

"""Create a single row of length 324, for one of the four types of constraints"""
def create_dl_row(r, c, n):
	b = (r - (r % 3)) + (c / 3)	#the box number that contains the row and column index
	n -= 1		#to account for 0 indexing
	return create_quarter_row(r, c) + create_quarter_row(r, n) + create_quarter_row(c, n) + create_quarter_row(b, n) 

"""Create a quarter section of a single row (81 columns) corresponding to 
 one of the four constraints"""
def create_quarter_row(num1, num2):
	quarter_row = [0] * 81
	quarter_row [ num1 * 9 + num2 ] = 1
	return quarter_row

"""Given a single solution row in the completed sparse matrix, pull out the 
associatied sudoku grid values from it"""
def condense_row(row):
	rc = row[ 0:81 ]
	rn = row[ 81:162 ]

	r, c = condense_quarter_row(rc)
	b, n = condense_quarter_row(rn)
	n += 1		#to account for 0-indexing
	return (r, c, n)

"""Given a quarter row complying to one of the four constraints, pull out the
 two numbers that set the constraint (from the position of the 1)"""
def condense_quarter_row(quarter_row):
	pos = quarter_row.index(1)
	num1 = pos / 9
	num2 = pos % 9
	return (num1, num2)

"""Print out the matrix"""
def print_sudoku_grid(grid, is_solved):
	if not is_solved:
		print "Unsolved sudoku grid: "
	else:
		print "Solved sudoku grid: "
	for r in grid:
		for num in r:
			print num, " ",
		print 
	print


"""Input: list of 81 items corresponding to an unsolved sudoku grid with 0's 
 as place holders for empty spaces
 Output: solved sudoku grid if board is solvable; Warning message if not """
def main():
	start_time = time.clock()
	sudoku_size = 0
	sudoku_grid = ""

	try:
		sudoku_size = int(sys.argv[1])
		grid_size = (sudoku_size**2)
		sudoku_grid = [[-1] * grid_size, [-1] * grid_size, [-1] * grid_size, [-1] * grid_size, [-1] * grid_size, [-1] * grid_size, [-1] * grid_size, [-1] * grid_size, [-1] * grid_size]
		input_grid = str(sys.argv[2])

		for i in range(grid_size):
			for j in range(grid_size):
				sudoku_grid[i][j] = int(input_grid[i*(grid_size) + j])
		print_sudoku_grid(sudoku_grid, 0)

	except IndexError:
		print "usage: sudokuToDL.py 3 400000805030000000000700000020000060000080400000010000000603070500200000104000000"
		sys.exit(2)

  	binary_matrix_rows = create_dl_matrix(sudoku_grid)	# create binary matrix from grid
  	sparse_matrix = SparseMatrix(binary_matrix_rows)	# transform binary matrix to sparse matrix

  	dl = DancingLinks(sparse_matrix)					
  	dl_soln = dl.search()								# find the row numbers that correspond to an exact covering

  	if dl_soln:			# an exact covering of the binay matrix exists 
  		dl_soln_rows = [node.row_ind for node in dl_soln if node]		
  		dl_matrix_soln = [binary_matrix_rows[r] for r in dl_soln_rows] 	# get binary rows in exact covering

  		condensed_soln = map(condense_row, dl_matrix_soln)		# transform binary rows back to constraint numbers
  		final_soln = [[0] * 9, [0] * 9, [0] * 9, [0] * 9, [0] * 9, [0] * 9, [0] * 9, [0] * 9, [0] * 9]
  		for r,c,num in condensed_soln:
  			final_soln[r][c] = num

  		print_sudoku_grid(final_soln, 1)

  	else:			# no exact covering exists
  		print "This sudoku grid has no solution!"
 	
 	end_time = time.clock()
 	total_time = end_time - start_time
 	print "Total time: ",  total_time

if __name__ == "__main__": main()
