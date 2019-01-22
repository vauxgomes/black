# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

import math

from instance import Instance
from abstractclassifier import AbstractClassifier

''' Partition Classifier '''

class PartitionClassifier(AbstractClassifier):

	#
	def __init__(self, itemset, pred = None, conf = 0.0, pred_ = None, conf_ = 0.0):
		super(PartitionClassifier, self).__init__(itemset, pred, conf)
		self.pred_ = pred_
		self.conf_ = conf_

	#
	def classify(self, X):
		# If itemset is the default one
		if self.itemset.default:
			return (self.pred, self.conf)

		# If rule covers instance
		if isinstance(X, Instance):
			if self.itemset.issubset(X.features):
				return (self.pred, self.conf)

		# If instance key is within support
		else:
			for i in self.itemset.supp.keys():
				# If inside support
				if X in self.itemset.supp[i]:
					return (self.pred, self.conf)		

		# If not covered or outside support
		return (self.pred_, self.conf_)