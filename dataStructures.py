#!/usr/bin/env python2.7

"""
Alice Gibbons
December 2015

SparseMatrix based off of: https://github.com/teamKandR/narorumo-backup/blob/master/sudokusolver/sudokudlx/sparsematrix.py
"""

"""Node object: represents each element in the sparse matrix with a value of 1"""
class Node(object):
	def __init__(self, row_ind, col_ind):
		self.left = self		# L[x]
		self.right = self		# R[x]
		self.up = self			# U[x]
		self.down = self		# D[x]
		self.column = None		# C[x]

		self.row_ind = row_ind
		self.col_ind = col_ind

"""Column object: represents a column in the sparse matrix, 
 connects the columns when they have no overlapping rows"""
class ColumnObj(object):
	def __init__(self, name, is_head = 0):
		self.left = None		# L[x]
		self.right = None		# R[x]
		self.up = self			# U[x]
		self.down = self		# D[x]

		self.size = 0			# S[x]
		self.name = name 		# N[x]

"""	4-way linked Matrix containing a node for very element that is 1 in matrix
	Based of 
"""
class SparseMatrix(object):

	def __init__(self, rows_list):
		self.nodes = {}
		self.rows = rows_list

		for r in range(len(rows_list)):
			for c in range(len(rows_list[0])):
				if rows_list[r][c]:
					one = Node(r, c)
					self.nodes[(r,c)] = one

		#create sparse matrix
		col_ind = range(len(self.rows[0]))
		self.columns = map( lambda(index): ColumnObj(index), col_ind)
		self.column_table = {}
		self.column_header = ColumnObj('h', is_head = 1)
		self.columns.append(self.column_header)

		for col in self.columns:
			self.column_table[col.name] = col

		self.create_col_obj_links()
		self.create_row_links()
		self.create_col_links()

	"""Link together all the column objects in the adjacent columns"""
	def create_col_obj_links(self):
		prev = None
		first = None

		for c in self.columns:
			if not first:
				first = c
			elif prev:
				c.left = prev
				prev.right = c
			prev = c

		c.right = first
		first.left = c

	"""Link together all nodes (circularily) in the same row of sparse matrix"""
	def create_row_links(self):
		keys = self.nodes.keys()
		row_ind = [row_ind for (row_ind, col_ind) in keys]
		row_ind = list(set(row_ind))
		row_ind.sort()

		for r in row_ind:
			#col_ind = self.col_ind_for(r)
			col_ind = [col_ind for (row_ind,col_ind) in keys if row_ind == r]
			col_ind = list(set(col_ind))
			col_ind.sort()

			prev = None
			first = None
			for c in col_ind:
				node = self.nodes[(r,c)]

				if not first:
					first = node
				elif prev:
					node.left = prev
					prev.right = node
				prev = node

		  	node.right = first
		  	first.left = node

	"""Link together all nodes (circularily) in the same column of sparse 
	matrix with column objects at the top of each column"""
	def create_col_links(self):
		keys = self.nodes.keys()
		col_ind = [col_ind for (row_ind, col_ind) in keys]
		col_ind = list(set(col_ind))
		col_ind.sort()

		for c in col_ind:
			column = self.column_table[c]
			row_ind = [row_ind for (row_ind,col_ind) in keys if col_ind == c]
			row_ind == list(set(row_ind))
			row_ind.sort()

		  	column.size = len(row_ind)

			prev = None
			first = None
			for r in row_ind:
				node = self.nodes[(r,c)]
				node.column = column

				if not first:
				  	first = node
				elif prev:
				 	node.up = prev
				  	prev.down = node
				prev = node

			column.up = node
			node.down = column

			column.down = first
			first.up = column


	"""Implementation of Knuth's cover procedue: 
	 remove column object and column nodes from column c in the sparse matrix, along with 
	 all the associated row nodes in other column lists in the same rows as c 
	 (ie. add it to a partial solution)"""
	def cover(self, column):
		column.right.left = column.left
		column.left.right = column.right

		row = column.down
		while row != column:
		  node = row.right
		  while node != row:
		    node.down.up = node.up
		    node.up.down = node.down
		    node.column.size -= 1
		    node = node.right

		  row = row.down

	"""Implementation of Knuth's uncover procedue:
	 restore a column object and column nodes to column c in the sparse matrix, along with 
	 all of the associated row nodes to the column lists that they were in 
	 (ie. remove it from a partial solution)"""
	def uncover(self, column):
		row = column.up
		while row != column:
		  
		  node = row.left

		  while node != row:
		    node.column.size += 1
		    node.down.up = node
		    node.up.down = node
		    node = node.left

		  row = row.up

		column.right.left = column
		column.left.right = column