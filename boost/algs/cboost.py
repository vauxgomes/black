# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
This module contains an implamentations of the
confidence-rated boosting algorithms for binary
classification problems.

References
----------
[1] Robert E. Schapire and Yoram Singer. Improved 
boosting algorithms using confidence-rated predictions.

'''

# Imports
import random
import math
import copy

# Local imports
from utils.settings import *
from core.itemset import Itemset
from core.partitionclassifier import PartitionClassifier

# Confidence-rated boosting algorithm
def cboost(itemsets, train, classes, rounds):
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
	default = PartitionClassifier(Itemset(-1, set(), {}, default=True))

	# First weights
	normalizer = float(len(train))
	for inst in train:
		weights[inst] = 1 / normalizer
		wsum[train[inst]] += weights[inst]

	# Boosting iterations
	for t in range(rounds):
		Z = 0.0
		chosen = []

		# Find the itemset that minimizes Z (by maximizing z)
		for itemset in itemsets:
			# Supports
			inweights = {}
			outweights = {}

			for class_ in classes:
				inweights[class_] = sum([weights[i] for i in itemset.supp[class_]])
				outweights[class_] = wsum[class_] - inweights[class_]

				# Safety: Sometimes this subtraction's results is negative
				if outweights[class_] < 0: outweights[class_] = 0
			
			# The weightest class within support
			pred = max(inweights, key=inweights.get)			
			aux = sum(inweights.values())

			if aux == 0: conf = 0 # Safety
			else: conf = ((inweights[pred] / aux) - 0.5) / 0.5

			# The weightest class outside support
			pred_ = max(outweights, key=outweights.get)
			aux = sum(outweights.values())

			if aux == 0: conf_ = 0 # Safety
			else: conf_ = ((outweights[pred_] / aux) - 0.5) / 0.5

			z = (2 * inweights[pred] - sum(inweights.values())) * conf + \
				(2 * outweights[pred_] - sum(outweights.values())) * conf_

			# Maximizing z
			if len(chosen) == 0 or z >= Z:
				if z > Z: Z = z; del chosen[:] # Two commands here ;)
				chosen.append((itemset, pred, conf, pred_, conf_, z))

		# No good rule was chosen
		if len(chosen) == 0:
			if len(model) == 0: # And model is empty
				model.append((default, 1.0))

			return model

		# Randomly choose the best itemset
		itemset, pred, conf, pred_, conf_, z = chosen[random.randint(0, len(chosen) - 1)]
		h = PartitionClassifier(itemset, pred, conf, pred_, conf_)

		# Calculating alpha
		alpha = math.log((1 + z) / (1 - z)) / 2

		# Updating train weights using h_t
		for inst in train:
			pred, conf = h.classify(inst)

			if pred == train[inst]:
				weights[inst] *= math.exp(-conf*alpha)
			else:
				# Missclassified
				weights[inst] *= math.exp(conf*alpha)

		# Normalization
		normalizer = sum(weights.values())
		for class_ in classes: wsum[class_] = 0

		for inst in train:
			weights[inst] /= normalizer
			wsum[train[inst]] += weights[inst]

		# Adding classifier to the final model
		model.append((copy.copy(h), alpha))

	return model

# Confidence-rated boosting algorithm
def cboost2(itemsets, train, classes, rounds):
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
	default = PartitionClassifier(Itemset(-1, set(), {}, default=True))

	# First weights
	normalizer = float(len(train))
	for inst in train:
		weights[inst] = 1 / normalizer
		wsum[train[inst]] += weights[inst]

	# Boosting iterations
	for t in range(rounds):
		Z = 0.0
		chosen = []

		# Find the itemset that minimizes Z (by maximizing z)
		for itemset in itemsets:
			# Supports
			inweights = {}
			outweights = {}

			for class_ in classes:
				inweights[class_] = sum([weights[i] for i in itemset.supp[class_]])
				outweights[class_] = wsum[class_] - inweights[class_]

				# Safety: Sometimes this subtraction's results is negative
				if outweights[class_] < 0: outweights[class_] = 0
			
			# The weightest class within support
			pred = max(inweights, key=inweights.get)			
			aux = sum(inweights.values())

			if aux == 0: conf = 0 # Safety
			else: conf = inweights[pred] / aux#((inweights[pred] / aux) - 0.5) / 0.5

			# The weightest class outside support
			pred_ = max(outweights, key=outweights.get)
			aux = sum(outweights.values())

			if aux == 0: conf_ = 0 # Safety
			else: conf_ = outweights[pred_] / aux#((outweights[pred_] / aux) - 0.5) / 0.5

			z = (2 * inweights[pred] - sum(inweights.values())) * conf + \
				(2 * outweights[pred_] - sum(outweights.values())) * conf_

			# Maximizing z
			if z >= Z:
				if z > Z:
					Z = z
					del chosen[:] 

				chosen.append((itemset, pred, conf, pred_, conf_, z))

		# No good rule was chosen
		if len(chosen) == 0:
			if len(model) == 0: # And model is empty
				model.append((default, 1.0))

			return model

		# Randomly choose the best itemset
		itemset, pred, conf, pred_, conf_, z = chosen[random.randint(0, len(chosen) - 1)]
		h = PartitionClassifier(itemset, pred, conf, pred_, conf_)

		# Calculating alpha
		alpha = math.log((1 + z) / (1 - z)) / 2

		# Updating train weights using h_t
		for inst in train:
			pred, conf = h.classify(inst)

			if pred == train[inst]:
				weights[inst] *= math.exp(-conf*alpha)
			else:
				# Missclassified
				weights[inst] *= math.exp(conf*alpha)

		# Normalization
		normalizer = sum(weights.values())
		for class_ in classes: wsum[class_] = 0

		for inst in train:
			weights[inst] /= normalizer
			wsum[train[inst]] += weights[inst]

		# Adding classifier to the final model
		model.append((copy.copy(h), alpha))

	return model

# Confidence-rated boosting algorithm
def cboost3(itemsets, train, classes, rounds):
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
	default = PartitionClassifier(Itemset(-1, set(), {}, default=True))


	#
	sizes = {class_:0 for class_ in classes}
	for i in train: sizes[train[i]] += 1

	predictions = {}
	for itemset in itemsets:
		insizes = {}
		outsizes = {}

		for class_ in classes:
			insizes[class_] = len(itemset.supp[class_])
			outsizes[class_] = sizes[class_] - insizes[class_]
		
		pred = max(insizes, key=insizes.get)
		aux = sum(insizes.values())
		
		if aux == 0: conf = 0
		else: conf = float(insizes[pred]) / float(aux)

		pred_ = max(outsizes, key=outsizes.get)
		aux = sum(outsizes.values())

		if aux == 0: conf_ = 0
		else: conf_ = float(outsizes[pred]) / float(float(aux))

		predictions[itemset] = [pred, conf, pred_, conf_]

	# First weights
	normalizer = float(len(train))
	for inst in train:
		weights[inst] = 1 / normalizer
		wsum[train[inst]] += weights[inst]

	# Boosting iterations
	for t in range(rounds):
		Z = 0.0
		chosen = []

		# Find the itemset that minimizes Z (by maximizing z)
		for itemset in itemsets:
			# Supports
			inweights = {}
			outweights = {}

			for class_ in classes:
				inweights[class_] = sum([weights[i] for i in itemset.supp[class_]])
				outweights[class_] = wsum[class_] - inweights[class_]

				# Safety: Sometimes this subtraction's results is negative
				if outweights[class_] < 0: outweights[class_] = 0
			
			# The weightest class within support
			pred = predictions[itemset][0]
			conf = predictions[itemset][1]

			# The weightest class outside support
			pred_ = predictions[itemset][2]
			conf_ = predictions[itemset][3]

			z = (2 * inweights[pred] - sum(inweights.values())) * conf + \
				(2 * outweights[pred_] - sum(outweights.values())) * conf_

			# Maximizing z
			if len(chosen) == 0 or z >= Z:
				if z > Z: Z = z; del chosen[:] # Two commands here ;)
				chosen.append((itemset, pred, conf, pred_, conf_, z))

		# No good rule was chosen
		if len(chosen) == 0:
			if len(model) == 0: # And model is empty
				model.append((default, 1.0))

			return model

		# Randomly choose the best itemset
		itemset, pred, conf, pred_, conf_, z = chosen[random.randint(0, len(chosen) - 1)]
		h = PartitionClassifier(itemset, pred, conf, pred_, conf_)

		# Calculating alpha
		alpha = math.log((1 + z) / (1 - z)) / 2

		# Updating train weights using h_t
		for inst in train:
			pred, conf = h.classify(inst)

			if pred == train[inst]:
				weights[inst] *= math.exp(-conf*alpha)
			else:
				# Missclassified
				weights[inst] *= math.exp(conf*alpha)

		# Normalization
		normalizer = sum(weights.values())
		for class_ in classes: wsum[class_] = 0

		for inst in train:
			weights[inst] /= normalizer
			wsum[train[inst]] += weights[inst]

		# Adding classifier to the final model
		model.append((copy.copy(h), alpha))

	return model