#!/usr/bin/python

# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
Boosting - main module

'''

# Imports
import argparse

# Local imports
import utils.settings as settings
import utils.reader as reader
import utils.utils as utils
import utils.metrics as metrics

import algs.zero as zero
import algs.lac as lac
import algs.dboost as dboost
import algs.cboost as cboost
import algs.slipper as slipper

# Argument parsing method
def arg_parsing():
	# Argument Parsing
	parser = argparse.ArgumentParser(description="Boosting module")

	# Main arguments
	parser.add_argument("-s", nargs="*", help="Traininig set files", required=True)
	parser.add_argument("-t", nargs=1, help="Testing set file", required=True)
	parser.add_argument("-i", nargs=1, help="Itemsets file", required=True)
	parser.add_argument("-b", nargs=1, help="Maximum number of rounds")
	
	parser.add_argument("-o", nargs=1, help="Original sizes of each class")
	parser.add_argument("-j", nargs=1, help="Jaccard's indexes")
	parser.add_argument("-c", help="Internal Cross Validation", action="store_true")

	# Algorithms
	parser.add_argument("-Z", help="ZERO Classifier", action="store_true")
	parser.add_argument("-A", help="Associative Classifier", action="store_true")
	parser.add_argument("-D", help="Discrete Adaboost", action="store_true")
	parser.add_argument("-C", help="Confidence-rated Adaboost", action="store_true")
	parser.add_argument("-S", help="SLIPPER Classifier", action="store_true")
	
	# Other settings
	parser.add_argument("--free", help="Uses only free itemsets", action="store_true")
	parser.add_argument("--rmode", nargs=1, help="Reader mode")
	parser.add_argument("--seed", nargs=1, help="Random objects' seed")

	return parser.parse_args()

# MAIN
if __name__ == "__main__":
	# Arguments
	args = arg_parsing()
	
	# Reading train
	train, classes, sizes = reader.read_train(args.s)
	# Reading test
	test = reader.read_test(args.t[0])
	# Reading itemsets
	itemsets = reader.read_itemsets(
		args.i[0], train, classes, 
		(args.rmode[0] if args.rmode is not None else None), 
		args.free)
	
	# Reading original sizes
	if args.o is not None:
		print args.o
		sizes_ = reader.read_sizes(args.o[0])
		extra = {class_: sizes_[class_] - sizes[class_] for class_ in classes}
	else: extra = None

	# Reading Jaccard's indexes
	if args.j is not None: jaccard = reader.read_jaccard(args.j[0])
	else: jaccard = None

	# Settings
	if args.seed is not None: settings.RANDOM_SEED = int(args.seed)
	if args.b is not None: settings.MAX_ROUNDS = int(args.b[0])

	# Default class
	default_class = max(sizes, key=sizes.get)

	# Variables
	models = []
	black_icv = []
	classes = sorted(classes)

	# def SUM(model):
	# 	sum_ = 0
	# 	for h, a in model:
	# 		sum_ += len(h.itemset.patterns[0])

	# 	return sum_

	# def DIFF(model):
	# 	return len(set([h.itemset.id for h, a in model]))

	# LAC
	if args.A == True:
		lac_ = lac.lac(itemsets, classes)
		models.append((lac_, "lac", False, True))

		# print "@ Size-LAC", len(lac_), SUM(lac_)

	# SLIPPER
	if args.S == True:
		slipper_ = slipper.slipper(itemsets, train, classes, settings.MAX_ROUNDS) #, weights=jaccard, extra=extra)
		# print "@ empty-black:", sum([1 for h, alpha in slipper_ if h.itemset.isdefault()]),

		models.append((slipper_, "black", True, False))		

		# Complexity
		# old_max = max(itemsets, key=lambda x:x.size()[0]).size()[0]
		# old_min = min(itemsets, key=lambda x:x.size()[0]).size()[0]
		# old_range = old_max - old_min
		
		# new_max = 10
		# new_min = 1
		# new_range = new_max - new_min

		# norm = lambda x: new_min + (x-old_min)*(new_range)/(old_range)

		# print "@ Complexity",
		# for h, alpha in slipper_:
		# 	print h.itemset.size()[0], 

		# print ""

		# for i in xrange(new_min, new_max + 1):
		# 	slipper_ = slipper.slipper([it for it in itemsets if norm(it.size()[0]) <= i], train, classes, settings.MAX_ROUNDS)
		# 	models.append((slipper_, "simpler_leq_"+str(i), True, False))

		# SLIPPER JACCARD
		if args.j is not None:
			slipper_ = slipper.slipper(itemsets, train, classes, settings.MAX_ROUNDS, weights=jaccard.copy())
			models.append((slipper_, "black_jacc", True, False))

		# SLIPPER EXTRA
		if args.o is not None:
			slipper_ = slipper.slipper(itemsets, train, classes, settings.MAX_ROUNDS, extra=extra)
			# print "empty-extra:", sum([1 for h, alpha in slipper_ if h.itemset.isdefault()])
			models.append((slipper_, "black_extra", True, False))

		# SLIPPER JACCARD EXTRA
		if args.j is not None and args.o is not None:
			slipper_ = slipper.slipper(itemsets, train, classes, settings.MAX_ROUNDS, weights=jaccard.copy(), extra=extra)
			models.append((slipper_, "black_jacc_extra", True, False))

		# Internal cross-validation
		if args.c == True:
			acc = utils.internalcv(itemsets, train, classes, slipper.slipper, jaccard, extra)

			# print "@ ModelSize",
			for i in xrange(settings.MAX_ROUNDS):
				rounds = acc[:i+1].index(max(acc[:i+1]))
				slipper_chosen = slipper_[:rounds+1]

				black_icv.append(slipper_chosen)
				# print rounds+1,

			# print ""

		# print "@ Size-SLIPPER", len(slipper_), SUM(slipper_), DIFF(slipper_)

		# # Train error
		# t_error = [0]*settings.MAX_ROUNDS
		# for inst in train:
		# 	pred = utils.prediction(slipper_, inst, True, False)

		# 	for i in range(len(pred)):
		# 		p = (pred[i] if pred[i] is not None else default_class)
				
		# 		if p == train[inst]:
		# 			t_error[i] += 1

		# print "@ TrainError-Slipper",
		# for i in t_error:
		# 	print 1.0-(float(i)/len(train)),
		# print ""

		# exit()

	if args.D == True:
		# DISCRETE BOOSTING: ALPHA
		dboost_ = dboost.dboost(itemsets, train, classes, settings.MAX_ROUNDS)
		models.append((dboost_, "dboost", True, False))

		# DISCRETE BOOSTING: CONFIDENCE
		aux = []
		for h, alpha in dboost_:
			h.conf = metrics.confidence(h.itemset, classes)[h.pred]
			aux.append((h, h.conf))
		models.append((aux, "dboost-conf", True, False))

		# DISCRETE BOOSTING: CONFIDENCE * ALPHA
		aux = []
		for h, alpha in dboost_:
			aux.append((h, h.conf*alpha))
		models.append((aux, "dboost-conf-alpha", True, False))

		# Train error
		# t_error = [0]*settings.MAX_ROUNDS
		# for inst in train:
		# 	pred = utils.prediction(dboost_, inst, True, False)

		# 	for i in range(len(pred)):
		# 		p = (pred[i] if pred[i] is not None else default_class)
				
		# 		if p == train[inst]:
		# 			t_error[i] += 1

		# print "@ TrainError-Dboost",
		# for i in t_error:
		# 	print 1.0-(float(i)/len(train)),
		# print ""

	# CONFIDENCE-RATED BOOSTING
	if args.C == True:
		cboost_ = cboost.cboost(itemsets, train, classes, settings.MAX_ROUNDS)
		models.append((cboost_, "cboost", True, False))

	# ZERO
	if args.Z == True:
		models.append((zero.zero(), "zero", False, False))

	# Predictions
	# <inst_class> <~alg_1> <pred_1> ... <pred_n> <~alg_2> <pred_1> <pred_1>
	for inst in test:
		print inst.class_, 

		for model, name, ppr, average in models:
			print "~" + name,
			pred = utils.prediction(model, inst, ppr, average)

			for p in pred:
				if p == None: p = default_class
				print p,

		if len(black_icv) > 0:
			print "~Tmax",
			for model in black_icv:
				pred = utils.prediction(model, inst, False, False)

				for p in pred:
					if p == None: p = default_class
					print p,

		print ""