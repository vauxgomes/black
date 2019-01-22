# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

# Imports
import random

# Local imports
import settings

# Prediction function "model(x)"
def prediction(model, test, print_per_round=False, average=False):
	# Just for safety
	if len(model) == 0: return [None]

	# Variables
	score = {}
	count = {}
	pred = []

	# Each rule in model: (h, alpha)
	for h, alpha in model:
		class_, conf = h.classify(test)

		if class_ is not None:
			score[class_] = score.get(class_, 0.0) + conf * alpha
			count[class_] = count.get(class_, 0.0) + 1.0

		if len(score) == 0:
			pred.append(None)
		elif average:
			avgscr = {class_: score[class_] / count[class_] for class_ in count.keys()}
			pred.append(max(avgscr, key=avgscr.get))
		else:
			pred.append(max(score, key=score.get))

	# Mostly LAC/EAC's case
	if not print_per_round: return [pred[-1]]

	# Avoiding extra work when reading results
	last = pred[-1]
	while len(pred) < settings.MAX_ROUNDS:
		pred.append(last)

	return pred

# Internal cross-validation
def internalcv(itemsets, train, classes, alg, weights=None, extra=None):
	# Safety
	if len(train) < settings.kICV: return [0]*settings.MAX_ROUNDS

	keys = train.keys()
	acc = [0]*settings.MAX_ROUNDS
	
	# Weights
	if weights is None: weights = {i: 1.0 for i in train}

	# Weights sum per class
	wsum = {class_: 0.0 for class_ in classes}
	for i in train: wsum[train[i]] += weights[i]

	for fold in stratified_wkfolds(train, classes, settings.kICV, weights):
		weights_ = weights.copy()
		wsum_ = {class_: wsum[class_] for class_ in classes}

		#
		for i in fold:
			wsum_[train[i]] -= weights_[i]
			weights_[i] = 0.0

		# Defining default class
		default_class = max(wsum_, key=wsum_.get)

		#
		alg_ = alg(itemsets, train, classes, settings.MAX_ROUNDS, weights_, extra)

		# Safety
		if len(alg_) > 0:
			while len(alg_) < settings.MAX_ROUNDS: alg_.append(alg_[-1])
		
		#
		for inst in fold:
			pred = prediction(alg_, inst, True, False)

			for j in xrange(len(pred)):
				if pred[j] == train[inst]:
					acc[j] += weights[inst]
				elif pred[j] is None and train[inst] == default_class:
					acc[j] += weights[inst]
					
		# Freeing some memory
		del alg_

	return acc

# Stratified weighted k-fold splitter
def stratified_wkfolds(train, classes, K, weights=None):
	# Setting seed
	random.seed(settings.RANDOM_SEED)
	
	# Shuffled keys
	keys = train.keys()
	random.shuffle(keys)

	# Safety
	if weights is None: weights = {i: 1.0 for i in train}

	# Variables
	folds = []
	
	props = {class_: 0.0 for class_ in classes}
	accs = {class_: 0.0 for class_ in classes}
	dists =  {class_: [] for class_ in classes}

	#
	k = float(K)

	for i in keys:
		props[train[i]] += weights[i] / k
		dists[train[i]].append(i)

	# Selecting instances of each fold
	for i in xrange(K):
		fold = []
		
		for class_ in classes:
			#
			current = accs[class_]
			expected = abs((i+1.0) * props[class_])

			rm = []
			dist = dists[class_]

			# Looking for any instance that can fit in the budget
			for j in xrange(len(dist)):
				aux = abs(current + weights[dist[j]])
				if aux - 0.0000001 <= expected: # Small gambiarra here
					current = aux
					fold.append(dist[j])
					rm.insert(0, j) # Inserting at the begining (so it is already reversed)

				# Avoinding extra work
				if current + 0.0000001 >= expected: break  # Small gambiarra here

			# Removing used instances
			for j in rm: del dist[j]

			# Updating acc
			accs[class_] = current

		# Appending fold
		folds.append(fold)

	return folds

# Controlled test for the fold splitter
# train = {1: 1, 3: 1, 5: 1, 7: 1, 9: 1, 11: 1, 13: 1, 15: 1, 17: 1, 19: 1, 21: 1, 23: 1, 25: 1, 27: 1, 29: 1, 31: 1, 33: 1, 35: 1, 37: 1, 39: 1, 41: 1, 43: 1, 45: 1, 47: 1, 49: 1, 0: 2, 2: 2, 4: 2, 6: 2, 8: 2, 10: 2, 12: 2, 14: 2, 16: 2, 18: 2}
# weights = {1: 0.6952089975, 3: 0.6700168903, 5: 0.1570005122, 7: 0.9832340259, 9: 0.3398338076, 11: 0.101418256, 13: 0.2614206015, 15: 0.7308608374, 17: 0.4747500886, 19: 0.3217569021, 21: 0.0096049616, 23: 0.9160294058, 25: 0.7153801899, 27: 0.7302972661, 29: 0.4125310539, 31: 0.7534956977, 33: 0.0096449887, 35: 0.4250019739, 37: 0.8217518391, 39: 0.3111709734, 41: 0.9590670266, 43: 0.6602219435, 45: 0.7619484517, 47: 0.9631219212, 49: 0.0483051012, 0: 0.6824548769, 2: 0.6519680893, 4: 0.8557142186, 6: 0.2744432122, 8: 0.5117333755, 10: 0.2990656226, 12: 0.8215778559, 14: 0.4344309848, 16: 0.5797528171, 18: 0.9217532245}
# classes = [1, 2]

# print weighted_stratified_kfolds(train, classes, 5, weights)