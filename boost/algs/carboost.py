# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
This module contains an implamentations of the
BoostCARs algorithm

References
----------
[1] Yoon, Y. and Lee, G. Gary. Text categorization
based on Boosting Association Rules.

[2] Yoon, Y. and Lee, G. Gary. Subcellular Localization
Prediction through Boosting Association Rules

'''

# Imports
import random
import math
import copy

# Local imports
from utils.settings import *
from utils.metrics import *
from core.ruleclassifier import RuleClassifier

# CAR Boosting algorithm
def carboost(itemsets, train, classes, cvth):
	# Safety
	if len(itemsets) == 0 or len(train) == 0:
		return []

	# Setting seed
	random.seed(RANDOM_SEED)
	
	# Boosting variables
	model = []
	conf = {}
	hypotheses = []

	# Sorted itemsets
	for it in itemsets:
		conf = Metrics.confidence(it, classes)
		for class_ in classes:
			hypotheses.append(RuleClassifier(it, class_, conf[class_]))
	
	hypotheses = sorted(hypotheses, key=lambda x: x.conf, reverse=True)

	# Train keys
	invproj = set(train.keys())

	# Covers
	covers = {inst: 0.0 for inst in invproj}

	# Boosting iterations
	for h in hypotheses:
		correct = False
		delete = []

		for inst in h.itemset.supp[h.class_]:
			if inst in invproj: # It means it still covers some
				if train[inst] == h.class_: # h_j predicts y_i
					correct = True
					covers[inst] += h.conf

					# Marking for deletion
					if covers[inst] > cvth:
						delete.append(inst)

		# Deleting
		for inst in delete:
			invproj.remove(inst)

		# Appending to the final model
		if correct:
			model.append((copy.copy(h), 1.0))

		# Making it a bit smarter
		if len(invproj) == 0:
			return model

	# Building model
	return model

# CAR Boosting algorithm
def carboost_exp(itemsets, train, cvth):
	# Safety
	if len(itemsets) == 0 or len(train) == 0:
		return []

	# Setting seed
	random.seed(RANDOM_SEED)
	
	classes = train.keys()
	classes.sort()
	
	# Boosting variables
	model = []
	invproj = {inst:class_ for class_ in classes for inst in train[class_]} 	# Inverted train
	weights = {inst: 1 for inst in invproj}

	# Shuffled itemsets
	itemsets_ = [r for r in itemsets]
	random.shuffle(itemsets_)

	# Boosting iterations
	for r in itemsets_:
		for class_ in classes:
			correct = False
			delete = []

			for inst in r.supp[class_]:
				if inst in invproj: # It means it still covers some
					if invproj[inst] == class_: # r_j predicts y_i
						correct = True
						weights[inst] *= math.exp(-r.conf[class_])

						# Marking for deletion
						if weights[inst] < cvth:
							delete.append(inst)

			# Deleting
			for inst in delete:
				invproj.pop(inst)

			# Appending to the final model
			if correct:
				model.append((r, class_, r.conf[class_], 0.0))

			# Making it a bit smarter
			if len(invproj) == 0:
				return model

	# Building model
	return model