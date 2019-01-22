#!/usr/bin/python

# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com

import os
import argparse
import numpy
from sklearn.cross_validation import StratifiedKFold

def arg_parsing():
	# Argument Parsing
	parser = argparse.ArgumentParser(description="Cross Validation Fold Maker")
	parser.add_argument("-f", nargs="*", help="File", required=True)
	parser.add_argument("-k", nargs=1, help="Number of Folds", required=True)
	
	return parser.parse_args()

def fold(file, k):
	if not os.path.isfile(file):
		return

	index = file.rfind("/")
	if index != -1:
	    directory = file[:file.rfind("/")] + "/"
	else:
		directory = ""


	file = file[file.rfind("/") + 1:]
	output_folder = directory + file + ".CV/"
	
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	print file

	X = []
	Y = []

	handler = open(directory + file, "r")
	for row in handler:
		row = row.strip()
		index = row.rfind(" ")

		X.append(row[:index].split()) # features
		Y.append(row[index + 1:]) # class

	handler.close()

	X = numpy.array(X)
	Y = numpy.array(Y)

	fold = 0
	skf = StratifiedKFold(Y, k, shuffle=True, random_state=2)
	
	for train_index, test_index in skf:
		fold += 1

		f = output_folder + file + ".train-" + str(fold)
		print f
		
		handler = open(f, "w")
		for i in train_index:
			handler.write(" ".join(X[i]) + " " + Y[i] + "\n")
		handler.close()

		f = output_folder + file + ".test-" + str(fold)
		print f

		handler = open(f, "w")
		for i in test_index:
			handler.write(" ".join(X[i]) + " " + Y[i] + "\n")
		handler.close()

	return directory

if __name__ == "__main__":
	args = arg_parsing()
	k = int(args.k[0])

	for file in args.f:
		fold(file, k)
