# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

from abc import ABCMeta, abstractmethod

''' Class Abstract Classifier '''

class AbstractClassifier(object):
	__metaclass__ = ABCMeta

	#
	def __init__(self, itemset, pred = None, conf = 0.0):
		self.itemset = itemset
		self.conf = conf
		self.pred = pred

	#
	@abstractmethod
	def classify(self, X):
		pass
