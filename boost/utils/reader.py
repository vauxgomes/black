# -*- coding: utf-8 -*-

# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

from core.itemset import Itemset
from core.instance import Instance

# Read training files (One per class)
def read_train(files):
	train = {}
	sizes = {}
	classes = []
	
	for file in files:
		with open(file, 'r') as handler:
			# Class name selected from file name
			class_ = int(file[file.rfind(".") + 1:])
			classes.append(class_)
			sizes[class_] = 0

			for inst in handler:
				# FOR MULTIDUPEHACK FORMAT
				if inst.find(" ") != -1:
					inst = inst[inst.find(" ") + 1:].strip()

				train[inst.strip()] = class_
				sizes[class_] += 1

	return train, classes, sizes

# Read test file LUCSKDD format
def read_test(file):
	instances = []

	with open(file, 'r') as handler:
		for inst in handler:
			ft = [int(i) for i in inst.split()]
			instances.append(Instance(len(instances), set(ft[:-1]), ft[-1]))

	return instances


# Read itemsets
def read_itemsets(file, train, classes, mode=None, free=False):
	last = "@vauxgomes"
	has_default = False
	itemsets = []

	# Multidupehack or D-peeler
	if mode is None: 
		with open(file, "r") as handler:
			for row in handler:
				# s,s,s f,f,f,f,f
				row = row.strip().split()
				support = row[0] # s,s,s
				features = row[1].split(",") # f,f,f

				# Warning: assuming the supports are printed in order
				if support == last and not itemsets[-1].default:
					if features[0] == '\xc3\xb8': # ø
						itemsets[-1].append(set([i for i in features]), free)
					else:
						itemsets[-1].append(set([int(i) for i in features]), free)
					continue

				#
				last = support
				length = 0
				supp = {class_:set() for class_ in classes}

				#
				for inst in row[0].split(","): # s,s,s
					supp[train[inst]].add(inst)
					length += 1

				if features[0] == '\xc3\xb8': # ø
					itemsets.append(Itemset(len(itemsets), set([i for i in features]), supp, default=True))
				else:
					itemsets.append(Itemset(len(itemsets), set([int(i) for i in features]), supp, default=(length == len(train))))

				#
				if itemsets[-1].isdefault(): has_default = True
			
	# LCM
	elif mode == "lcm":
		# It needs to be mapped
		map_ = [int(i) for i in train.keys()]
		map_.sort()
		map_ = [str(i) for i in map_] # it's preferable working w/ strings

		# One itemset every two lines
		itemset = None

		# f f f f <new line> s s s s s s
		with open(file, "r") as handler:
			for row in handler:
				if itemset is None:
					features = row.strip().split() # f f f f

					if features == "":
						itemset = set([]) # Itemset features
					else:
						itemset = set([int(i) for i in features]) # Itemset features
				else:
					row = row.strip().split()
					supp = {class_:set() for class_ in classes}
					
					for inst in row: # s s s s s
						inst = map_[int(inst)]
 						supp[train[inst]].add(inst)

 					length = sum(len(supp[class_]) for class_ in classes)
					itemsets.append(Itemset(len(itemsets), itemset, supp, default=(len(itemset) == 0 or length == len(train))))					
					itemset = None # So it will read an itemset's row next time

					#
					if itemsets[-1].isdefault(): has_default = True

	# Forcing a default itemset
	if not has_default:
		supp = {class_:set() for class_ in classes}
		for inst in train: supp[train[inst]].add(inst)

		itemsets.append(Itemset(-1, None, supp, default=True))
	
	# print "@ itemsets", len(itemsets)
	return itemsets

# Read sizes
def read_sizes(file):
	sizes = {}
	with open(file, "r") as handler:
		for row in handler:
			# Class size
			row = row.strip().split()
			sizes[int(row[0])] = int(row[1])

	return sizes

# Read Jaccard's indexes
def read_jaccard(file):
	jaccard = {}

	# ID Index
	with open(file, "r") as handler:
		for row in handler:
			row = row.strip().split()
			jaccard[row[0]] = float(row[1])

	return jaccard