# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
This module contains an implamentations of the
SLIPPER algorithm with two output confidences for
binary classification problems.

References
----------
[1] Cohen, William W., and Yoram Singer. A simple,
fast, and effective rule learner

'''

# Imports
import random
import math
import copy

# Local imports
from utils.settings import *
from core.itemset import Itemset
from core.ruleclassifier import RuleClassifier

# SLIPPER: Multiclass
def slipper(itemsets, train, classes, rounds, weights=None, extra=None):
	# Safety
	if len(itemsets) == 0 or len(train) == 0:
		return []
	elif len(classes) == 1:
		return [(RuleClassifier(Itemset(-1, None, None, default=True), classes[0], 1.0),1.0)]
	elif len(classes) == 0:
		return [(RuleClassifier(Itemset(-1, None, None, default=True), None, 1.0),1.0)]

	# Setting seed
	random.seed(RANDOM_SEED)

	# Variables
	model = []
	smooth = 1.0 / (2.0 * len(train))
	normalizer = 1.0/len(train)

	# Initializing weights
	if weights is None: weights = {i: normalizer for i in train}

	# Extra weight
	if extra is None: extra = {class_: 0 for class_ in classes}
	eweights = {class_: 1.0 for class_ in classes}
	
	# Boosting iterations
	for t in xrange(rounds):
		G = 0
		chosen = []

		# Normalization
		normalizer = sum(weights.values()) \
			+ sum([eweights[class_] * extra[class_] for class_ in classes])

		# if t == 0:
		# 	print "@ train-error",
		# 	Z = normalizer
		# else:
		# 	Z *= normalizer

		# print Z,

		# Safety
		if normalizer == 0: break

		for i in train: weights[i] /= normalizer
		for class_ in classes: eweights[class_] /= normalizer

		# Find the itemset that minimizes V
		for itemset in itemsets:
			# Support weights
			if itemset.isdefault() and extra is not None:
				cover_weights = {class_: 0.0 for class_ in classes}

				for inst in train: cover_weights[train[inst]] += weights[inst]
				for class_ in classes: cover_weights[class_] += eweights[class_] * extra[class_]
			else:
				cover_weights = {class_:max(0, sum([weights[i] for i in itemset.supp[class_]])) for class_ in classes}

			#
			pos, neg = sorted(cover_weights, key=cover_weights.get, reverse=True)[:2]
			g = math.sqrt(cover_weights[pos]) - math.sqrt(cover_weights[neg])

			# Maximizing G
			if g >= G:
				if g > G:
					G = g
					del chosen[:]
				
				chosen.append((itemset, pos, cover_weights[pos], neg, cover_weights[neg]))

		# No good rule was chosen
		if len(chosen) == 0: break

		# Randomly chose the best itemset
		itemset, pos, wpos, neg, wneg = random.sample(chosen, 1)[0]
		conf = math.log((wpos + smooth) / (wneg + smooth)) / 2.0

		# Building classifier
		h = RuleClassifier(itemset, (neg if conf < 0 else pos if conf > 0 else None), abs(conf))

		# Updating weights: Default classifier
		if h.itemset.isdefault():
			pred, conf = h.pred, h.conf
			right, wrong = math.exp(-conf), math.exp(conf)

			# Updating train weights
			for i in train:
				if pred == train[i]: weights[i] *= right
				else: weights[i] *= wrong # Missclassified

			# Updating extra weights			
			for class_ in classes:
				if pred == class_: eweights[class_] *= right
				else: eweights[class_] *= wrong # Missclassified
		else:
			# Updating weights: Non-default classifier
			pred, conf = h.pred, h.conf
			right, wrong = math.exp(-conf), math.exp(conf)

			# Updating train weights
			for class_ in classes:
				aux = (right if class_ == pred else wrong)
				for i in h.itemset.supp[class_]:
					weights[i] *= aux

		# Adding classifier to the final model
		model.append((h, 1.0))
		cover_weights.clear()

	# Freeing memory
	weights.clear()
	# print ""

	return model