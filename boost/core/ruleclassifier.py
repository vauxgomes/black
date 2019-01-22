# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

from instance import Instance
from abstractclassifier import AbstractClassifier

''' Rule Classifier '''

class RuleClassifier(AbstractClassifier):

	#
	def __init__(self, itemset, pred = None, conf = 0.0):
		super(RuleClassifier, self).__init__(itemset, pred, conf)

	#
	def classify(self, X):
		# If itemset is the default one
		if self.itemset.isdefault():
			return (self.pred, self.conf)

		# If rule covers instance
		if isinstance(X, Instance):
			if self.itemset.issubset(X.features):
				return (self.pred, self.conf)

		# If instance key is within support
		else:
			for i in self.itemset.supp.keys():
				if X in self.itemset.supp[i]:
					return (self.pred, self.conf)

		return (None, 0)