# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
This module contains an implamentations of the
discrete boosting algorithms.

References
----------
[1] Robert E. Schapire. The strength of weak
learnability.

'''

# Imports
import random
import math

# Local imports
from utils.settings import *
from core.itemset import Itemset
from core.ruleclassifier import RuleClassifier
import utils.metrics as metrics

# Discrete Boosting algorithm
def dboost(itemsets, train, classes, rounds):
	# Safety
	if len(itemsets) == 0 or len(train) == 0:
		return []

	# Setting seed
	random.seed(RANDOM_SEED)

	# Variables
	model = []
	weights = {}
	wsum = {class_: 0 for class_ in classes} # Distribution sum per class

	#
	default = RuleClassifier(Itemset(-1, set(), {}, default=True))

	# First weights
	normalizer = float(len(train))
	for i in train:
		weights[i] = 1 / normalizer
		wsum[train[i]] += weights[i]

	# Boosting iterations
	for t in range(rounds):
		chosen = []
		minerror = 1.0001

		# Find the itemset that minimizes minerror
		for itemset in itemsets:
			# Support weights
			wsupp_0 = sum([weights[i] for i in itemset.supp[classes[0]]])
			wsupp_1 = sum([weights[i] for i in itemset.supp[classes[1]]])
			
			# Projection error
			error = {}
			error[classes[0]] = wsum[classes[0]] - wsupp_0 + wsupp_1
			error[classes[1]] = wsum[classes[1]] - wsupp_1 + wsupp_0

			# Best twin rule
			class_ = min(error, key=error.get)
			error = error[class_]

			if error <= 0:
				minerror = 0
				break

			# Minimizing minerror
			if minerror >= error:
				if minerror > error:
					minerror = error
					del chosen[:]

				chosen.append((itemset, class_))

		# No good itemset was chosen
		if minerror >= (0.5 - GAMMA) or minerror == 0:
			if len(model) == 0:
				model.append((default, 1.0))

			return model

		# Randomly chose the best itemset
		itemset, pred = random.sample(chosen, 1)[0]
		h = RuleClassifier(itemset, pred, 1.0)

		# Calculating alpha
		alpha = math.log((1.0 - minerror) / minerror) / 2

		# Updating train weights
		aux_corr = math.exp(-alpha)
		aux_err = math.exp(alpha)
		normalizer = 0.0

		for i in train:
			pred, conf = h.classify(i)

			# Outside support
			if pred == None:
				# Same class: Misclassified
				if h.pred == train[i]: weights[i] *= aux_err
				# Diff class
				else: weights[i] *= aux_corr

			# Inside support
			else:
				# Same class
				if h.pred == train[i]: weights[i] *= aux_corr
				# Diff class: Misclassified
				else: weights[i] *= aux_err

			normalizer += weights[i]


		# Normalization
		wsum = {class_: 0 for class_ in classes}

		for i in train:
			weights[i] /= normalizer
			wsum[train[i]] += weights[i]

		# Adding classifier to the final model
		model.append((h, alpha))

	return model