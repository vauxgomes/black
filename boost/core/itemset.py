# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

''' Class Itemset '''

# Itemset class to keep it organized
class Itemset(object):

	#
	def __init__ (self, id, pattern, supp, default=False):
		self.id = id
		self.patterns = [pattern]
		self.supp = supp
		self.default = default # Default itemset

	#
	def append(self, pattern, free=False):
		# Append if it is a free itemset
		if free:
			rm = []			
			for p in self.patterns:
				if pattern.issubset(p):
					rm.append(p)
			#
			if len(rm) != 0:
				for p in rm:
					self.patterns.remove(p)

		self.patterns.append(pattern)

	# For either commom itemset or meta-itemset (pattern[0] || pattern[1])
	def issubset(self, X):
		for p in self.patterns:
			if p.issubset(X): return True

		return False

 	#
	def isdefault(self):
		return self.default

	#
	def size(self):
		return [len(p) for p in self.patterns]

	#
	def __str__(self):
		return "r" + str(self.id) + \
		" {" + str(self.patterns) + "}" + \
		str([len(self.supp[class_]) for class_ in self.supp])